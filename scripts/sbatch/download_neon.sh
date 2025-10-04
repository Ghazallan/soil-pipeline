#!/bin/bash
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --job-name=neon_download
#SBATCH --output=%x_%j.out

module load python/3.10

# Activate your virtual env if needed
# source ~/ENV/bin/activate

python download_to_dir.py
