#!/bin/bash
#SBATCH --job-name=kraken_bracken_multi
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=kraken_%A_%a.out
#SBATCH --error=kraken_%A_%a.err
#SBATCH --array=1-2   # <-- set number of samples or auto-detect later

# =========================================================
#   Kraken2 + Bracken multi-sample pipeline (SLURM)
#   Author: <Your Name>
#   Date: $(date +%Y-%m-%d)
#   Description:
#     Runs Kraken2 classification and Bracken abundance estimation
#     across multiple metagenomic samples in an HPC environment.
# =========================================================

# ----------------------------
# 1. Load required modules
# ----------------------------
module load StdEnv/2023
module load kraken2/2.1.3
module load bracken/3.0

# ----------------------------
# 2. Define paths
# ----------------------------
export KRAKEN_DB=/project/def-yuezhang/hazad25/project/database/kraken2_db
DATA_DIR=/project/def-yuezhang/hazad25/project/raw_sample
OUT_DIR=/project/def-yuezhang/hazad25/project/results

mkdir -p "$OUT_DIR"

# ----------------------------
# 3. Define samples
# ----------------------------
# List of sample base names (without _R1/_R2)
SAMPLES=("SCBI_012" "WOOD_002")
SAMPLE=${SAMPLES[$((SLURM_ARRAY_TASK_ID-1))]}

# Input FASTQ files
R1=${DATA_DIR}/${SAMPLE}_R1.fastq
R2=${DATA_DIR}/${SAMPLE}_R2.fastq

echo "========================================================="
echo "[$(date)] Starting Kraken2 + Bracken for sample: ${SAMPLE}"
echo "Input files:"
echo "  R1: $R1"
echo "  R2: $R2"
echo "Database: $KRAKEN_DB"
echo "Output directory: $OUT_DIR"
echo "========================================================="

# =========================================================
# 4. Run Kraken2
# =========================================================
echo "[$(date)] Running Kraken2..."
kraken2 \
  --db "$KRAKEN_DB" \
  --threads $SLURM_CPUS_PER_TASK \
  --use-names \
  --report "${OUT_DIR}/${SAMPLE}.kraken_report" \
  --output "${OUT_DIR}/${SAMPLE}.kraken_output" \
  "$R1" "$R2"

if [[ $? -ne 0 ]]; then
  echo "[$(date)] ERROR: Kraken2 failed for ${SAMPLE}" >&2
  exit 1
fi

echo "[$(date)] Kraken2 completed successfully for ${SAMPLE}"
echo "---------------------------------------------------------"

# =========================================================
# 5. Amend Kraken report (tab-delimited format for Bracken)
# =========================================================
echo "[$(date)] Reformatting Kraken report..."
awk '{$1=$1}1' OFS='\t' "${OUT_DIR}/${SAMPLE}.kraken_report" > "${OUT_DIR}/${SAMPLE}_amend.report"

if [[ $? -ne 0 ]]; then
  echo "[$(date)] ERROR: Failed to create amended report" >&2
  exit 1
fi

echo "[$(date)] Amended report created: ${OUT_DIR}/${SAMPLE}_amend.report"
echo "---------------------------------------------------------"

# =========================================================
# 6. Run Bracken
# =========================================================
echo "[$(date)] Running Bracken..."
bracken \
  -d "$KRAKEN_DB" \
  -i "${OUT_DIR}/${SAMPLE}_amend.report" \
  -o "${OUT_DIR}/${SAMPLE}.bracken_report" \
  -r 150 -l S -t $SLURM_CPUS_PER_TASK

if [[ $? -ne 0 ]]; then
  echo "[$(date)] ERROR: Bracken failed for ${SAMPLE}" >&2
  exit 1
fi

echo "[$(date)] Bracken completed successfully for ${SAMPLE}"
echo "Output file: ${OUT_DIR}/${SAMPLE}.bracken_report"
echo "---------------------------------------------------------"

# =========================================================
# 7. Combine results (only once after last job)
# =========================================================
if [[ $SLURM_ARRAY_TASK_ID -eq ${#SAMPLES[@]} ]]; then
  echo "[$(date)] Combining Bracken reports into abundance matrix..."
  cd "$OUT_DIR"

  rm -f bracken_abundance_matrix.tsv
  bracken_combine_outputs.py --files *.bracken_report -o bracken_abundance_matrix.tsv

  if [[ $? -eq 0 ]]; then
    echo "[$(date)] Combined abundance matrix created:"
    echo "  ${OUT_DIR}/bracken_abundance_matrix.tsv"
  else
    echo "[$(date)] WARNING: Failed to combine Bracken outputs." >&2
  fi
fi

echo "[$(date)] Finished processing sample: ${SAMPLE}"
echo "========================================================="
# End of scripts/sbatch/kraken_bracken2.sh