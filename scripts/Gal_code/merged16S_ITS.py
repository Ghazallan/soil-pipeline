import os
import pandas as pd
import glob
from functools import reduce

# === 1. Input folder (where per-site merged CSVs are stored) ===
folder = r"C:\Users\hadis\OneDrive\Documents\Project\soil Biodiversity\NEON data\Neon_Taxon"

# === 2. Output paths ===
output_16S = os.path.join(folder, "NEON_AllSites_16S_OuterMerged.csv")
output_ITS = os.path.join(folder, "NEON_AllSites_ITS_OuterMerged.csv")

# === 3. Helper function for outer merge ===
def outer_merge_csvs(file_list, output_file, key_column="taxonID"):
    """Merge a list of CSVs by outer join along the given key column."""
    if not file_list:
        print(f"⚠️ No files found for {output_file}")
        return

    dfs = []
    for file in file_list:
        name = os.path.splitext(os.path.basename(file))[0]  # e.g., WOOD_2020_16S
        try:
            df = pd.read_csv(file)
        except Exception:
            df = pd.read_csv(file, sep="\t", engine="python")

        # Try to identify a shared key column
        if key_column not in df.columns:
            # Try possible NEON taxon keys
            possible_keys = [c for c in df.columns if "taxon" in c.lower() or "id" in c.lower()]
            if possible_keys:
                key_column = possible_keys[0]
            else:
                df.reset_index(inplace=True)
                df.rename(columns={"index": "taxonID"}, inplace=True)
                key_column = "taxonID"

        # Rename value columns to include site name prefix
        value_cols = [c for c in df.columns if c != key_column]
        df = df[[key_column] + value_cols]
        df = df.add_prefix(f"{name}_")
        df.rename(columns={f"{name}_{key_column}": key_column}, inplace=True)
        dfs.append(df)
        print(f"  ✅ Added {os.path.basename(file)} ({len(df)} rows)")

    # Merge all files outer on the key column
    merged_df = reduce(lambda left, right: pd.merge(left, right, on=key_column, how="outer"), dfs)
    merged_df.to_csv(output_file, index=False)
    print(f"📁 Saved outer-merged file → {output_file}")
    print(f"📊 Final shape: {merged_df.shape}")

# === 4. Locate all 16S and ITS files ===
files_16S = glob.glob(os.path.join(folder, "*_16S.csv"))
files_ITS = glob.glob(os.path.join(folder, "*_ITS.csv"))

print(f"🔍 Found {len(files_16S)} 16S and {len(files_ITS)} ITS files")

# === 5. Perform outer merges ===
outer_merge_csvs(files_16S, output_16S)
outer_merge_csvs(files_ITS, output_ITS)

print("\n🎉 Done! All 16S and ITS files merged by outer join.")
# === End of script ===