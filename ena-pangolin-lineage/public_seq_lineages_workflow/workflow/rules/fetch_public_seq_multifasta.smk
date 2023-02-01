rule fetch_public_seq_multifasta:
	input:
		expand("{output_dir}/embl-covid19.accs_updated.txt", output_dir=config["output_dir"])
	output:
                expand("{output_dir}/public_seq_multifasta/multifasta_{n}.fasta", n=range(1,config["chunks"]+1), output_dir=config["output_dir"])
	params:
                num = str(config["chunks"])
	threads: 4
        
	resources:
                mem_mb = 3048,
		tmpdir=config["temp_dir"]
	shell:
		 "python3 {config[workflow_dir]}/workflow/scripts/data_fetch_public_seq.py -o {config[output_dir]}/public_seq_multifasta -f {input} -num {params.num}"
