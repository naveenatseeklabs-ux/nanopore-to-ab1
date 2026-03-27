import streamlit as st
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
import io
import os

st.set_page_config(page_title="Nanopore to Benchling Trace", layout="wide")
st.title("🧬 Nanopore to Benchling Trace Generator")

template_path = "template.ab1"

if not os.path.exists(template_path):
    st.error(f"Error: '{template_path}' not found. Please ensure your file is named 'template.ab1' in GitHub.")
else:
    uploaded_file = st.file_uploader("Upload your 4-tab Excel file", type=['xlsx'])

    if uploaded_file:
        try:
            # 1. Load Tab 4
            df = pd.read_excel(uploaded_file, sheet_name=3)
            
            if st.button("Generate Trace for Benchling"):
                # 2. Calculate New Quality (0-40 scale)
                df['Quality'] = (df['Match'] / df['TotalReads'] * 40).fillna(0).round().astype(int).clip(upper=40)
                new_seq_str = "".join(df['REF'].astype(str).str.upper())
                new_quals = df['Quality'].tolist()

                # 3. Load and Hack the Template
                with open(template_path, "rb") as h:
                    record = SeqIO.read(h, "abi")
                
                # --- THE FIX ---
                # We must clear the old annotations before changing the sequence
                record.letter_annotations = {} 
                
                # Now we can safely set the new data
                record.seq = Seq(new_seq_str)
                record.letter_annotations["phred_quality"] = new_quals
                # ---------------

                # 4. Export the modified file
                output = io.BytesIO()
                SeqIO.write(record, output, "abi")
                
                st.success(f"Success! Processed {len(new_seq_str)} bases.")
                st.download_button(
                    label="📥 Download .ab1 for Benchling",
                    data=output.getvalue(),
                    file_name="nanopore_benchling_trace.ab1",
                    mime="application/octet-stream"
                )

        except Exception as e:
            st.error(f"An error occurred: {e}")

st.info("💡 **Benchling Tip:** Once downloaded, align this file to your reference in Benchling. Ensure 'Trace Quality' is turned on in the alignment settings to see your confidence bars.")
