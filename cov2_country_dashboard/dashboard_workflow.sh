#!/bin/bash
source <path/to/miniconda_directory>/miniconda/bin/activate; source $HOME/.bashrc
echo "Start Fetching Data from ENAREAD" &&
python3 <path/to/script_directory>/SQL_Analysis_fetching.py -c <path/to/config_directory>/config.yaml -o <path/to/output_directory> &&
echo "ENAREAD Querying is DONE"
echo "Start Processing Analysis and Sequence data" &&
python3 <path/to/script_directory>/Seq_Analysis_grouping.py -f <path/to/SQL_Analysis_fetching.py_output_directory> -o <path/to/output_directory> &&
echo "Analysis and Sequence data processing is Done"
echo "Start Fetching Data from ERAREAD" &&
python3 <path/to/script_directory>/SQL.Reads_fetching.py -c <path/to/config_directory>/config.yaml -o <path/to/output_directory> &&
echo "ENRREAD Querying is DONE"
echo "Start Processing Read data" &&
python3 <path/to/script_directory>/APIReads_fetch_process.py -f <path/to/SQL.Reads_fetching.py_output_directory> -o <path/to/output_directory> &&
echo "Read data processing is Done"
echo "Sending Data to the DASH VM" &&
sshpass -p "<VM password>" rsync -aP <path/to/output_directory> dash@dca-cv19-dash:<path/to/dashboard_directory>
echo "************DONE****************"
