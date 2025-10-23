import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from skbio.diversity import beta_diversity
from skbio.stats.ordination import pcoa


# ---------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------
file_path = r"C:\Users\hadis\OneDrive\Documents\Project\Ga_output\MetaphlanOutput.rocrate\relative_abundances\merged_metaphlan_genus_level.tsv"
out_dir = r"C:\Users\hadis\OneDrive\Documents\Project\Soil_Pipeline\soil-pipeline\Metaphlan_Exploratory_Analysis"
os.makedirs(out_dir, exist_ok=True)

# Load data
df = pd.read_csv(file_path, sep="\t", index_col=0)
print("✅ Data loaded successfully!")
print(f"Shape: {df.shape} (taxa × samples)")

# ---------------------------------------------------------------------
# Basic summaries
# ---------------------------------------------------------------------
print("\n--- Basic Summary ---")
print(df.describe())

sample_sums = df.sum(axis=0)
print("\n--- Total abundance per sample ---")
print(sample_sums.head())

mean_abundance = df.mean(axis=1).sort_values(ascending=False)
print("\n--- Top 10 taxa ---")
print(mean_abundance.head(10))

# Helper to save figures
def save_fig(name):
    plt.tight_layout()
    path = os.path.join(out_dir, f"{name}.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"📁 Saved: {path}")

# ---------------------------------------------------------------------
# Visualization (each figure saved separately)
# ---------------------------------------------------------------------

# Histogram of relative abundances
plt.figure(figsize=(8, 6))
plt.hist(df.values.flatten(), bins=50, color='skyblue', edgecolor='black')
plt.yscale('log')
plt.xlabel('Relative Abundance')
plt.ylabel('Frequency (log scale)')
plt.title('Histogram of Relative Abundances')
save_fig("abundance_histogram")

# Boxplot of sample distributions
plt.figure(figsize=(8, 6))
plt.boxplot(df.values, vert=False)
plt.xlabel('Relative Abundance')
plt.title('Boxplot of Sample Distributions')
plt.grid(True)
save_fig("sample_boxplot")

# Distribution of mean genus abundance (log10)
plt.figure(figsize=(8, 6))
plt.hist(np.log10(mean_abundance + 1e-6), bins=50, color='lightgreen')
plt.title("Distribution of Mean Genus Abundance (log10)")
plt.xlabel("log10(mean abundance + 1e-6)")
plt.ylabel("Count of genera")
save_fig("mean_genus_abundance_distribution")

# Top 10 most abundant genera
top10 = mean_abundance.head(10)
plt.figure(figsize=(8, 6))
plt.barh(top10.index[::-1], top10.values[::-1], color='teal')
plt.title("Top 10 Most Abundant Genera")
plt.xlabel("Mean Relative Abundance (%)")
save_fig("top10_genera")

# Correlation heatmap between samples
plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(), cmap='coolwarm', center=0)
plt.title("Sample Correlation Heatmap")
save_fig("sample_correlation_heatmap")

# ---------------------------------------------------------------------
# Alpha diversity
# ---------------------------------------------------------------------
rel = df.div(df.sum(axis=0), axis=1)
richness = (rel > 0).sum(axis=0)
shannon = - (rel * np.log(rel + 1e-12)).sum(axis=0)

plt.figure(figsize=(8, 6))
plt.hist(richness, bins=20, color='skyblue')
plt.title("Sample Richness (# taxa present)")
plt.xlabel("Richness")
plt.ylabel("Count of Samples")
save_fig("alpha_richness")

plt.figure(figsize=(8, 6))
plt.hist(shannon, bins=20, color='orange')
plt.title("Shannon Diversity Index")
plt.xlabel("Shannon Index")
plt.ylabel("Count of Samples")
save_fig("alpha_shannon")

