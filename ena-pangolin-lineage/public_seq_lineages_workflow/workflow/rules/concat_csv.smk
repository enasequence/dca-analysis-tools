rule concat_csv:
	input:
		expand("{output_dir}/pango_seq/pango_lineages.{n}.csv", n=range(1,config["chunks"]+1), output_dir=config["output_dir"])
	output:
		"{output_dir}/pango_seq/end_of_pangolin_workflow.txt"
	
	resources:
                mem_mb = 2048,
		tmpdir=config["temp_dir"]

	shell:
		"python {config[workflow_dir]}/workflow/scripts/public_concatenate_pangolin.py -f {config[output_dir]}/pango_seq -o {config[final_output_dir]}"
