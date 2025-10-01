rule merge_reads:
    input:
        r1 = "results/fastp/{sample}_R1_trimmed.fastq",
        r2 = "results/fastp/{sample}_R2_trimmed.fastq"
    output:
        merged = "results/fastp/{sample}_merged.fastq"
        
    wildcard_constraints:
        sample="|".join([re.escape(s) for s in RAW_SAMPLES])
    
    conda: "fastp"
        
    shell:
        """
        cat results/fastp/{wildcards.sample}_R1_trimmed.fastq \
            results/fastp/{wildcards.sample}_R2_trimmed.fastq \
            > results/fastp/{wildcards.sample}_merged.fastq
        """
