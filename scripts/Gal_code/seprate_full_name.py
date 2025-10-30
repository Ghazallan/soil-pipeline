import os
import pandas as pd
import re

# --------------------------------------------------
# 1️⃣ Define directories
# --------------------------------------------------
input_dir = r"C:\Users\hadis\OneDrive\Documents\Project\Ga_output\MetaphlanOutput.rocrate\relative_abundances"
output_dir = r"C:\Users\hadis\OneDrive\Documents\Project\Ga_output\MetaphlanOutput.rocrate\merged_by_taxonomic_level"

# Create output directory if missing
os.makedirs(output_dir, exist_ok=True)

# --------------------------------------------------
# 2️⃣ Find all MetaPhlAn output files
# --------------------------------------------------
files = [f for f in os.listdir(input_dir) if f.endswith((".tabular", ".txt", ".tsv"))]
if not files:
    raise FileNotFoundError("❌ No MetaPhlAn output files found in input directory!")

print(f"🔍 Found {len(files)} MetaPhlAn files to merge...\n")

# --------------------------------------------------
# 3️⃣ Merge all MetaPhlAn outputs
# --------------------------------------------------
merged_df = pd.DataFrame()

for file in files:
    file_path = os.path.join(input_dir, file)
    try:
        df = pd.read_csv(file_path, sep="\t", comment="#", header=None)
    except Exception as e:
        print(f"⚠️ Skipping {file} (read error: {e})")
        continue

    if df.shape[1] < 2:
        print(f"⚠️ Skipping {file}: not enough columns.")
        continue

    # Select clade_name and relative_abundance columns
    df = df.iloc[:, [0, 2]] if df.shape[1] >= 3 else df.iloc[:, [0, 1]]
    df.columns = ["clade_name", "relative_abundance"]

    # Extract sample ID (e.g. GUAN_049)
    match = re.search(r"([A-Z]{2,5}_\d{3})", file)
    sample_id = match.group(1) if match else os.path.splitext(file)[0]
    df = df.rename(columns={"relative_abundance": sample_id})

    # Merge into master table
    merged_df = df if merged_df.empty else pd.merge(merged_df, df, on="clade_name", how="outer")

# --------------------------------------------------
# 4️⃣ Clean merged data
# --------------------------------------------------
merged_df = merged_df.fillna(0)
merged_df = merged_df.sort_values("clade_name")

# Save main merged file
merged_out_path = os.path.join(output_dir, "merged_all_levels.tsv")
merged_df.to_csv(merged_out_path, sep="\t", index=False)
print(f"✅ Saved merged file: {merged_out_path}")

# --------------------------------------------------
# 5️⃣ Split and prepare taxonomy columns
# --------------------------------------------------
taxa_levels = ["kingdom", "phylum", "class", "order", "family", "genus", "species", "strain"]
split_cols = merged_df["clade_name"].str.split("|", expand=True)
split_cols.columns = taxa_levels[:split_cols.shape[1]]
df = pd.concat([merged_df, split_cols], axis=1)

# Identify sample columns
sample_cols = [c for c in df.columns if c not in ["clade_name"] + taxa_levels]
df[sample_cols] = df[sample_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

# --------------------------------------------------
# 6️⃣ Extract only the exact taxon level (no parent lines)
# --------------------------------------------------
for level in taxa_levels:
    if level not in df.columns:
        continue

    level_idx = taxa_levels.index(level)

    # Keep only rows where this level is the last defined (exact level)
    mask = df[taxa_levels[level_idx + 1:]].isna().all(axis=1)
    sub_df = df[mask].copy()
    if sub_df.empty:
        continue

    # Keep only entries that contain this exact level (e.g., |p__ for phylum)
    if level_idx > 0:
        pattern = rf"\|{level[0]}__"
        sub_df = sub_df[sub_df["clade_name"].str.contains(pattern, regex=True, na=False)]
    else:
        # For kingdom level, keep only k__ entries without a deeper |
        sub_df = sub_df[~sub_df["clade_name"].str.contains(r"\|", regex=True, na=False)]

    if sub_df.empty:
        continue

    # Create taxonomy path up to this level
    sub_df["taxonomy_path"] = sub_df[taxa_levels[: level_idx + 1]].apply(
        lambda r: "|".join([x for x in r if pd.notna(x)]), axis=1
    )

    # Collapse duplicates and sum across samples
    sub_df = sub_df.groupby("taxonomy_path", as_index=False)[sample_cols].sum()

    # Add total abundance column
    sub_df.insert(1, "total_abundance", sub_df[sample_cols].sum(axis=1))

    # Save output
    out_path = os.path.join(output_dir, f"merged_{level}_level.tsv")
    sub_df.to_csv(out_path, sep="\t", index=False)
    print(f"✅ Saved {level}-only file: {out_path}")
    print(f"📊 {sub_df.shape[0]} taxa × {len(sample_cols)} samples\n")
    # ✅ Simplify taxonomy path: always include kingdom + current level