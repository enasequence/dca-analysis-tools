rule symlink:
	input:
        expand("{output_dir}/pango_seq/end_of_pangolin_workflow.txt", output_dir=config["output_dir"])
	output:
		"{output_dir}/pango_seq/symlinked.txt"

	shell:
		"ln -sfn {config[final_output_dir]}/$(ls {config[final_output_dir]} -rt | tail -n1)  {config[final_output_dir]}/public_sequence_pango_lineages.csv && touch {config[output_dir]}/pango_seq/symlinked.txt"

