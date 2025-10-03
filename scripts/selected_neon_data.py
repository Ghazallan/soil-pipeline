import pandas as pd
import requests
import os

# ------------------------------
# Step 1: Load metadata
# ------------------------------

metadata_file = r"C:\Users\hadis\OneDrive\Documents\Project\soil Biodiversity\NEON data\NEON_2022_raw_file_URLs.csv"
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
sampled_metadata_file = r"C:\Users\hadis\OneDrive\Documents\Project\soil Biodiversity\NEON data\sample_per_site.csv"
df_sampled.to_csv(sampled_metadata_file, index=False)

print(f"✅ Sampling complete. Saved: {sampled_metadata_file}")
print(f"Rows in sampled set: {len(df_sampled)}")
print("👉 Columns kept:", df_sampled.columns.tolist())

