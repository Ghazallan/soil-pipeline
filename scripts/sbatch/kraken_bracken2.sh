#!/bin/bash
#SBATCH --job-name=kraken_multi
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=kraken_%A_%a.out
#SBATCH --error=kraken_%A_%a.err
#SBATCH --array=1-2   # <-- fixed number of samples

module load StdEnv/2023
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

echo "[$(date)] Starting analysis for sample: ${SAMPLE}"
echo "Input reads:"
echo "  R1: $R1"
echo "  R2: $R2"
echo "Output directory: $OUT_DIR"
echo "Kraken database: $KRAKEN_DB"
echo "---------------------------------------------------------"

# =========================================================
# Run Kraken2
# =========================================================
echo "[$(date)] Running Kraken2 for ${SAMPLE}..."
kraken2 \
  --db "$KRAKEN_DB" \
  --threads $SLURM_CPUS_PER_TASK \
  --use-names \
  --report-zero-counts \
  --report "${OUT_DIR}/${SAMPLE}.kraken_report" \
  --output "${OUT_DIR}/${SAMPLE}.kraken_output" \
  "$R1" "$R2"

if [[ $? -ne 0 ]]; then
  echo "[$(date)] ERROR: Kraken2 failed for ${SAMPLE}"
  exit 1
fi
echo "[$(date)] Kraken2 completed successfully for ${SAMPLE}"
echo "---------------------------------------------------------"

# =========================================================
# Run Bracken
# =========================================================
echo "[$(date)] Running Bracken for ${SAMPLE}..."
bracken \
  -d "$KRAKEN_DB" \
  -i "${OUT_DIR}/${SAMPLE}.kraken_report" \
  -o "${OUT_DIR}/${SAMPLE}.bracken_report" \
  -r 150 -l S -t $SLURM_CPUS_PER_TASK

if [[ $? -ne 0 ]]; then
  echo "[$(date)] ERROR: Bracken failed for ${SAMPLE}"
  exit 1
fi
echo "[$(date)] Bracken completed successfully for ${SAMPLE}"
echo "---------------------------------------------------------"

# =========================================================
# If this is the last job in the array, combine all Bracken outputs
# =========================================================
if [[ $SLURM_ARRAY_TASK_ID -eq ${#SAMPLES[@]} ]]; then
  echo "[$(date)] Combining Bracken reports into abundance matrix..."
  cd "$OUT_DIR"

  # Clean up old combined files
  rm -f bracken_abundance_matrix.tsv

  # Combine all *.bracken_report into one matrix
  bracken_combine_outputs.py --files *.bracken_report -o bracken_abundance_matrix.tsv

  if [[ $? -eq 0 ]]; then
    echo "[$(date)] Combined abundance matrix created: ${OUT_DIR}/bracken_abundance_matrix.tsv"
  else
    echo "[$(date)] WARNING: Failed to combine Bracken outputs."
  fi
fi

echo "[$(date)] Finished processing sample: ${SAMPLE}"