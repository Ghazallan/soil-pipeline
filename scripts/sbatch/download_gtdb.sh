#!/bin/bash
# Create target directory if it doesn't exist
mkdir -p /project/def-yuezhang/hazad25/atlas_project/atlas_db/GTDB_V06
cd /project/def-yuezhang/hazad25/atlas_project/atlas_db/GTDB_V06

# Base GTDB URL
BASE_URL="https://data.gtdb.ecogenomic.org/releases/release202/202.0/auxillary_files"

# Download key GTDB files
wget -c ${BASE_URL}/gtdbtk_r202_data.tar.gz
wget -c ${BASE_URL}/metadata_field_desc.tsv
wget -c ${BASE_URL}/hq_mimag_genomes_r202.tsv
wget -c ${BASE_URL}/gtdb_vs_ncbi_r202_bacteria.xlsx
wget -c ${BASE_URL}/gtdb_vs_ncbi_r202_archaea.xlsx
wget -c ${BASE_URL}/synonyms_bac120_r202.tsv
wget -c ${BASE_URL}/synonyms_ar122_r202.tsv
wget -c ${BASE_URL}/bac120_markers_info_r202.tsv
wget -c ${BASE_URL}/ar122_marker_info_r202.tsv
wget -c ${BASE_URL}/bac120_r202_sp_labels.tree
wget -c ${BASE_URL}/ar122_r202_sp_labels.tree

# Optional QC files
wget -c ${BASE_URL}/qc_failed.tsv

# Verify download sizes
echo "Download complete. Verifying files:"
ls -lh
