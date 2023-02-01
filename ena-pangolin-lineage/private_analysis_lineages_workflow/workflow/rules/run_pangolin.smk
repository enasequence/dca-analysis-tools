rule run_pangolin:
	input:
		"{output_dir}/private_multifasta/multifasta_{n}.fasta"
	output:
		"{output_dir}/pango/pango_lineages.{n}.csv"
	threads: 4
	resources:
		mem_mb = 2048,
                tmpdir=config["temp_dir"]
	shell:
		"pangolin --threads {threads} --outfile {output} {input}"
