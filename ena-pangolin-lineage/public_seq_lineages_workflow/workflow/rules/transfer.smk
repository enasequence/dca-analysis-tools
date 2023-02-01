rule transfer:
        input:
                expand("{transfer_input}", transfer_input=config["transfer_input"])
        output:
                expand("{workflow_dir}/workflow/rules/embl-covid19.accs.txt", workflow_dir=config["workflow_dir"])
	resources:
                tmpdir=config["temp_dir"]

        shell:
                 "cp {input} {output}"
