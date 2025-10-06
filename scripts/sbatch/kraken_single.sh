#!/bin/bash
#SBATCH --job-name=kraken2_run
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=kraken2_%j.out
#SBATCH --error=kraken2_%j.err

module load kraken2/2.1.3
export KRAKEN_DB=/project/def-yuezhang/hazad25/project/database/kraken2_db

kraken2 \
  --db $KRAKEN_DB \
  --threads 16 \
  --report sample.report \
  --output sample.kraken \
  sample_R1.fastq.gz sample_R2.fastq.gz
