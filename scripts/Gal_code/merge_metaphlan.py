import os
import pandas as pd

# --------------------------------------------------
# 1️⃣ Define directories
# --------------------------------------------------
input_dir = r"C:\Users\hadis\OneDrive\Documents\Project\Galaxy_output\MetaphlanOutput.rocrate\relative_abundances"
output_path = os.path.join(input_dir, "merged_metaphlan_outputs.tsv")

# --------------------------------------------------
# 2️⃣ Find all MetaPhlAn output files
# --------------------------------------------------
files = [f for f in os.listdir(input_dir) if f.endswith((".tabular", ".txt", ".tsv"))]
if not files:
    raise FileNotFoundError("❌ No MetaPhlAn output files found in input directory!")

print(f"🔍 Found {len(files)} files to merge...\n")

# --------------------------------------------------
# 3️⃣ Merge all into one table
# --------------------------------------------------
merged_df = pd.DataFrame()

for file in files:
    file_path = os.path.join(input_dir, file)

    # Read file
    df = pd.read_csv(
        file_path,
        sep="\t",
        comment="#",
        header=None,
        names=["clade_name", "NCBI_tax_id", "relative_abundance", "additional_species"],
        usecols=["clade_name", "relative_abundance"]
    )

    # Extract sample ID from last 8 chars before extension
    sample_id = os.path.splitext(file)[0][-8:]

    # Keep only clade and abundance, rename abundance column to sample name
    df = df[["clade_name", "relative_abundance"]].rename(columns={"relative_abundance": sample_id})

    if merged_df.empty:
        merged_df = df
    else:
        merged_df = pd.merge(merged_df, df, on="clade_name", how="outer")

# --------------------------------------------------
# 4️⃣ Clean and format output
# --------------------------------------------------
merged_df = merged_df.fillna(0)

# Sort by taxonomy for readability
merged_df = merged_df.sort_values("clade_name")

# Save as TSV
merged_df.to_csv(output_path, sep="\t", index=False)

print(f"✅ Merged table saved successfully:\n{output_path}")
print(f"📊 Shape: {merged_df.shape[0]} taxa × {merged_df.shape[1]-1} samples")
print("🎉 Merging complete!")