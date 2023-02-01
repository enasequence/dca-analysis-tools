rule symlink:
	input:
                expand("{output_dir}/pango/end_of_pangolin_workflow.txt", output_dir=config["output_dir"])
	output:
		"{output_dir}/pango/symlinked.txt"
	resources:
                tmpdir=config["temp_dir"]

	shell:
		"ln -sfn {config[final_output_dir]}/$(ls {config[final_output_dir]} -rt | tail -n1)  {config[final_output_dir]}/public_consensus_pango_lineages.csv && touch {config[output_dir]}/pango/symlinked.txt"

