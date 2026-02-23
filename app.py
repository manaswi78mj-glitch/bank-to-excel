import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Pro Bank Converter", layout="wide")

# Simple Login Logic
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login():
    st.title("🔐 Secure Access")
    pwd = st.text_input("Enter Access Key:", type="password")
    if st.button("Login"):
        if pwd == "BankFree2026": # You can change this
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid Key")

if not st.session_state["authenticated"]:
    login()
else:
    st.title("🏦 Pro Bank-to-Excel Converter")
    st.info("Upload your PDF. Our 'Smart Cleaner' will handle the headers and alignment.")

    with st.sidebar:
        pdf_pass = st.text_input("PDF Password (if any):", type="password")
        clean_mode = st.checkbox("Enable Smart Cleaning", value=True)

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        try:
            with pdfplumber.open(uploaded_file, password=pdf_pass) as pdf:
                all_rows = []
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        # Convert to DataFrame
                        df_page = pd.DataFrame(table)
                        all_rows.append(df_page)

                if all_rows:
                    final_df = pd.concat(all_rows, ignore_index=True)

                    # --- SMART CLEANER LOGIC ---
                    if clean_mode:
                        # 1. Drop completely empty rows/columns
                        final_df = final_df.dropna(how='all', axis=0).dropna(how='all', axis=1)
                        # 2. Use the first row as header
                        final_df.columns = final_df.iloc[0]
                        final_df = final_df[1:]
                        # 3. Remove rows that repeat the header (common in multi-page PDFs)
                        header_val = final_df.columns[0]
                        final_df = final_df[final_df.iloc[:, 0] != header_val]

                    st.write("### Data Preview")
                    st.dataframe(final_df, use_container_width=True)

                    # Export to Excel
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        final_df.to_excel(writer, index=False, sheet_name='Bank_Statement')
                    
                    st.download_button(
                        label="📥 Download Excel File",
                        data=output.getvalue(),
                        file_name="Converted_Statement.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e:
            st.error(f"Error: {e}. If the PDF is locked, enter the password in the sidebar.")
            # --- Privacy & Safety Footer ---
st.markdown("---")
st.caption("🔒 **Privacy & Security Notice:**")
st.caption("""
- **Zero Storage:** We do not store your PDF files, passwords, or extracted data on any server.
- **Session Based:** All processing happens in temporary memory and is deleted as soon as you close this tab.
- **Open Source:** This tool is built using transparent Python libraries to ensure financial data remains private.
""")

