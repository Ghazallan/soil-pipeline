#!/bin/bash
#SBATCH --account=def-yourpi        # Replace with your PI's account
#SBATCH --time=1-00:00              # 1 day
#SBATCH --mem=64G                   # memory
#SBATCH --cpus-per-task=16          # number of threads
#SBATCH --job-name=megahit_job
#SBATCH --output=megahit_%j.out

module load megahit/1.2.9

# Run MEGAHIT on paired-end reads
megahit \
    -1 R1.fastq \
    -2 R2.fastq \
    -o megahit_output \
    --num-cpu-threads $SLURM_CPUS_PER_TASK
