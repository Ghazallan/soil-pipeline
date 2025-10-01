rule merge_metaphlan_profiles:
    input:
        expand("results/taxonomy/{sample}_metaphlan_profile.tsv", sample=SAMPLES)
    output:
        merged = "results/taxonomy/merged_metaphlan_profiles.tsv",
        summary = "results/reports/taxonomic_summary.tsv"
    log:
        "logs/merge_metaphlan.log"
    conda:
        "metaphlan_env"
    script:
        "workflow/scripts/merge_metaphlan_tables.py"
