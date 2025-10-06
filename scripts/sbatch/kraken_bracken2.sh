#!/bin/bash
#SBATCH --job-name=kraken_multi
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=kraken_%A_%a.out
#SBATCH --error=kraken_%A_%a.err
#SBATCH --array=1-$(ls /project/def-yuezhang/hazad25/project/raw_sample/*_R1.fastq.gz | wc -l)

module load kraken2/2.1.3
module load bracken/3.0

# Paths
export KRAKEN_DB=/project/def-yuezhang/hazad25/project/database/kraken2_db
DATA_DIR=/project/def-yuezhang/hazad25/project/raw_sample
OUT_DIR=/project/def-yuezhang/hazad25/project/results

mkdir -p $OUT_DIR

# Generate sample list dynamically (once per job)
SAMPLE_LIST=($(ls ${DATA_DIR}/*_R1.fastq.gz | sed 's/_R1.fastq.gz//' | xargs -n1 basename))
SAMPLE=${SAMPLE_LIST[$((SLURM_ARRAY_TASK_ID-1))]}

R1=${DATA_DIR}/${SAMPLE}_R1.fastq.gz
R2=${DATA_DIR}/${SAMPLE}_R2.fastq.gz

echo "[$(date)] Processing sample: ${SAMPLE}"
echo "R1: $R1"
echo "R2: $R2"

# Run Kraken2 classification
kraken2 \
  --db $KRAKEN_DB \
  --threads 16 \
  --report ${OUT_DIR}/${SAMPLE}.report \
  --output ${OUT_DIR}/${SAMPLE}.kraken \
  $R1 $R2

# Run Bracken abundance estimation
bracken \
  -d $KRAKEN_DB \
  -i ${OUT_DIR}/${SAMPLE}.report \
  -o ${OUT_DIR}/${SAMPLE}.bracken \
  -r 150 -l S

echo "[$(date)] Finished ${SAMPLE}"
