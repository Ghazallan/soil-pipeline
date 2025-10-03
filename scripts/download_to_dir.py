import pandas as pd
import requests
import os

# ------------------------------
# Step 3: Download all files for sampled rows
# ------------------------------

# Path to sampled metadata CSV (created in Step 2)
sampled_metadata_file = r"C:\Users\hadis\OneDrive\Documents\Project\soil Biodiversity\NEON data\sample_per_site.csv"

# Load sampled metadata
df_sampled = pd.read_csv(sampled_metadata_file)

# Directory to save downloaded files
download_neon_dir = "/home/hadis/soil_microbiome/data/neon_data"
os.makedirs(download_neon_dir, exist_ok=True)

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
        save_path = os.path.join(download_neon_dir, filename)

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
# Note: If you encounter issues with large files, consider using tools like wget or curl for more robust downloading.