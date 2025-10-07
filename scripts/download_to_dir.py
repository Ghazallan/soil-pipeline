import pandas as pd
import requests
import os

# ------------------------------
# Step 3: Download all files for sampled rows
# ------------------------------

# Path to sampled metadata CSV in $PROJECT
sampled_metadata_file = "/home/hazad25/projects/sample_per_site.csv"
df_sampled = pd.read_csv(sampled_metadata_file)

# Directory to save downloaded files in $PROJECT
download_neon_dir = "/project/def-yuezhang/hazad25/project/neon_data"
os.makedirs(download_neon_dir, exist_ok=True)

print(f"\n🔽 Starting downloads of {len(df_sampled)} files...")

for i, row in df_sampled.iterrows():
    url = row["rawDataFilePath"]

    try:
        sample_prefix = str(row["dnaSampleID"]).split("-")[0]
        desc = str(row["rawDataFileDescription"])
        if "R1" in desc:
            read_suffix = "R1"
        elif "R2" in desc:
            read_suffix = "R2"
        else:
            read_suffix = "UNK"

        filename = f"{sample_prefix}_{read_suffix}.fastq.gz"
        save_path = os.path.join(download_neon_dir, filename)

        if os.path.exists(save_path):
            print(f"⏩ Skipping (already exists): {filename}")
            continue

        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"✅ Downloaded: {filename}")

    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")

print("🎉 All downloads complete.")
