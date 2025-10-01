#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from umap import UMAP
from skbio.stats.ordination import nmds
import argparse
import os

def load_and_combine_data(file_list):
    """Load and combine multiple normalized sample files"""
    dfs = []
    for f in file_list:
        sample_name = os.path.basename(f).replace('_normalized.tsv', '')
        df = pd.read_csv(f, sep='\t', index_col=0)
        df.columns = [f"{sample_name}_{col}" for col in df.columns]
        dfs.append(df.T)
    
    combined = pd.concat(dfs)
    return combined.fillna(0)

def perform_pca(data, n_components=2):
    """Perform PCA dimensionality reduction"""
    pca = PCA(n_components=n_components)
    pca_results = pca.fit_transform(data)
    return pca_results, pca.explained_variance_ratio_

def perform_tsne(data, n_components=2, perplexity=30):
    """Perform t-SNE dimensionality reduction"""
    tsne = TSNE(n_components=n_components, perplexity=perplexity)
    return tsne.fit_transform(data)

def perform_umap(data, n_components=2, n_neighbors=15):
    """Perform UMAP dimensionality reduction"""
    umap = UMAP(n_components=n_components, n_neighbors=n_neighbors)
    return umap.fit_transform(data)

def perform_nmds(data, n_components=2):
    """Perform NMDS dimensionality reduction"""
    # Convert to distance matrix (Bray-Curtis)
    from skbio.diversity import beta_diversity
    from skbio.stats.distance import DistanceMatrix
    bc_dm = beta_diversity("braycurtis", data.values, ids=data.index)
    nmds_results = nmds(bc_dm, n_components=n_components)
    return nmds_results.samples.values

def plot_results(results_dict, output_file):
    """Create multi-panel visualization of all clustering results"""
    methods = list(results_dict.keys())
    n_methods = len(methods)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.ravel()
    
    for i, method in enumerate(methods):
        ax = axes[i]
        data = results_dict[method]
        
        if isinstance(data, tuple):  # PCA case with variance explained
            coords, var_exp = data
            ax.scatter(coords[:, 0], coords[:, 1], alpha=0.7)
            ax.set_xlabel(f'PC1 ({var_exp[0]*100:.1f}%)')
            ax.set_ylabel(f'PC2 ({var_exp[1]*100:.1f}%)')
        else:
            ax.scatter(data[:, 0], data[:, 1], alpha=0.7)
            ax.set_xlabel(f'{method}1')
            ax.set_ylabel(f'{method}2')
        
        ax.set_title(method.upper())
        ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Perform clustering analysis')
    parser.add_argument('--input', nargs='+', required=True, help='Input normalized TSV files')
    parser.add_argument('--output', required=True, help='Output PDF file for plots')
    args = parser.parse_args()

    # Load and combine data
    combined_data = load_and_combine_data(args.input)
    
    # Perform all clustering methods
    results = {
        'PCA': perform_pca(combined_data),
        't-SNE': perform_tsne(combined_data),
        'UMAP': perform_umap(combined_data),
        'NMDS': perform_nmds(combined_data)
    }
    
    # Generate visualization
    plot_results(results, args.output)

if __name__ == '__main__':
    main()