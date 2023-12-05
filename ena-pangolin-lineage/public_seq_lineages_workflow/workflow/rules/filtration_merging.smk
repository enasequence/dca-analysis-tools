rule filtration_merging:
	input:
		expand ("{output_dir}/pango_seq/end_of_pangolin_workflow.txt", output_dir=config["output_dir"])
	output:
		"{output_dir}/pango_seq/merged.txt"
	
	resources:
                mem_mb = 6048

	shell:
		"python {config[workflow_dir]}/workflow/scripts/merging_filtration.py -f {config[final_output_dir]} && touch {config[output_dir]}/pango_seq/merged.txt"
