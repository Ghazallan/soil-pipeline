#!/bin/bash
#SBATCH --account=def-yourpi
#SBATCH --time=2-00:00              # 2 days
#SBATCH --mem=64G
#SBATCH --cpus-per-task=16
#SBATCH --job-name=megahit_multi
#SBATCH --output=megahit_multi_%j.out

module load megahit/1.2.9

# Loop through all samples with R1 fastq
for R1 in *_R1.fastq; do
    # Derive sample name (everything before "_R1")
    SAMPLE=$(basename "$R1" _R1.fastq)
    R2="${SAMPLE}_R2.fastq"

    echo "Running MEGAHIT for sample: $SAMPLE"

    megahit \
        -1 "$R1" \
        -2 "$R2" \
        -o "megahit_${SAMPLE}" \
        --num-cpu-threads $SLURM_CPUS_PER_TASK
done
echo "All MEGAHIT jobs completed."