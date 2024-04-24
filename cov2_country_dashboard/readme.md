# SARS-CoV-2 Country Submission Tracking Dashboard

  `This script needs to be run through the EBI VPN`

The dashboard in this repository are created using Plotly Dash framework to track the SARS-CoV-2 country submissions into ENA.

The Tool includes:
-  **SQL.Reads_fetching.py:** Fetch the read data from ERAREAD database.
-  **SQL_Analysis_fetching.py:** Fetch Analysis and Sequence data from ENAREAD and ERAREAD
-  **Seq_Analysis_grouping.py:** Process/group the analysis and the sequences from ENAREAD and ERAREAD.
-  **APIReads_fetch_process.py:** Fetch Read and sequence data through ENA portal API, process/group the read data (from the portal API and ERAREAD) and NCBI/DDBJ data (reads and sequences).
-  **dashboard_v2.py:** The Dashboard script contains the final processing and data grouping and the dashboard layout and callbacks
-  **dashboard_workflow.sh:** Bash script that run the workflow to retrieve and process the data.

## Getting Started
- **Install a Conda-based Python3 distribution**, miniconda is recommended (see the link below) [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)

- **Setting up the Oracle database enviroment**
The ERA database is an Oracle database. In order to query the db, this script uses the `cx_Oracle` python module, which requires a little setup.
 - Install the module using:  `pip install cx_Oracle`
 - The [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client.html) is a requirement of this module. The ***‘Basic Light’*** package is sufficient for our needs.
 - Once the instant client is downloaded, set the location of this library using the `$ORACLE_CLIENT_LIB` environment variable before using this script.
 
	 ***Setting up the Enviroment***
	 `NO NEED FOR ROOT WORK`
 - Unzip the `instantclient`
 - Find the path for the unzipped `instantclient`  and save it
 - Edit the `.bashrc` file to set oracle enviroment
 - Add the following lines to the end of `.bashrc` file
	 - `export ORACLE_HOME=/path/to/oracle/instantclient`
	 - `export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH`	   		 	  
	 - `export PATH=$ORACLE_HOME:$PATH`
	 - `export ORACLE_CLIENT_LIB=$ORACLE_HOME`
 
 - `source` the `.bashrc` file
`source $HOME/.bashrc`

For more details, see: [https://cx oracle.readthedocs.io/en/latest/user_guide/installation.html](https://cxoracle.readthedocs.io/en/latest/user_guide/installation.html)

- **Clone the repository**
	```
	git clone <repository>

## Running the Tool:

 ### Setting up your Environment
- **Activate conda environment**
	```
	source path/to/conda/bin/activate
	```

 - **Setting up the scripts environment**

	  ***Modify the config file (config.yaml) by including the appropriate values for each variable as below:***
	  - ***ERAPRO_DETAILS:*** The credentials of the ERAREAD database where runs and analysis are going to be retrieved and  processed
	  -  ***ENAPRO_DETAILS:*** The credentials of the ENAREAD database where sequences are going to be retrieved and processed

	  ***Modify the data fetching and processing workflow file (dashboard_workflow.sh) by adding the absulote files path to each script***


>**Note:**
> The data fetching and processing workflow file (dashboard_workflow.sh) output the data in the form of .csv files, please make sure that the output directory is the same for all the scripts (`-o/--output flag`)

 ### Running The Tool
***To run the data fetching and processing workflow just run the following command:***
	``sh <path/to>/dashboard_workflow.sh`` 
	 
***To run the dashboard just run the following command:***
	```python3 <path/to>/dashboard_v2.py -f <path/to/workflow_output_directory>```

>**Note:**
> You can view the Dashboard by using the following link in your browser (Make sure that you are connected to EBI VPN)
> http://10.42.28.202:8080/ 
