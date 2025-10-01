import pandas as pd
import requests
import os

# ------------------------------
# Step 1: Load metadata
# ------------------------------

metadata_file = "/home/hadis/soil_microbiome/data/neon_data/NEON_2022_raw_file_URLs.csv"
df = pd.read_csv(metadata_file)

# Ensure startDate is datetime
df["startDate"] = pd.to_datetime(df["startDate"])

# ------------------------------
# Step 2: Sample one dnaSampleCode per site
# ------------------------------

# Get unique site-level combinations (ignoring file-specific rows)
unique_samples = (
    df[["domainID", "siteID", "startDate", "dnaSampleCode"]]
      .drop_duplicates()
      .groupby("siteID")
      .first()   # pick the first dnaSampleCode per site (deterministic)
      .reset_index()
)

# Filter original df to keep *all rows* (all files) for those sampled dnaSampleCodes
df_sampled = df.merge(unique_samples, on=["domainID", "siteID", "startDate", "dnaSampleCode"])

# Save sampled metadata (still contains all columns)
sampled_metadata_file = "/home/hadis/soil_microbiome/data/neon_data/sample_per_site.csv"
df_sampled.to_csv(sampled_metadata_file, index=False)

print(f"✅ Sampling complete. Saved: {sampled_metadata_file}")
print(f"Rows in sampled set: {len(df_sampled)}")
print("👉 Columns kept:", df_sampled.columns.tolist())

# ------------------------------
# Step 3: Download all files for sampled rows
# ------------------------------

download_dir = "/home/hadis/soil_microbiome/data/neon_data"
os.makedirs(download_dir, exist_ok=True)

print(f"\n🔽 Starting downloads of {len(df_sampled)} files...")

for i, row in df_sampled.iterrows():
    url = row["rawDataFilePath"]

    try:
        # Get prefix from dnaSampleID (everything before first "-")
        sample_prefix = str(row["dnaSampleID"]).split("-")[0]

        # Extract read direction (R1 or R2) from description
        desc = str(row["rawDataFileDescription"])
        if "R1" in desc:
            read_suffix = "R1"
        elif "R2" in desc:
            read_suffix = "R2"
        else:
            read_suffix = "UNK"

        # Build filename
        filename = f"{sample_prefix}_{read_suffix}.fastq.gz"
        save_path = os.path.join(download_dir, filename)

        # ✅ Skip if already exists
        if os.path.exists(save_path):
            print(f"⏩ Skipping (already exists): {filename}")
            continue

        # Download if not exists
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"✅ Downloaded: {filename}")

    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")

print("🎉 All downloads complete.")