import pandas as pd
import io

def generate_excel_bytes(data_records: list, template_name: str) -> bytes:
    """
    Takes a list of dictionaries containing the extracted records 
    and packages them into a multi-tab capable Excel workbook using xlsxwriter.
    """
    df = pd.DataFrame(data_records)
    
    if not df.empty:
        # Reorder and rename columns for the QC ledger
        df = df[['qc_index', 'parameter', 'value', 'verbatim_quote']]
        df.columns = ['QC Index', 'Parameter Framework Name', 'Extracted Matrix Entry', 'Source Verbatim Text']
        
    output = io.BytesIO()
    # Engine must be xlsxwriter
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet names have a 31 character limit in Excel
        sheet_name = template_name.replace('/', '_').replace('\\', '_')[:31]
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        if not df.empty:
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Add some formatting
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D7E4BC',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            worksheet.set_column('A:A', 12)
            worksheet.set_column('B:B', 30)
            worksheet.set_column('C:C', 30)
            worksheet.set_column('D:D', 60)
        
    return output.getvalue()
