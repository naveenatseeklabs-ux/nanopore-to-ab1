import streamlit as st
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import io

st.set_page_config(page_title="Nanopore Tab 4 to FASTQ", layout="wide")

st.title("🧬 Nanopore Confidence Visualizer")
st.write("This tool turns your Tab 4 coverage data into a FASTQ file you can open in a trace viewer.")

uploaded_file = st.file_uploader("Upload your 4-tab Excel file", type=['xlsx'])

if uploaded_file:
    try:
        # Load Tab 4 (Index 3)
        df = pd.read_excel(uploaded_file, sheet_name=3)
        
        # Verify columns exist
        required = ['POS', 'REF', 'Match', 'TotalReads']
        if not all(col in df.columns for col in required):
            st.error(f"Missing columns! Ensure Tab 4 has: {', '.join(required)}")
        else:
            st.write("### Data Preview (Tab 4)", df.head(5))

            if st.button("Generate FASTQ with Confidence"):
                # 1. Calculate Quality Score (0-40 scale)
                # Formula: (Matches / Total) * 40
                df['Quality'] = (df['Match'] / df['TotalReads'] * 40).fillna(0).round().astype(int).clip(upper=40)
                
                # 2. Build the Sequence Record
                seq_str = "".join(df['REF'].astype(str).str.upper())
                quals = df['Quality'].tolist()
                
                record = SeqRecord(
                    Seq(seq_str), 
                    id="Nanopore_Sample", 
                    description="Converted_from_Tab4_Coverage"
                )
                record.letter_annotations["phred_quality"] = quals

                # 3. Export to FASTQ (Works perfectly in Biopython)
                output = io.StringIO()
                SeqIO.write(record, output, "fastq")
                
                st.success(f"Processed {len(df)} bases. FASTQ ready!")
                st.download_button(
                    label="📥 Download FASTQ File",
                    data=output.getvalue(),
                    file_name="nanopore_confidence.fastq",
                    mime="text/plain"
                )

    except Exception as e:
        st.error(f"An error occurred: {e}")

st.info("💡 **How to view:** Download the FASTQ and drag it into **SnapGene Viewer**. You will see your sequence with the confidence bars underneath.")
