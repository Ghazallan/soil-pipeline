rule fastp_qc_summary:
    input:
        jsons = expand("results/fastp/{sample}.json", sample=RAW_SAMPLES)
    output:
        csv = "results/reports/fastp_qc_summary.csv",
        plot1 = "results/plots/basepair_stacked_barplot.png",
        plot2 = "results/plots/base_quality_density.png"
    conda: "fastp"
    threads: 2
    log:
        "results/reports/fastp_qc_summary.log"
    script:
        "/home/hadis/soil_microbiome_pipeline/workflow/scripts/fastp_qc_summary.py"