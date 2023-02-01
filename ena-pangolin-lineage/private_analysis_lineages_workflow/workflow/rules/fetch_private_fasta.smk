rule fetch_private_fasta:
	input:
		expand("{output_dir}/run_pangolin.txt", output_dir=config["output_dir"])
	output:
		"{output_dir}/private_consensus/end.txt"

	resources:
                mem_mb = 2048,
                tmpdir=config["temp_dir"]

	shell:
		 "python3 {config[workflow_dir]}/workflow/scripts/private_fasta_fetching.py -o {config[output_dir]}/private_consensus"
