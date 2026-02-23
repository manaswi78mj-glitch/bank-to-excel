import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import os

# --- PROFESSIONAL THEME SETUP ---
st.set_page_config(page_title="BankStat to Excel", layout="centered", page_icon="🏦")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #333333 !important; }
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #dee2e6; }
    .stButton>button { background-color: #0056b3 !important; color: white !important; border-radius: 8px; font-weight: bold; width: 100%; }
    .main-header { color: #0056b3; font-size: 32px; font-weight: 700; text-align: center; }
    .disclaimer-box { background-color: #fff9db; border: 1px solid #f59f00; padding: 15px; border-radius: 8px; color: #333333; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN LOGIC ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login():
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    st.markdown("<p class='main-header'>BankStat to Excel</p>", unsafe_allow_html=True)
    st.write("<p style='text-align: center; color: #6c757d;'>Secure Professional Converter</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Access Key", type="password")
        if st.button("Login"):
            if pwd == "BankFree2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid Key")

if not st.session_state["authenticated"]:
    login()
else:
    # --- AUTHENTICATED INTERFACE ---
    col_logo, col_text = st.columns([1, 4])
    with col_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=80)
        else:
            st.title("🏦")
    with col_text:
        st.markdown("<h2 style='color: #0056b3; margin-top: 10px;'>Professional Portal</h2>", unsafe_allow_html=True)

    st.markdown("---")

    with st.sidebar:
        st.header("Settings")
        pdf_pass = st.text_input("PDF Password (if any)", type="password")
        st.divider()
        st.write("🔒 **Privacy:** Data is processed in-memory and never stored.")

    uploaded_file = st.file_uploader("Upload Bank Statement (Digital PDF)", type="pdf")

    if uploaded_file:
        try:
            with pdfplumber.open(uploaded_file, password=pdf_pass) as pdf:
                all_rows = []
                with st.spinner('Extracting data...'):
                    for page in pdf.pages:
                        # Improved table settings for borderless e-statements
                        table = page.extract_table({
                            "vertical_strategy": "text", 
                            "horizontal_strategy": "text"
                        })
                        if table:
                            all_rows.append(pd.DataFrame(table))

                if all_rows:
                    final_df = pd.concat(all_rows, ignore_index=True)
                    
                    # 1. Remove rows that are completely empty
                    final_df = final_df.dropna(how='all')
                    
                    # 2. Set headers and filter repeating ones
                    final_df.columns = final_df.iloc[0]
                    final_df = final_df[1:]
                    
                    # Filter out rows that repeat header text (e.g., "Particulars")
                    header_text = str(final_df.columns[0])
                    final_df = final_df[final_df.iloc[:, 0].astype(str) != header_text]
                    
                    # 3. Final drop for any remaining null rows
                    final_df = final_df.dropna(subset=[final_df.columns[0]])

                    st.subheader("📊 Data Preview")
                    st.dataframe(final_df, use_container_width=True)

                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        final_df.to_excel(writer, index=False)
                    
                    st.download_button(
                        label="📥 Download Excel File",
                        data=output.getvalue(),
                        file_name="Converted_Statement.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("No tabular data found. Is this a scanned image instead of a digital PDF?")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # --- DISCLAIMER SECTION ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class='disclaimer-box'>
            <strong>⚖️ Disclaimer & Security Notice</strong><br>
            <ul>
                <li><strong>Privacy:</strong> Built by <strong>Manaswi</strong> for CA professionals.</li>
                <li><strong>Owner Security:</strong> Portal is key-protected.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
