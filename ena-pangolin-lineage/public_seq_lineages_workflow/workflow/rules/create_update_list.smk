rule create_update_list:
        input:
                expand("{workflow_dir}/workflow/rules/embl-covid19.accs.txt", workflow_dir=config["workflow_dir"])
        output:
                expand("{output_dir}/embl-covid19.accs_updated.txt", output_dir=config["output_dir"])
        params:
                days = config["days"]
        resources:
                mem_mb = 3048
        shell:
                "python3 {config[workflow_dir]}/workflow/scripts/list_updated.py -o {config[output_dir]} -f {input} -d {params.days}"
