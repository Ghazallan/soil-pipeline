rule indicator_species:
    input:
        features = "results/normalized/combined_normalized.tsv",
        metadata = "metadata/environmental_variables.tsv"
    output:
        plots = "results/analysis/indicator_species_plots.pdf",
        results = "results/analysis/indicator_species_results.rds",
        tables = expand("results/analysis/indicator_species_{variable}_indval.tsv",
                       variable=["pH", "temperature", "moisture"])
    conda: "stats_env"
    threads: 2
    log:
        "results/stats/indicator_species.log"
    script:
        "scripts/indicator_species.R"
