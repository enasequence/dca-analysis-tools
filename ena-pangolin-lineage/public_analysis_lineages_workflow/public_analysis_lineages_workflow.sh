#!/bin/bash

# SLURM job parameters
#SBATCH --time=7-00:00:00   # walltime
#SBATCH --mem=400G           # memory per node
#SBATCH -J "pub_ana_lineages_workflow"   # job name
#SBATCH -e "public_analysis_lineages_workflow_covid.err"   # job error file
#SBATCH -o "public_analysis_lineages_workflow_covid.out"
#SBATCH --mail-user=khadim@ebi.ac.uk   # email address
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --cpus-per-task=48
#SBATCH -p standard

#rm -rf output_rm/

# Load Conda and activate the environment
source /hps/nobackup/cochrane/ena/users/analyser/miniconda3/etc/profile.d/conda.sh
export PATH="/hps/nobackup/cochrane/ena/users/analyser/miniconda3/bin:$PATH"


conda activate pangolin

/hps/nobackup/cochrane/ena/users/analyser/miniconda3/bin/python public_analysis_lineages_covid.py
