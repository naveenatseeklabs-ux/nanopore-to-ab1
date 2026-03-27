import streamlit as st
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import io

st.set_page_config(page_title="Nanopore to AB1 Converter")

st.title("🧬 Nanopore to Trace Converter")
st.write("Upload an Excel/CSV to generate a synthetic .ab1 file with confidence scores.")

uploaded_file = st.file_uploader("Upload your file", type=['csv', 'xlsx'])

if uploaded_file:
    # 1. Load the data
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    st.write("Preview:", df.head(3))

    # 2. Select columns
    col1, col2 = st.columns(2)
    with col1:
        base_col = st.selectbox("Base Column (A,C,G,T)", df.columns)
    with col2:
        qual_col = st.selectbox("Confidence/Quality Column", df.columns)

    if st.button("Generate .ab1"):
        # 3. Create the Trace Record
        df = df.dropna(subset=[base_col, qual_col])
        seq_str = "".join(df[base_col].astype(str).str.upper())
        quals = df[qual_col].astype(float).astype(int).tolist()
        
        record = SeqRecord(Seq(seq_str), id="Nanopore_Converted")
        record.letter_annotations["phred_quality"] = quals

        # 4. Write to binary ABIF format
        output = io.BytesIO()
        SeqIO.write(record, output, "abi")
        
        st.success("File Ready!")
        st.download_button(
            label="Download .ab1 File",
            data=output.getvalue(),
            file_name="converted_trace.ab1",
            mime="application/octet-stream"
        )

st.info("💡 Open the downloaded file in SnapGene or 4Peaks to see the quality bars.")
