rule humann:
    input:
        fastq="results/fastp/{sample}_merged.fastq",

    output:
        pathabundance="results/function/{sample}_pathabundance.tsv",
        pathcoverage="results/function/{sample}_pathcoverage.tsv",
        genefamilies="results/function/{sample}_genefamilies.tsv"

    wildcard_constraints:
        sample="|".join([re.escape(s) for s in RAW_SAMPLES])
    params:
        output_dir="results/function",
        basename="{wildcards.sample}"
    log:
        "logs/humann_{sample}.log"
    resources:
        mem_mb=32000
    threads: 4
    conda: "humann_env"
    shell:
        """
        humann --input {input.fastq} \
               --output results/function \
               --output-basename {wildcards.sample} \
               --threads {threads} \
               >> {log} 2>&1
        """