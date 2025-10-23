#!/bin/bash

# Exit on error
set -e

# --- Step 1: Create and activate a conda environment ---
echo "Creating MetaPhlAn4 environment..."
conda create -n metaphlan4 -y python=3.9
conda activate metaphlan4

# --- Step 2: Install dependencies ---
echo "Installing dependencies..."
conda install -c bioconda -c conda-forge metaphlan bowtie2 -y

# --- Step 3: Download MetaPhlAn database (optional if not already present) ---
# Default location: ~/.conda/envs/metaphlan4/lib/python3.9/site-packages/metaphlan/metaphlan_databases/
# You can customize it below:
DB_DIR=~/metaphlan_db
mkdir -p $DB_DIR

echo "Downloading MetaPhlAn database..."
metaphlan --install --bowtie2db $DB_DIR

# --- Step 4: Run MetaPhlAn ---
# Example usage: bash metaphlan4_run.sh sample.fastq.gz output_profile.txt

INPUT_FASTQ=$1
OUTPUT_PROFILE=$2

if [ -z "$INPUT_FASTQ" ] || [ -z "$OUTPUT_PROFILE" ]; then
    echo "Usage: bash metaphlan4_run.sh <input.fastq.gz> <output_profile.txt>"
    exit 1
fi

echo "Running MetaPhlAn on $INPUT_FASTQ ..."
metaphlan $INPUT_FASTQ \
    --input_type fastq \
    --bowtie2db $DB_DIR \
    -o $OUTPUT_PROFILE

echo "✅ MetaPhlAn4 analysis complete!"
echo "Results saved to: $OUTPUT_PROFILE"
