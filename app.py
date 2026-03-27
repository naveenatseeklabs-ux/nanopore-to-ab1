import streamlit as st
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import io
import os

st.set_page_config(page_title="Nanopore to Benchling Trace", layout="wide")
st.title("🧬 Nanopore to Benchling Trace Generator")

# 1. Look for the template you uploaded
template_path = "template.ab1" # Make sure your file on GitHub is named exactly this

if not os.path.exists(template_path):
    st.error(f"Error: '{template_path}' not found in your GitHub repo. Please rename your .ab1 file to 'template.ab1'.")
else:
    uploaded_file = st.file_uploader("Upload your 4-tab Excel file", type=['xlsx'])

    if uploaded_file:
        try:
            # 2. Load Tab 4 (Index 3)
            df = pd.read_excel(uploaded_file, sheet_name=3)
            st.write("### Data Preview (Tab 4)", df.head(3))

            if st.button("Generate Trace for Benchling"):
                # 3. Calculate Quality Scores (0-40)
                # (Match / TotalReads) * 40
                df['Quality'] = (df['Match'] / df['TotalReads'] * 40).fillna(0).round().astype(int).clip(upper=40)
                
                new_seq_str = "".join(df['REF'].astype(str).str.upper())
                new_quals = df['Quality'].tolist()

                # 4. Load the template and SWAP the data
                # We read the template metadata and replace the sequence/quality
                with open(template_path, "rb") as h:
                    record = SeqIO.read(h, "abi")
                
                # Overwrite the template's old sequence and quality
                record.seq = Seq(new_seq_str)
                record.letter_annotations["phred_quality"] = new_quals
                
                # 5. Export the 'Hacked' File
                output = io.BytesIO()
                SeqIO.write(record, output, "abi")
                
                st.success(f"Success! Replaced template data with {len(new_seq_str)} Nanopore bases.")
                st.download_button(
                    label="📥 Download .ab1 for Benchling",
                    data=output.getvalue(),
                    file_name="nanopore_benchling_trace.ab1",
                    mime="application/octet-stream"
                )

        except Exception as e:
            st.error(f"An error occurred: {e}")

st.info("💡 **Benchling Tip:** After downloading, import this into a Benchling Alignment. You will see your Nanopore confidence scores as vertical bars!")
