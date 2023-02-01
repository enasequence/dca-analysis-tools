
# ENA ***XML*** Dump 

## Background
This tool has been developed to handle XML bulk download of ENA objects from ERA database
The tool only required the object or the project accession number and fetch the public and private data only. 
## Getting Started

`This script needs to be run through the VPN`
```Python 3.9```

The ERA database is an Oracle database. In order to query the db, this script uses the `cx_Oracle` python module, which requires a little setup.

 - Install the module using:  `pip install cx_Oracle`

 - The [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client.html) is a requirement of this module. The ***‘Basic Light’*** package is sufficient for our needs.

 - Once the instant client is downloaded, set the location of this library using the `$ORACLE_CLIENT_LIB` environment variable before using this script.
 
 ***Setting up the Enviroment***
	 `,NO NEED FOR ROOT WORK`
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

## Running the Script

 - Provide your *ERAPRO* details and credentials into the config file (*config.yaml*)
 - Run the script using the following flags
	 
	**One of the following flags only needed**
	 - `--file/-f`: Accession list file path (no header is needed) 
	 - `--accession/-acc`: Accession numbers seperated by comma ( make sure no spaces) 
	 
	 **Mandatory Flags**
	 - `--type/-t`: Data type (options: project, study, sample, analysis, run and experiment)
	 - `--config/-c`: Path to *config.yaml* file
	 - `--output/-o`: Path to the output directory
	
 *Examples:*
 - `python3 xml_dump.py -acc ERZ### -t analysis-c config.yaml -o path/to/output`
 - `python3 xml_dump.py -f path/to/accession_file.txt -t run -c config.yaml -o path/to/output`

	 
	**Fetch XMLs using project accession**
 - Combining the project accession in `--accession/-c` flag with data type (`--type/-t`), you will be downloading all the data (specified in the data type flag) associated to the project.
 
 - *Example:*
	 - ` python3 xml_dump.py -acc PRJEB## -t sample -c config.yaml -o
   path/to/output`
 - To fetch all the data in a project, use the `--type/-t all` flag
 
 - *Example:*

	 - ` python3 xml_dump.py -acc PRJEB## -t all -c config.yaml -o
   path/to/output`

	
	 

 

