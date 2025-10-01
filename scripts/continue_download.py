import pandas as pd
import requests
import os

# ------------------------------
# Step 3: Download all files for sampled rows
# ------------------------------

# Load the sampled rows (already created in Step 1 & 2)
sampled_metadata_file = "/home/hadis/soil_microbiome/data/neon_data/sample_per_site.csv"
df_sampled = pd.read_csv(sampled_metadata_file)

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

        # Final filename
        filename = f"{sample_prefix}_{read_suffix}.fastq.gz"
        save_path = os.path.join(download_dir, filename)

        # ✅ Skip if already exists
        if os.path.exists(save_path):
            print(f"⏩ Skipping (already exists): {filename}")
            continue

        # Download if missing
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"✅ Downloaded: {filename}")

    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")

print("🎉 All downloads complete.")
