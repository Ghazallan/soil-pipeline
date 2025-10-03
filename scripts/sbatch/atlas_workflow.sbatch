#!/bin/bash
#SBATCH --account=def_YOURPI
#SBATCH --job-name=atlas_all
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G
#SBATCH --time=5-00:00:00
#SBATCH --output=%x-%j.out

set -euo pipefail

# --- Load modules ---
module purge
module load StdEnv/2020 intel/2020.1.217
module load python/3.10
module load metagenome-atlas/2.5.0

# --- Set paths ---
export ATLAS_WORKDIR=$SCRATCH/atlas_raw_sample
export ATLAS_DBDIR=$SCRATCH/atlas_db
export CONDA_PKGS_DIRS=$SLURM_TMPDIR/conda_pkgs
mkdir -p $CONDA_PKGS_DIRS

# --- Run atlas workflow ---
atlas run all -w $ATLAS_WORKDIR -j $SLURM_CPUS_PER_TASK
