rule fastp:
    input:
        r1 = lambda wildcards: sample_dict[wildcards.sample]["R1"],
        r2 = lambda wildcards: sample_dict[wildcards.sample]["R2"]
    output:
        r1_trimmed="results/fastp/{sample}_R1_trimmed.fastq",
        r2_trimmed="results/fastp/{sample}_R2_trimmed.fastq",
        html="results/fastp/{sample}.html",     
        json="results/fastp/{sample}.json"     

    wildcard_constraints:
        sample="|".join([re.escape(s) for s in RAW_SAMPLES])
    log:
        "logs/fastp/{sample}.log"
    threads: config.get("fastp_threads", config["threads"])
    
    conda: "fastp"

    shell:
        """
        fastp -i {input.r1} -I {input.r2} \
              -o {output.r1_trimmed} -O {output.r2_trimmed} \
              -h {output.html} -j {output.json} \
              --thread {threads} \
              2> {log}
        """


