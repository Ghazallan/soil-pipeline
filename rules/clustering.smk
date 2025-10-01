rule clustering:
    input:
        expand("results/normalized/{sample}_clr.tsv", sample=RAW_SAMPLES)
    output:
        report = "results/ml/clustering_results.pdf",
        cluster_data = "results/ml/cluster_assignments.tsv"
    conda: "stats_env"
    threads: 2
    log:
        "results/ml/clustering.log"
    script:
        "scripts/clustering.py"

