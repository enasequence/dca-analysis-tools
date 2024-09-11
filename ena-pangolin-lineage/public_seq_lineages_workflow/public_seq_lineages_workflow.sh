#!/bin/bash

# SLURM job parameters
#SBATCH --time=7-00:00:00   # walltime
#SBATCH --mem=100G           # memory per node
#SBATCH -J "pub_seq_lineages_workflow"   # job name
#SBATCH -e "public_seq_lineages_workflow_covid.err"   # job error file
#SBATCH --mail-user=khadim@ebi.ac.uk   # email address
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --cpus-per-task=48

rm -rf slurm*
rm -rf .snakemake*

# Load Conda and activate the environment
source /hps/nobackup/cochrane/ena/users/analyser/miniconda3/etc/profile.d/conda.sh
export PATH="/hps/nobackup/cochrane/ena/users/analyser/miniconda3/bin:$PATH"

conda activate pangolin

/hps/nobackup/cochrane/ena/users/analyser/miniconda3/bin/python workflow/Snakefile.py

# Remove existing Snakemake locks
#snakemake --unlock > snakemake_log.txt

# Run Snakemake workflow

#snakemake -s /nfs/production/cochrane/ena/users/khadim/project/COVID19_lineages/public_seq_lineages_workflow/workflow/Snakefile --restart-times 4 --latency-wait 60 --forceall --rerun-incomplete --cores 50 >> snakemake_log.txt

