import glob
import os.path
import datetime
import os
import sys
import pathlib


rule data_analysis:
	input:
		expand("{output_dir}/end.txt", output_dir=config["output_dir"])

	output:
		expand("{output_dir}/end_final.txt", output_dir=config["output_dir"])

	params: 
		latest_folder=max([f.path for f in os.scandir(config["output_dir"]) if f.is_dir()], key=os.path.getctime)
	resources:
		mem_mb = 5048,
		tmpdir=config["temp_dir"]

	run:
		shell("python3 {config[workflow_dir]}/workflow/scripts/data_analysis_script.py -f {params.latest_folder} -db reads -c {config[workflow_dir]}/config/config_credentials.yaml")
		shell("python3 {config[workflow_dir]}/workflow/scripts/data_analysis_script.py -f {params.latest_folder} -db sequences -c {config[workflow_dir]}/config/config_credentials.yaml && touch {output}")
