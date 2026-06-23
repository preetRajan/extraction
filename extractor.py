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

def extract_data(text: str, template_name: str, schema_dict: dict, model_name: str):
    """
    Executes the LLM extraction using Instructor with Pydantic forced schemas.
    Handles rate limit 429s by blacklisting and rotating the key.
    """
    api_key = vault.get_next_key()
    if not api_key:
        st.error("No valid Groq API keys available or all keys are rate-limited.")
        return None

    client = instructor.from_groq(Groq(api_key=api_key))
    
    # Build Pydantic model
    DynamicModel = build_dynamic_schema(template_name, schema_dict)

    prompt = f"""
    You are a rigid data normalization layer designed for clinical auditing.
    For every requested parameter in the schema, locate the exact metric from the provided text and assign it to 'value'.
    You must also populate 'verbatim_quote' with the precise sequence of 5-12 words from the source text where that metric resides.
    Do not paraphrase, reword, or fix typos in the quote. If a value is not found, leave it as null/None.
    
    Source Text:
    {text}
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
            if "429" in error_msg or "rate limit" in error_msg:
                st.warning(f"Rate limit hit on current key. Blacklisting and rotating...")
                vault.blacklist_key(api_key, duration_seconds=60)
                api_key = vault.get_next_key()
                if not api_key:
                    st.error("All keys are currently rate-limited. Please wait 60 seconds.")
                    return None
                client = instructor.from_groq(Groq(api_key=api_key))
            else:
                st.error(f"Extraction error: {str(e)}")
                return None

    st.error("Extraction failed after multiple rate-limit attempts.")
    return None
