import pandas as pd

import plotly.express as px
from plotly.subplots import make_subplots

# --------------------------------------------------
# 1️⃣ Load MetaPhlAn output file
# --------------------------------------------------
df = pd.read_csv(
    r"C:\Users\hadis\OneDrive\Documents\Project\Galaxy_output\MetaphlanOutput.rocrate\relative_abundances\MetaPhlAn_on_data_1__Predicted_taxon_relative_abundances_SCBI_012.tabular",
    sep="\t",
    comment="#",
    header=None,
    names=["clade_name", "NCBI_tax_id", "relative_abundance", "additional_species"]
)

# --------------------------------------------------
# 2️⃣ Split hierarchical taxonomy into columns
# --------------------------------------------------
tax_split = df["clade_name"].str.split("|", expand=True)
tax_split.columns = ["Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species", "t"][:tax_split.shape[1]]

# Clean prefixes like k__, p__, etc.
for c in tax_split.columns:
    tax_split[c] = tax_split[c].str.replace(r"^[a-z]__", "", regex=True)

# Merge taxonomy with abundance
df = pd.concat([tax_split, df["relative_abundance"]], axis=1)
df = df.fillna("Unclassified").replace("", "Unclassified")

# Convert abundance to numeric
df["relative_abundance"] = pd.to_numeric(df["relative_abundance"], errors="coerce")

# --------------------------------------------------
# 3️⃣ Define levels for Sunburst visualization
# --------------------------------------------------
levels = {
    "Phylum": ["Kingdom", "Phylum"],
    "Class": ["Kingdom", "Phylum", "Class"],
    "Order": ["Kingdom", "Phylum", "Class", "Order"],
    "Family": ["Kingdom", "Phylum", "Class", "Order", "Family"],
    "Genus": ["Kingdom", "Phylum", "Class", "Order", "Family", "Genus"]
}

# --------------------------------------------------
# 4️⃣ Create subplot grid (1 column × 5 rows)
# --------------------------------------------------
rows = len(levels)
fig = make_subplots(
    rows=rows,
    cols=1,
    specs=[[{"type": "domain"}] for _ in range(rows)],
    subplot_titles=[f"{level} Level" for level in levels.keys()]
)

# --------------------------------------------------
# 5️⃣ Generate one Sunburst per taxonomic level
# --------------------------------------------------
row_idx = 1
for level_name, path in levels.items():
    df_level = df.groupby(path, as_index=False)["relative_abundance"].sum()

    # Create Sunburst chart
    sun = px.sunburst(
        df_level,
        path=path,
        values="relative_abundance",
        color=path[1] if len(path) > 1 else None,  # color by Phylum or higher level
        title=f"{level_name} Level",
    )

    for trace in sun.data:
        fig.add_trace(trace, row=row_idx, col=1)

    row_idx += 1

# --------------------------------------------------
# 6️⃣ Final layout and export
# --------------------------------------------------
fig.update_layout(
    title_text="MetaPhlAn Taxonomic Composition — Sunburst Charts (Phylum to Genus)",
    height=3000,
    showlegend=False,
)

fig.write_html("metaphlan_sunburst_all_levels.html")
print("✅ Saved combined Sunburst plots → metaphlan_sunburst_all_levels.html")
