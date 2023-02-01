rule transfer:
    input:
         expand("{output_dir}/pango_lineages.csv", output_dir=config["output_dir"])
    output:
          expand("{output_dir_trans}/end.txt", output_dir_trans=config["output_dir"])
    resources:
          tmpdir=config["temp_dir"]
    shell:
         "aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp {input} s3://dcc_walton/dcc_walton_phylogeny/pango_lineages.csv&&touch {output}"
