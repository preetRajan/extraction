import instructor
from groq import Groq
from schema_engine import build_dynamic_schema
from auth import vault
import streamlit as st
import time

AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "qwen-2.5-32b",
    "mixtral-8x7b-32768"
]

def chunk_text(text: str, max_words: int = 1500) -> list[str]:
    """Splits text into smaller chunks to avoid TPM limits."""
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def _extract_from_chunk(chunk: str, DynamicModel, model_name: str):
    api_key = vault.get_next_key()
    if not api_key:
        st.error("No valid Groq API keys available or all keys are rate-limited.")
        return None

    client = instructor.from_groq(Groq(api_key=api_key))
    
    prompt = f"""
    You are a rigid data normalization layer designed for clinical auditing.
    For every requested parameter in the schema, locate the exact metric from the provided text and assign it to 'value'.
    You must also populate 'verbatim_quote' with the precise sequence of 5-12 words from the source text where that metric resides.
    Do not paraphrase, reword, or fix typos in the quote. If a value is not found, leave it as null/None.
    
    Source Text:
    {chunk}
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_name,
                response_model=DynamicModel,
                messages=[
                    {"role": "system", "content": "You are a highly accurate clinical data extraction system."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            return response
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "rate limit" in error_msg or "too large" in error_msg:
                st.warning(f"Rate limit or token size hit on current key. Blacklisting and rotating...")
                vault.blacklist_key(api_key, duration_seconds=60)
                api_key = vault.get_next_key()
                if not api_key:
                    st.warning("All keys are currently rate-limited. Waiting 20 seconds before retry...")
                    time.sleep(20)
                    api_key = vault.get_next_key()
                    if not api_key:
                        return None
                client = instructor.from_groq(Groq(api_key=api_key))
            else:
                st.error(f"Extraction error: {str(e)}")
                return None
    return None

def extract_data(text: str, template_name: str, schema_dict: dict, model_name: str):
    """
    Executes the LLM extraction using Instructor with Pydantic forced schemas.
    Chunks the text to avoid TPM limits and merges the results.
    """
    DynamicModel = build_dynamic_schema(template_name, schema_dict)
    
    chunks = chunk_text(text, max_words=1200) # ~1600 tokens per chunk
    merged_data = {}
    
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    for i, chunk in enumerate(chunks):
        progress_text.text(f"Processing chunk {i+1} of {len(chunks)}...")
        
        result = _extract_from_chunk(chunk, DynamicModel, model_name)
        if result:
            # Merge logic: if we found a non-null value, keep it.
            for field_name, wrapper_obj in result.model_dump().items():
                if wrapper_obj and wrapper_obj.get("value") not in [None, "", "null"]:
                    # Only overwrite if we haven't found a valid value for this field yet
                    if field_name not in merged_data:
                        merged_data[field_name] = wrapper_obj
        
        progress_bar.progress((i + 1) / len(chunks))
        
        # Slight delay to prevent immediate TPM spikes if using the same key
        time.sleep(1)
        
    progress_text.empty()
    progress_bar.empty()
    
    if not merged_data:
        st.warning("No data extracted from any chunk.")
        return None
        
    # Reconstruct final Pydantic model filling missing fields with None
    final_dict = {}
    for field_name in DynamicModel.model_fields.keys():
        final_dict[field_name] = merged_data.get(field_name, None)
        
    return DynamicModel(**final_dict)
