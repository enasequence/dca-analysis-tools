rule run_pangolin:
	input:
		"{output_dir}/public_seq_multifasta/multifasta_{n}.fasta"
	output:
		"{output_dir}/pango_seq/pango_lineages.{n}.csv"
	threads: 4
	resources:
		mem_mb = 3048,
		tmpdir=config["temp_dir"]
	shell:
		"pangolin --threads {threads} --outfile {output} {input}"
