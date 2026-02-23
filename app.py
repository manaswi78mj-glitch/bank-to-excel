import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

# --- PROFESSIONAL THEMING ---
st.set_page_config(page_title="BankStat to Excel", layout="wide")

# Custom CSS for Blue & White Professional Look
st.markdown("""
    <style>
    .main {
        background-color: #FFFFFF;
    }
    .stButton>button {
        background-color: #004a99;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        background-color: #003366;
        color: white;
    }
    h1, h2, h3 {
        color: #004a99;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stSidebar {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN LOGIC ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login():
    # Header with "Logo" text
    st.markdown("<h1 style='text-align: center;'>🏦 BankStat <span style='color: #333;'>to Excel</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Secure Financial Data Transformation</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.write("---")
        pwd = st.text_input("Enter Access Key:", type="password")
        if st.button("Access Portal"):
            if pwd == "BankFree2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid Key")

if not st.session_state["authenticated"]:
    login()
else:
    # --- MAIN INTERFACE ---
    # Top Logo Bar
    st.markdown("<h2 style='margin-bottom: 0;'>🏦 BankStat to Excel</h2>", unsafe_allow_html=True)
    st.write("Professional Audit & Reconciliation Utility")
    st.markdown("---")

    with st.sidebar:
        st.title("Settings")
        pdf_pass = st.text_input("Encrypted PDF Password:", type="password", help="Most bank PDFs are locked. Enter the password here.")
        clean_mode = st.toggle("Smart Cleaning (Recommended)", value=True)
        st.write("---")
        st.write("Need help? Contact Support.")

    uploaded_file = st.file_uploader("Upload Bank Statement (PDF)", type="pdf")

    if uploaded_file:
        try:
            with pdfplumber.open(uploaded_file, password=pdf_pass) as pdf:
                all_rows = []
                with st.status("Processing Securely...", expanded=True) as status:
                    for i, page in enumerate(pdf.pages):
                        st.write(f"Analyzing Page {i+1}...")
                        table = page.extract_table()
                        if table:
                            df_page = pd.DataFrame(table)
                            all_rows.append(df_page)
                    status.update(label="Conversion Complete!", state="complete", expanded=False)

                if all_rows:
                    final_df = pd.concat(all_rows, ignore_index=True)

                    if clean_mode:
                        final_df = final_df.dropna(how='all', axis=0).dropna(how='all', axis=1)
                        final_df.columns = final_df.iloc[0]
                        final_df = final_df[1:]
                        header_val = final_df.columns[0]
                        final_df = final_df[final_df.iloc[:, 0] != header_val]

                    st.subheader("📊 Data Preview")
                    st.dataframe(final_df, use_container_width=True)

                    # Export to Excel
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        final_df.to_excel(writer, index=False, sheet_name='Sheet1')
                    
                    st.download_button(
                        label="📥 Download Excel (.xlsx)",
                        data=output.getvalue(),
                        file_name="Bank_Statement_Export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e:
            st.error(f"Error: {e}. Please verify your PDF password.")

    # --- PRIVACY FOOTER ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    colA, colB = st.columns(2)
    with colA:
        st.caption("🔒 **Security:** SSL Encrypted & Session-Only processing.")
    with colB:
        st.caption("💻 **Build:** v2.0 - Optimized for CA Professionals.")
