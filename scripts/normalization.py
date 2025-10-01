#!/usr/bin/env python3
import pandas as pd
import numpy as np
import argparse
from skbio.stats.composition import clr
from biom import load_table
from biom.util import biom_open
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

# Enable pandas-to-R conversion
pandas2ri.activate()

def load_data(input_file):
    """Load TSV file (HUMAnN/Kraken output) into a pandas DataFrame."""
    df = pd.read_csv(input_file, sep='\t', index_col=0)
    return df

def normalize_clr(df):
    """Centered Log-Ratio (CLR) normalization using scikit-bio."""
    df_clr = pd.DataFrame(
        clr(df + 1),  # Add pseudocount to avoid zeros
        index=df.index,
        columns=df.columns
    )
    return df_clr

def normalize_css(df):
    """Cumulative Sum Scaling (CSS) via metagenomeSeq (R)."""
    # Convert to BIOM format (required by metagenomeSeq)
    biom_table = biom.Table(df.values, observation_ids=df.index, sample_ids=df.columns)
    with biom_open("temp.biom", 'w') as f:
        biom_table.to_hdf5(f, "temp.biom")
    
    # Run CSS in R
    r = ro.r
    r('library(metagenomeSeq)')
    r('library(biomformat)')
    r(f'biom_data <- read_biom("temp.biom")')
    r('css_data <- metagenomeSeq::newMRexperiment(biom_data@otu_table@.Data)')
    r('css_norm <- metagenomeSeq::cumNorm(css_data)')
    r('css_mat <- metagenomeSeq::MRcounts(css_norm, norm=TRUE)')
    css_df = r('css_mat')
    return pd.DataFrame(css_df, index=df.index, columns=df.columns)

def normalize_deseq2(df):
    """DESeq2 Variance-Stabilizing Transformation (VST)."""
    r = ro.r
    r('library(DESeq2)')
    r('library(phyloseq)')
    # Convert to DESeq2 object
    pandas2ri.activate()
    r_df = pandas2ri.py2rpy(df)
    r('dds <- DESeqDataSetFromMatrix(countData = r_df, colData = data.frame(sample=colnames(r_df)), design = ~ 1)')
    r('dds <- estimateSizeFactors(dds)')
    r('vst_data <- varianceStabilizingTransformation(dds)')
    vst_df = r('assay(vst_data)')
    return pd.DataFrame(vst_df, index=df.index, columns=df.columns)

def main():
    parser = argparse.ArgumentParser(description="Normalize metagenomic count data.")
    parser.add_argument("--input", required=True, help="Input TSV file (e.g., HUMAnN/Kraken output)")
    parser.add_argument("--output", required=True, help="Output normalized TSV file")
    parser.add_argument("--method", choices=["clr", "css", "deseq2"], default="clr", help="Normalization method")
    args = parser.parse_args()

    df = load_data(args.input)
    
    if args.method == "clr":
        norm_df = normalize_clr(df)
    elif args.method == "css":
        norm_df = normalize_css(df)
    elif args.method == "deseq2":
        norm_df = normalize_deseq2(df)
    
    norm_df.to_csv(args.output, sep='\t')

if __name__ == "__main__":
    main()