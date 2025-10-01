rule normalization:
    input:
        "results/function/{sample}_pathabundance.tsv.gz"
    output:
        "results/normalized/{sample}_{method}.tsv"
    params:
        method = "{method}"

    conda:"stats_env"
    
    threads: 2
    log:
        "results/normalized/{sample}_{method}.log"
    script:
        "workflow/scripts/normalization.py"


