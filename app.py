import streamlit as st
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import io

st.set_page_config(page_title="Nanopore to AB1 Converter", layout="wide")

st.title("🧬 Nanopore to Trace Converter")
st.write("Upload an Excel/CSV to generate a synthetic .ab1 file with confidence scores.")

uploaded_file = st.file_uploader("Upload your file", type=['csv', 'xlsx'])

if uploaded_file:
    # 1. Load the data
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    st.write("### Data Preview", df.head(5))

    # 2. Select columns
    col1, col2 = st.columns(2)
    with col1:
        base_col = st.selectbox("Select the Base Column (A, C, G, T)", df.columns)
    with col2:
        qual_col = st.selectbox("Select the Confidence/Quality Column", df.columns)

    if st.button("Generate .ab1 File"):
        try:
            # 3. Clean Data: Remove rows where base or quality is missing
            df_clean = df.dropna(subset=[base_col, qual_col]).copy()
            
            # Convert Quality to numeric, forcing errors to NaN, then drop those NaNs
            df_clean[qual_col] = pd.to_numeric(df_clean[qual_col], errors='coerce')
            df_clean = df_clean.dropna(subset=[qual_col])
            
            # Ensure bases are strings and uppercase
            seq_str = "".join(df_clean[base_col].astype(str).str.strip().str.upper())
            # Convert quality to integers (Phred scores must be ints)
            quals = df_clean[qual_col].astype(float).round().astype(int).tolist()
            
            if len(seq_str) == 0:
                st.error("No valid data found in those columns. Please check your selection.")
            else:
                # 4. Create the Trace Record
                record = SeqRecord(Seq(seq_str), id="Nanopore_Converted")
                record.letter_annotations["phred_quality"] = quals

                # Write to binary ABIF format
                output = io.BytesIO()
                SeqIO.write(record, output, "abi")
                
                st.success(f"Successfully processed {len(seq_str)} bases!")
                st.download_button(
                    label="📥 Download .ab1 File",
                    data=output.getvalue(),
                    file_name="nanopore_trace.ab1",
                    mime="application/octet-stream"
                )
        except Exception as e:
            st.error(f"An error occurred: {e}")

st.info("💡 Pro Tip: Make sure your Quality column contains numbers (like 20, 30, 40) representing the confidence of each base.")
