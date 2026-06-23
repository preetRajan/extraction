import fitz
import io
from rapidfuzz import fuzz

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text sequentially from PDF blocks, preserving basic structure.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        # Using "text" to get standard reading order string
        full_text += page.get_text("text") + "\n"
    return full_text

def annotate_pdf(pdf_bytes: bytes, quotes_and_indices: list) -> bytes:
    """
    Finds verbatim quotes in the PDF, highlights them in yellow, 
    and adds a red numerical QC marker slightly to the left.
    quotes_and_indices is a list of tuples: (verbatim_quote_string, qc_index)
    Returns annotated PDF as bytes.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for quote, index in quotes_and_indices:
        if not quote or str(quote).strip() == "":
            continue
            
        found = False
        # Phase 1: Exact search
        for page in doc:
            text_instances = page.search_for(quote)
            if text_instances:
                for inst in text_instances:
                    # Add highlight
                    annot = page.add_highlight_annot(inst)
                    annot.update()
                    # Add red numerical marker [index] to the left (using standard "helv" font)
                    rect = fitz.Rect(max(0, inst.x0 - 25), inst.y0, inst.x0, inst.y0 + 12)
                    page.insert_textbox(rect, f"[{index}]", color=(1, 0, 0), fontsize=10, fontname="helv", align=fitz.TEXT_ALIGN_RIGHT)
                found = True
                break
                
        # Phase 2: Fuzzy matching fallback if exact search failed
        if not found:
            for page in doc:
                blocks = page.get_text("blocks")
                for b in blocks:
                    block_text = b[4]
                    # Check sequence distance score
                    if fuzz.partial_ratio(quote.lower(), block_text.lower()) > 85:
                        # Found a match! Use the block's bounding box
                        inst = fitz.Rect(b[0], b[1], b[2], b[3])
                        annot = page.add_highlight_annot(inst)
                        annot.update()
                        
                        rect = fitz.Rect(max(0, inst.x0 - 25), inst.y0, inst.x0, inst.y0 + 12)
                        page.insert_textbox(rect, f"[{index}]", color=(1, 0, 0), fontsize=10, fontname="helv", align=fitz.TEXT_ALIGN_RIGHT)
                        
                        found = True
                        break
                if found:
                    break

    out_pdf = io.BytesIO()
    doc.save(out_pdf)
    return out_pdf.getvalue()