# ---------------------------------------------------------------------
# PCA (beta diversity)
# ---------------------------------------------------------------------
X = df.T.fillna(0)
X_scaled = StandardScaler().fit_transform(X)
pca = PCA(n_components=2)
coords = pca.fit_transform(X_scaled)
plt.figure(figsize=(6, 6))
plt.scatter(coords[:, 0], coords[:, 1], color='steelblue')
plt.title("PCA of Genus-Level Abundances")
plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% var)")
plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% var)")
plt.grid(True)
save_fig("pca_beta_diversity")

# ---------------------------------------------------------------------
# Rank–abundance curve
# ---------------------------------------------------------------------
plt.figure(figsize=(6, 5))
plt.plot(range(1, len(mean_abundance) + 1), mean_abundance.values, color='darkred')
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Taxon Rank")
plt.ylabel("Mean Abundance")
plt.title("Rank–Abundance Curve")
save_fig("rank_abundance_curve")

# ---------------------------------------------------------------------
# Stacked barplot of top 10 genera
# ---------------------------------------------------------------------
top10 = df.mean(axis=1).sort_values(ascending=False).head(10).index
plot_df = df.copy()
plot_df.loc[~df.index.isin(top10)] = np.nan
plot_df = plot_df.fillna(0)
plot_df.loc["Other"] = 100 - plot_df.sum()
plot_df.T.plot(kind='bar', stacked=True, figsize=(12, 6))
plt.title("Stacked Barplot of Top 10 Genera per Sample")
plt.ylabel("Relative Abundance (%)")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Genus")
save_fig("stacked_barplot_top10")

# ---------------------------------------------------------------------
# Heatmap (taxa vs samples)
# ---------------------------------------------------------------------
sns.clustermap(np.log10(df + 1e-5), cmap="viridis", figsize=(10, 8))
plt.savefig(os.path.join(out_dir, "heatmap_clustermap.png"), dpi=300, bbox_inches='tight')
plt.close()
print("📁 Saved: heatmap_clustermap.png")

# ---------------------------------------------------------------------
# Bray–Curtis PCoA
# ---------------------------------------------------------------------
bc = beta_diversity("braycurtis", df.T.values, ids=df.columns)
pcoa_res = pcoa(bc)
plt.figure(figsize=(6, 6))
plt.scatter(pcoa_res.samples['PC1'], pcoa_res.samples['PC2'], color='purple')
plt.xlabel(f"PC1 ({pcoa_res.proportion_explained[0]*100:.1f}% var)")
plt.ylabel(f"PC2 ({pcoa_res.proportion_explained[1]*100:.1f}% var)")
plt.title("PCoA Based on Bray–Curtis Distances")
plt.grid(True)
save_fig("pcoa_braycurtis")

# ---------------------------------------------------------------------
# Co-occurrence network (safe)
# ---------------------------------------------------------------------
corr = df.T.corr()
corr.columns = [f"Sample_{i}" for i in range(corr.shape[1])]
corr.index = corr.columns

edges = corr.stack().reset_index()
edges.columns = ['Taxon1', 'Taxon2', 'Correlation']
edges = edges.query("0.7 < Correlation < 1 and Taxon1 != Taxon2")

if not edges.empty:
    G = nx.from_pandas_edgelist(edges, 'Taxon1', 'Taxon2', ['Correlation'])
    plt.figure(figsize=(8, 8))
    nx.draw_networkx(G, node_size=100, with_labels=False)
    plt.title("Co-occurrence Network (r > 0.7)")
    save_fig("cooccurrence_network")
else:
    print("⚠️ No strong correlations found (r > 0.7) — skipping network plot.")

# ---------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------
print("\n--- Summary Statistics ---")
print(f"Number of samples: {df.shape[1]}")
print(f"Number of genera: {df.shape[0]}")
print(f"Average richness (genera/sample): {richness.mean():.1f} ± {richness.std():.1f}")
print(f"Average Shannon diversity (sample): {shannon.mean():.2f} ± {shannon.std():.2f}")
print(f"Explained variance by PC1+PC2: {pca.explained_variance_ratio_[:2].sum()*100:.1f}%")
print("\n🎉 Exploratory analysis complete!")
print(f"All figures saved in: {out_dir}")
