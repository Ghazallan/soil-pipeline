import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Input JSON files from Snakemake
json_files = snakemake.input.jsons

records = []
for filepath in json_files:
    with open(filepath) as f:
        data = json.load(f)
        sample = os.path.basename(filepath).replace("_fastp.json", "")
        before = data["summary"]["before_filtering"]
        after = data["summary"]["after_filtering"]

        records.append({
            "sample": sample,
            "bases_before": before["total_bases"],
            "bases_after": after["total_bases"],
            "q20_before": before["q20_rate"] * 100,
            "q30_before": before["q30_rate"] * 100,
            "q20_after": after["q20_rate"] * 100,
            "q30_after": after["q30_rate"] * 100,
        })

df = pd.DataFrame(records)
df_sorted = df.sort_values("bases_before", ascending=False)
df.to_csv(snakemake.output.csv, index=False)

# Plot 1: Stacked base pair bar plot
plt.figure(figsize=(10, 6))
plt.barh(df_sorted["sample"], df_sorted["bases_before"], color="#00BCD4", label="Pre-filtering")
plt.barh(df_sorted["sample"], df_sorted["bases_after"], color="#F44336", label="Post-filtering")
plt.xlabel("Base pairs")
plt.ylabel("Sample")
plt.title("Raw read QC summary stacked bar plot")
plt.legend()
plt.tight_layout()
plt.savefig(snakemake.output.plot1)

# Plot 2: Q20/Q30 KDEs
fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
sns.kdeplot(df["q30_before"], fill=True, ax=axs[0], label="Q30", color="gray")
sns.kdeplot(df["q20_before"], fill=True, ax=axs[0], label="Q20", color="black")
axs[0].set_title("Base Quality (Pre-filter)")
axs[0].legend()

sns.kdeplot(df["q30_after"], fill=True, ax=axs[1], label="Q30", color="gray")
sns.kdeplot(df["q20_after"], fill=True, ax=axs[1], label="Q20", color="black")
axs[1].set_title("Base Quality (Post-filter)")
axs[1].set_xlabel("Percentage of high-quality bases")
axs[1].legend()

plt.tight_layout()
plt.savefig(snakemake.output.plot2)