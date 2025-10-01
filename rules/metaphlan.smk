rule metaphlan_profiling:
    input:
        r1 = lambda wc: FASTQS[wc.sample][0],
        r2 = lambda wc: FASTQS[wc.sample][1]
    output:
        profile = "results/taxonomy/{sample}_metaphlan_profile.tsv",
        bowtie2 = temp("results/bowtie2/{sample}.bowtie2.bz2")
    log:
        "logs/metaphlan/{sample}.log"
    threads: 4
    conda:
        "metaphlan_env"
    shell:
        r"""
        set -euo pipefail
        mkdir -p results/taxonomy logs/metaphlan results/bowtie2 results/reports

        (
          echo "Starting MetaPhlAn for {wildcards.sample}"
          echo "Input: {input.r1} , {input.r2}"
          echo "DB dir: {config[metaphlan_db]} | Index: {config[metaphlan_index]}"
          date

          metaphlan \
            {input.r1},{input.r2} \
            --input_type fastq \
            --bowtie2db "{config[metaphlan_db]}" \
            -x "{config[metaphlan_index]}" \
            --nproc {threads} \
            {config[metaphlan_presets]} \
            -o {output.profile} \
            --bowtie2out {output.bowtie2}

          echo "Done"
          date
        ) &>> "{log}"
        """
