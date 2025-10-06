#!/bin/bash
#SBATCH --job-name=kraken_multi
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=kraken_%A_%a.out
#SBATCH --error=kraken_%A_%a.err
#SBATCH --array=1-2   # <-- fixed number of samples

module load kraken2/2.1.3
module load bracken/3.0

# ---- Paths ----
export KRAKEN_DB=/project/def-yuezhang/hazad25/project/database/kraken2_db
DATA_DIR=/project/def-yuezhang/hazad25/project/raw_sample
OUT_DIR=/project/def-yuezhang/hazad25/project/results

mkdir -p $OUT_DIR

# ---- Sample list ----
SAMPLES=("SCBI_012" "WOOD_002")
SAMPLE=${SAMPLES[$((SLURM_ARRAY_TASK_ID-1))]}

R1=${DATA_DIR}/${SAMPLE}_R1.fastq
R2=${DATA_DIR}/${SAMPLE}_R2.fastq

echo "[$(date)] Processing sample: ${SAMPLE}"
echo "Input reads: $R1 and $R2"

# ---- Run Kraken2 ----
kraken2 \
  --db $KRAKEN_DB \
  --threads 16 \
  --report ${OUT_DIR}/${SAMPLE}.report \
  --output ${OUT_DIR}/${SAMPLE}.kraken \
  $R1 $R2

# ---- Run Bracken ----
bracken \
  -d $KRAKEN_DB \
  -i ${OUT_DIR}/${SAMPLE}.report \
  -o ${OUT_DIR}/${SAMPLE}.bracken \
  -r 150 -l S

echo "[$(date)] Finished ${SAMPLE}"
