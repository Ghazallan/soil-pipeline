#!/bin/bash
#SBATCH --job-name=kraken_build
#SBATCH --cpus-per-task=16
#SBATCH --mem=200G
#SBATCH --time=1-00:00:00
#SBATCH --output=kraken_build.out
#SBATCH --error=kraken_build.err

module load kraken2/2.1.3

cd /project/def-yuezhang/hazad25/project/database/kraken2_db_new

kraken2-build --build --db . --threads 16
