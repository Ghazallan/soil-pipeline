import os
import pandas as pd

# --------------------------------------------------
# 1️⃣ Define directories
# --------------------------------------------------
input_dir = r"C:\Users\hadis\OneDrive\Documents\Project\Ga_output\MetaphlanOutput.rocrate\relative_abundances"
output_base = os.path.join(input_dir, "merged_metaphlan_outputs")

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

    try:
        df = pd.read_csv(file_path, sep="\t", comment="#", header=None)
    except Exception as e:
        print(f"⚠️ Skipping {file} due to read error: {e}")
        continue

    if df.shape[1] < 2:
        print(f"⚠️ Skipping {file}: not enough columns.")
        continue

    # Use first column as clade, second as abundance
    df = df.iloc[:, [0, 1]]
    df.columns = ["clade_name", "relative_abundance"]

    # Derive sample name
    sample_id = os.path.splitext(file)[0]
    df = df.rename(columns={"relative_abundance": sample_id})

    # Merge
    if merged_df.empty:
        merged_df = df
    else:
        merged_df = pd.merge(merged_df, df, on="clade_name", how="outer")

# --------------------------------------------------
# 4️⃣ Clean merged table
# --------------------------------------------------
merged_df = merged_df.fillna(0).sort_values("clade_name")

# --------------------------------------------------
# 5️⃣ Create one file per clade_name
# --------------------------------------------------
output_dir = os.path.join(input_dir, "merged_by_clade")
os.makedirs(output_dir, exist_ok=True)

for _, row in merged_df.iterrows():
    clade = row["clade_name"]

    # Sanitize filename (remove | and / etc.)
    safe_name = clade.replace("|", "_").replace("/", "_").replace(" ", "_")

    # Create DataFrame for this clade (one row = abundances across samples)
    clade_df = pd.DataFrame(row).T
    clade_df = clade_df.drop(columns=["clade_name"]).T
    clade_df.columns = ["relative_abundance"]
    clade_df.index.name = "sample_id"

    # Save TSV for each clade
    out_path = os.path.join(output_dir, f"{safe_name}.tsv")
    clade_df.to_csv(out_path, sep="\t")

print(f"✅ Created {len(merged_df)} individual files in:\n{output_dir}")
print("🎉 Merging complete!")

