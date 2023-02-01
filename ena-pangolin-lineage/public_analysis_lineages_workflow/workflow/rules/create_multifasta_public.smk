rule create_multifasta_public:
	input:
		expand("{output_dir}/public_consensus/end.txt", output_dir=config["output_dir"])
	output:
		expand("output_dir/public_multifasta/multifasta_{n}.fasta", n=range(1,config["chunks"]+1), output_dir=config["output_dir"])
	params:
		num = str(config["chunks"])
	resources:
                mem_mb = 2048,
                tmpdir=config["temp_dir"]
	shell:
		"python {config[workflow_dir]}/workflow/scripts/create_multifasta_public.py -f {config[output_dir]}/public_consensus -num {params.num} -o {config[output_dir]}/public_multifasta"
