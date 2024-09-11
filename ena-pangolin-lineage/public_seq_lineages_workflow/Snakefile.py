import subprocess
import yaml
import os
import concurrent.futures
import glob

def load_config(configfile):
    """Load configuration file."""
    with open(configfile) as f:
        config = yaml.safe_load(f)
    return config

def transfer_rule(config):
    """Execute the transfer rule."""
    transfer_input = config["transfer_input"]
    workflow_dir = config["workflow_dir"]
    output_files_transfer = f"{workflow_dir}/workflow/rules/embl-covid19.accs.txt"

    subprocess.run(["cp", transfer_input, output_files_transfer])

def create_update_list_rule(config):
    """Execute the create_update_list rule."""
    workflow_dir = config["workflow_dir"]
    input_file_create_update_list = f"{workflow_dir}/workflow/rules/embl-covid19.accs.txt"
    output_dir = config["output_dir"]
    output_file_create_update_list = f"{output_dir}"
    days = 90

    subprocess.run([
        "python3",
        f"{workflow_dir}/workflow/scripts/list_updated.py",
        "-o", output_file_create_update_list,
        "-f", input_file_create_update_list,
        "-d", str(days)
    ])


def fetch_public_seq_multifasta_rule(config):
    """Execute the fetch_public_seq_multifasta rule."""
    output_dir = config["output_dir"]
    chunks = config["chunks"]
    workflow_dir = config["workflow_dir"]

    input_file  = f"{output_dir}/embl-covid19.accs_updated.txt"
    
    subprocess.run([
            "python3",
            f"{workflow_dir}/workflow/scripts/data_fetch_public_seq.py",
            "-o", f"{output_dir}/public_seq_multifasta",
            "-f", input_file,
            "-num", str(chunks)
        ])

def run_pangolin_rule(config):
    """Execute the run_pangolin rule."""
    output_dir = config["output_dir"]
    os.system(f'mkdir -p {output_dir}/pango_seq')
    input_files = os.listdir(f"{output_dir}/public_seq_multifasta")
    input_files = [f"{output_dir}/public_seq_multifasta/{file}" for file in input_files if file.startswith("multifasta_")]

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for input_file in input_files:
            output_file = f"{output_dir}/pango_seq/{os.path.basename(input_file).replace('multifasta_', 'pango_lineages_').replace('.fasta', '.csv')}"
            futures.append(executor.submit(run_pangolin, input_file, output_file))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

def run_pangolin(input_file, output_file):
    """Run Pangolin on the specified input file."""
    try:
        subprocess.run(["pangolin", "--threads", "4", "--outfile", output_file, input_file], check=True)
        print(f"Pangolin completed for {input_file}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Pangolin failed for {input_file}: {e}")

def concat_csv(config):
    """Concatenate CSV files."""
    output_dir = config["output_dir"]
    input_files_dir = f"{output_dir}/pango_seq"
    #output_file = f"{output_dir}/pango_seq/end_of_pangolin_workflow.txt"

    try:
        subprocess.run([
            "python",
            f"{config['workflow_dir']}/workflow/scripts/public_concatenate_pangolin.py",
            "-f", input_files_dir,
            "-o", config["final_output_dir"]
        ], check=True)
        print("CSV files concatenated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def filtration_merging(config):
    #input_file = os.path.join(config["output_dir"], "pango_seq", "end_of_pangolin_workflow.txt")
    #output_file = os.path.join(config["output_dir"], "pango_seq", "merged.txt")

    # Execute the merging and filtration script
    subprocess.run(["python", f"{config['workflow_dir']}/workflow/scripts/merging_filtration.py", "-f", config["final_output_dir"]])

    # Create the output file to indicate completion
    #with open(output_file, "w") as f:
    #    pass

def create_symlink(config):
    # Get the latest CSV file in the final output directory
    latest_csv = sorted(glob.glob(os.path.join(config["final_output_dir"], "*.csv")), key=os.path.getctime)[-1]
    
    # Create a symbolic link to the latest CSV file
    symlink_path = os.path.join(config["final_output_dir"], "public_sequence_pango_lineages.csv")
    os.system(f"ln -sfn {latest_csv} {symlink_path}")

    # Create the output file to indicate completion
    # os.system(f"touch {symlink_path}")

def main(configfile):
    """Main function to execute the rules."""
    # Load config
    config = load_config(configfile)

    # Execute transfer rule
    transfer_rule(config)

    # Execute create_update_list rule
    create_update_list_rule(config)

    # Execute fetch_public_seq_multifasta rule
    fetch_public_seq_multifasta_rule(config)

    #  pangolin 
    run_pangolin_rule(config)

    # concat
    concat_csv(config)

    # filter
    filtration_merging(config)

    # Create symlink
    create_symlink(config)


# Run the main function
configfile = "/hps/nobackup/cochrane/ena/users/khadim/project/COVID19_lineages/public_seq_lineages_workflow/config/config.yaml"
main(configfile)
