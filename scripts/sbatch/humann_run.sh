#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# --- Step 1: Create and activate a conda environment ---
echo "Creating HUMAnN environment..."
conda create -n humann4 -y python=3.9
conda activate humann4

# --- Step 2: Install dependencies ---
echo "Installing HUMAnN and dependencies..."
conda install -c bioconda -c conda-forge humann metaphlan bowtie2 diamond -y

# --- Step 3: Download databases (optional but recommended) ---
# You can specify a custom directory for databases
DB_DIR=~/humann_db
mkdir -p $DB_DIR

# Download CHOCOPhlAn (nucleotide) database
echo "Downloading CHOCOPhlAn database..."
humann_databases --download chocophlan full $DB_DIR

# Download UniRef (protein) database
echo "Downloading UniRef90 database..."
humann_databases --download uniref uniref90_diamond $DB_DIR

# --- Step 4: Run HUMAnN ---
# Example usage: bash humann_run.sh sample.fastq.gz output_folder/
INPUT_FASTQ=$1
OUTPUT_DIR=$2

if [ -z "$INPUT_FASTQ" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: bash humann_run.sh <input.fastq.gz> <output_dir>"
    exit 1
fi

mkdir -p $OUTPUT_DIR

echo "Running HUMAnN on $INPUT_FASTQ ..."
humann \
    --input $INPUT_FASTQ \
    --output $OUTPUT_DIR \
    --metaphlan-options "--bowtie2db $DB_DIR/chocophlan" \
    --nucleotide-database $DB_DIR/chocophlan \
    --protein-database $DB_DIR/uniref90_diamond

echo "✅ HUMAnN analysis complete!"
echo "Results saved to: $OUTPUT_DIR"
#SBATCH --job-name=humann_run
#SBATCH --cpus-per-task=16
#SBATCH --mem=100G
#SBATCH --time=12:00:00