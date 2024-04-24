import glob
import os.path
import datetime
import os
import sys
import pathlib

rule emailer:
	input:
		expand("{output_dir}/end_final.txt",output_dir=config["output_dir"])
	output:
		expand("{output_dir}/sent.txt", output_dir=config["output_dir"])

	resources:
		mem_mb = 8048,
		tmpdir=config["temp_dir"]
	params:
                latest_folder=max([f.path for f in os.scandir(config["output_dir"]) if f.is_dir()], key=os.path.getctime)

	shell:
		"python3 {config[workflow_dir]}/workflow/scripts/emailer.py -f {params.latest_folder} -c {config[workflow_dir]}/config/config_credentials.yaml -g {config[workflow_dir]}/ignore_list.txt && touch {output}"
