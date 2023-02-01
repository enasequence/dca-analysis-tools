rule fetch_public_fasta:
	input:
		expand("{output_dir}/run_public_pangolin.txt", output_dir=config["output_dir"])
	output:
		"{output_dir}/public_consensus/end.txt"

	resources:
                mem_mb = 2048,
                tmpdir=config["temp_dir"]

	shell:
		 "python3 {config[workflow_dir]}/workflow/scripts/public_consensus_fetch.py -o {config[output_dir]}/public_consensus"
