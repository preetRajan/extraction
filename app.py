import streamlit as st
import base64
import pandas as pd
import fitz  # Added for image rendering
from auth import vault
from schema_engine import get_template_names, get_template_schema
from pdf_processor import extract_text_from_pdf, annotate_pdf
from extractor import extract_data, AVAILABLE_MODELS
from export import generate_excel_bytes

st.set_page_config(page_title="Universal Spatial SLR Extractor", layout="wide")

# --- UI Sidebar: Vault & Config ---
st.sidebar.title("Configuration Vault")

st.sidebar.subheader("Groq API Keys (Dynamic Rotation)")
key1 = st.sidebar.text_input("Groq Key 1", type="password")
key2 = st.sidebar.text_input("Groq Key 2", type="password")
key3 = st.sidebar.text_input("Groq Key 3", type="password")
key4 = st.sidebar.text_input("Groq Key 4", type="password")

if st.sidebar.button("Update Keys"):
    vault.update_keys([key1, key2, key3, key4])
    st.sidebar.success(f"Registered {len(st.session_state.groq_keys)} active keys.")

st.sidebar.subheader("Extraction Settings")
selected_model = st.sidebar.selectbox("Model", AVAILABLE_MODELS, index=0)

templates = get_template_names() + ["Custom Schema"]
selected_template = st.sidebar.selectbox("Select Domain Template", templates)

schema_dict = {}
if selected_template == "Custom Schema":
    st.sidebar.markdown("### Custom Blueprint")
    # Initialize default custom grid
    if 'custom_grid' not in st.session_state:
        st.session_state.custom_grid = pd.DataFrame([
            {"Parameter Name": "custom_metric_1", "Data Type": "string"},
            {"Parameter Name": "custom_metric_2", "Data Type": "integer"}
        ])
    
    edited_df = st.sidebar.data_editor(st.session_state.custom_grid, num_rows="dynamic")
    for _, row in edited_df.iterrows():
        name = str(row.get("Parameter Name", "")).strip()
        dtype = str(row.get("Data Type", "")).strip()
        if name and dtype:
            schema_dict[name] = dtype
else:
    schema_dict = get_template_schema(selected_template)


# --- Main Viewport ---
st.title("Universal Spatial SLR Extractor")

uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"])

if uploaded_file is not None and st.button("Run Extraction Pipeline"):
    if not st.session_state.groq_keys:
        st.error("Please add and update at least one Groq API Key in the sidebar.")
    elif not schema_dict:
        st.error("Schema is empty. Please define at least one parameter.")
    else:
        with st.spinner("Step 1/3: Parsing Binary PDF Stream..."):
            pdf_bytes = uploaded_file.getvalue()
            source_text = extract_text_from_pdf(pdf_bytes)
            
        with st.spinner(f"Step 2/3: Enforcing constraints via {selected_model}..."):
            llm_result = extract_data(source_text, selected_template, schema_dict, selected_model)
        
        if llm_result:
            with st.spinner("Step 3/3: Mapping coordinates and rendering canvas..."):
                # Flatten the Pydantic model into a list of dicts for the table and annotation
                records = []
                quotes_and_indices = []
                qc_index = 1
                
                # Dynamic model fields
                model_dump = llm_result.model_dump()
                for param_name, wrapper_obj in model_dump.items():
                    if wrapper_obj is not None:
                        val = wrapper_obj.get("value")
                        quote = wrapper_obj.get("verbatim_quote")
                        
                        records.append({
                            "qc_index": f"[{qc_index}]",
                            "parameter": param_name,
                            "value": val,
                            "verbatim_quote": quote
                        })
                        quotes_and_indices.append((quote, qc_index))
                        qc_index += 1
                
                # Annotate PDF
                annotated_pdf_bytes = annotate_pdf(pdf_bytes, quotes_and_indices)
                st.session_state.records = records
                st.session_state.annotated_pdf_bytes = annotated_pdf_bytes
                st.success("Extraction Complete!")

# --- Dual Viewport Render ---
if 'records' in st.session_state and 'annotated_pdf_bytes' in st.session_state:
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Structured Audit Ledger")
        df_records = pd.DataFrame(st.session_state.records)
        if not df_records.empty:
            st.dataframe(df_records, use_container_width=True)
            
            # Export
            excel_bytes = generate_excel_bytes(st.session_state.records, selected_template)
            st.download_button(
                label="📥 Download Excel Workbook",
                data=excel_bytes,
                file_name="extraction_audit.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No data extracted.")
            
    with col2:
        st.subheader("Live PDF Preview")
        # Convert PDF pages to images using PyMuPDF to bypass browser iframe blocks
        try:
            doc = fitz.open(stream=st.session_state.annotated_pdf_bytes, filetype="pdf")
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=150) # 150 DPI is a good balance of quality and performance
                st.image(pix.tobytes("png"), caption=f"Page {page_num + 1}", use_container_width=True)
        except Exception as e:
            st.error(f"Could not render PDF preview: {e}")
