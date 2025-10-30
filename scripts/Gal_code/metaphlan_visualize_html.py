import os
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

# ==============================================================
# Function: Generate combined Sunburst plots for one MetaPhlAn output
# ==============================================================
def generate_metaphlan_sunburst(input_path, output_dir):
    # Extract sample ID from file name (last 8 chars before extension)
    base_name = os.path.basename(input_path)
    sample_id = os.path.splitext(base_name)[0][-8:]
    output_path = os.path.join(output_dir, f"{sample_id}_sunburst.html")

    print(f"🔹 Processing: {base_name}  →  {output_path}")

    # --------------------------------------------------
    # 1️⃣ Load MetaPhlAn output
    # --------------------------------------------------
    df = pd.read_csv(
        input_path,
        sep="\t",
        comment="#",
        header=None,
        names=["clade_name", "NCBI_tax_id", "relative_abundance", "additional_species"]
    )

    if df.empty:
        print(f"⚠️ Skipping empty file: {input_path}")
        return

    # --------------------------------------------------
    # 2️⃣ Split hierarchical taxonomy and ensure all columns exist
    # --------------------------------------------------
    tax_split = df["clade_name"].str.split("|", expand=True)
    all_levels = ["Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species", "t"]

    # If fewer columns exist, fill missing with "Unclassified"
    if tax_split.shape[1] < len(all_levels):
        for _ in range(len(all_levels) - tax_split.shape[1]):
            tax_split[tax_split.shape[1]] = "Unclassified"

    tax_split.columns = all_levels

    # Clean prefixes (k__, p__, etc.)
    for c in tax_split.columns:
        tax_split[c] = tax_split[c].str.replace(r"^[a-z]__", "", regex=True).fillna("Unclassified")

    # Merge with abundance
    df = pd.concat([tax_split, df["relative_abundance"]], axis=1)
    df["relative_abundance"] = pd.to_numeric(df["relative_abundance"], errors="coerce").fillna(0)

    # --------------------------------------------------
    # 3️⃣ Define taxonomic levels to visualize
    # --------------------------------------------------
    levels = {
        "Phylum": ["Kingdom", "Phylum"],
        "Class": ["Kingdom", "Phylum", "Class"],
        "Order": ["Kingdom", "Phylum", "Class", "Order"],
        "Family": ["Kingdom", "Phylum", "Class", "Order", "Family"],
        "Genus": ["Kingdom", "Phylum", "Class", "Order", "Family", "Genus"]
    }

    # --------------------------------------------------
    # 4️⃣ Create subplot grid
    # --------------------------------------------------
    rows = len(levels)
    fig = make_subplots(
        rows=rows,
        cols=1,
        specs=[[{"type": "domain"}] for _ in range(rows)],
        subplot_titles=[f"{level} Level" for level in levels.keys()]
    )

    # --------------------------------------------------
    # 5️⃣ Generate Sunburst plots for each level safely
    # --------------------------------------------------
    row_idx = 1
    for level_name, path in levels.items():
        valid_cols = [col for col in path if col in df.columns]
        if len(valid_cols) < 2:
            print(f"⚠️ Skipping {level_name} (not enough taxonomic levels in {sample_id})")
            continue

        df_level = df.groupby(valid_cols, as_index=False)["relative_abundance"].sum()

        sun = px.sunburst(
            df_level,
            path=valid_cols,
            values="relative_abundance",
            color="Phylum"
            if "Phylum" in valid_cols else valid_cols[1],  # color by Phylum or next available level
            title=f"{level_name} Level",    
        )

        for trace in sun.data:
            fig.add_trace(trace, row=row_idx, col=1)
        row_idx += 1

    # --------------------------------------------------
    # 6️⃣ Save to HTML
    # --------------------------------------------------
    fig.update_layout(
        title_text=f"MetaPhlAn Taxonomic Composition — {sample_id}",
        height=3000,
        showlegend=False,
    )

    os.makedirs(output_dir, exist_ok=True)
    fig.write_html(output_path)
    print(f"✅ Saved: {output_path}\n")


# ==============================================================
# Batch process all MetaPhlAn outputs in a folder
# ==============================================================
input_dir = r"C:\Users\hadis\OneDrive\Documents\Project\Ga_output\MetaphlanOutput.rocrate\relative_abundances"
output_dir = r"C:\Users\hadis\OneDrive\Documents\Project\Soil_Pipeline\soil-pipeline\Metaphlan_sunburst_all_levels"

for file in os.listdir(input_dir):
    if file.endswith(".tabular") or file.endswith(".txt") or file.endswith(".tsv"):
        input_path = os.path.join(input_dir, file)
        generate_metaphlan_sunburst(input_path, output_dir)

print("🎉 All Sunburst plots generated successfully!")
# ==============================================================