# INSDC SARS-CoV-2 Dataflow Tracking Workflow

  `This script needs to be run through EBI VPN`

The workflow in this repository are created using Snakemake workflow management system to monitor the SARS-CoV-2 dataflow between INSDC (NCBI and DDBJ) and ENA.

The workflows includes:
-  **Data Fetching Script:** Fetch the data through API's from NCBI and ENA.
-  **Data Analysis Script:** Process and compare the data between ENA and NCBI.
-  **Emailer Script:** Email the report as an automated email.

## Getting Started
- **Install a Conda-based Python3 distribution**, miniconda is recommended (see the link below) [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
- **Installation of snakemake**, please follow the guideline below [https://snakemake.readthedocs.io/en/stable/getting_started/installation.html](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html)

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
	```
  
>**Note:**

*The metadata folder needs to be cleaned regularly*
```(path/to/workflow_dir/workflow/.snakemake/metadata)```
  

## Running the workflow:
 
- **Activate conda environment**
```
source path/to/conda/bin/activate
```

### Setting up your Environment

***Modify the workflow config file (config_workflow.yaml) in the folder (config->config_workflow.yaml) by including the appropriate values for each variable as below:***

-  ***output_dir :***  ``` “<path/to/outputFolder >”``` -> The absolute path to the output of the workflow

-  ***workflow_dir :***  ```“</path/to/workflowFolder >”``` -> The absolute path to the workflow folder

-  ***temp_dir :***  ```“<path/to/temp>”``` -> The absolute path to prefer temporary file directory

  ***Modify the credentials config file (config_credentials.yaml) in the folder (config->config_credentials.yaml) by including the appropriate values for each variable as below:***
  - ***ERAPRO_DETAILS:*** The credentials of the ERAREAD database where runs are going to be analysed 
  -  ***ENAPRO_DETAILS:*** The credentials of the ENAREAD database where sequences are going to be analysed  
  - ***EMAIL_DETAILS:*** The credentials of the sender email where the email are going to be sent from (more details below)
	  - ***sender_email_add:*** The email address of the sender
	  -  ***sender_email_pass:*** The email password of the sender
	  -  ***emails_list:*** The recipient emails list (seperated by comma without spaces)

- Modify the "configfile" path in the *Snakefile* to direct to your current *config_workflow.yaml* file

	``` configfile: "<path/to/config_workflow.yaml>" ```

  

### Run the Workflow

***To run the workflow just run the following command:***

```snakemake --cores 8 -s <path/to/Snakefile> --latency-wait 60 --rerun-incomplete```
  

***To integrate the workflow in a routine job please add the ```--forceall``` flag as following***

```snakemake --cores 8 -s <path/to/Snakefile> --latency-wait 60 --rerun-incomplete --forceall```
  
*for further instruction on how to use snakemake, please check snakemake guideline (link below):*

https://snakemake.readthedocs.io/en/stable/index.html

  
```Snakemake v7.21.0```, ```Python 3.9```
