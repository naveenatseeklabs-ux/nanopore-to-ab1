import streamlit as st
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import io

st.set_page_config(page_title="Nanopore Tab 4 Trace Generator", layout="wide")

st.title("🧬 Nanopore Tab 4 Trace Generator")
st.write("This tool analyzes the per-base coverage in Tab 4 to create a confidence trace.")

uploaded_file = st.file_uploader("Upload your 4-tab Excel file", type=['xlsx'])

if uploaded_file:
    try:
        # Load only Tab 4 (Index 3)
        df = pd.read_excel(uploaded_file, sheet_name=3)
        st.write("### Tab 4 Preview", df.head(5))

        if st.button("Generate Trace from Tab 4"):
            # 1. Calculate Confidence (Quality Score) 
            # We use the Match/TotalReads ratio scaled to 0-40 (Phred scale)
            df['Quality'] = (df['Match'] / df['TotalReads'] * 40).fillna(0).round().astype(int).clip(upper=40)
            
            # 2. Identify Mutation Sites
            # If Match < TotalReads, it means other bases (A,T,C,G) were called there
            mutation_notes = []
            for idx, row in df.iterrows():
                if row['Match'] < row['TotalReads']:
                    mutation_notes.append(f"Pos {row['POS']}: {row['Match']}/{row['TotalReads']} match")

            # 3. Build Record
            seq_str = "".join(df['REF'].astype(str).str.upper())
            quals = df['Quality'].tolist()
            
            record = SeqRecord(Seq(seq_str), id="Nanopore_Tab4_Trace")
            record.letter_annotations["phred_quality"] = quals
            # Add mutation data to the description/comments
            record.description = "Mutations: " + " | ".join(mutation_notes[:20]) + "..." 

            # 4. Export to .ab1
            output = io.BytesIO()
            SeqIO.write(record, output, "abi")
            
            st.success(f"Analyzed {len(df)} positions. Found {len(mutation_notes)} potential mutation sites.")
            st.download_button(
                label="📥 Download .ab1 File",
                data=output.getvalue(),
                file_name="tab4_confidence_trace.ab1",
                mime="application/octet-stream"
            )

    except Exception as e:
        st.error(f"Error: {e}. Make sure the 4th tab has 'POS', 'REF', 'Match', and 'TotalReads' columns.")
