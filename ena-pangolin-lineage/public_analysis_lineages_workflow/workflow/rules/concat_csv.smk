rule concat_csv:
	input:
		expand("{output_dir}/pango/pango_lineages.{n}.csv", n=range(1,config["chunks"]+1), output_dir=config["output_dir"])
	output:
		expand("{output_dir}/pango/end_of_pangolin_workflow.txt", output_dir=config["output_dir"])
	
	resources:
                mem_mb = 2048,
                tmpdir=config["temp_dir"]

	shell:
		"python {config[workflow_dir]}/workflow/scripts/public_concatenate_pangolin.py -f {config[output_dir]}/pango -o {config[final_output_dir]}"
