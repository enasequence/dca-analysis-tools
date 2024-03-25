
# Analysis Duplication Scanner

## Background
This tool has been developed to scan the analysis objects held by specific projects in ENA for duplication

The tool exclude the suppressed and cancelled data and print out three files
1. Summary of the duplicates 
2. List of accessions to be cancelled ( *if exist*) 
3. List of accessions to be suppressed (*if exist*)

>Note: The tool send the most recent submission out of the duplicates to be suppressed/ cancelled except if the duplicates contains both private and public status, then it will cancel the private analysis regardless of the submission date 
## Getting Started

`This script needs to be run through the VPN`
```Python 3```

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
 - Provide the *project accessions* that you want to scan into the config file (*config.yaml*)
 - Run the script using the following flags
 
	 - `--config/-c`: path/ to/config file
	 - `--output/-o`: path /to/the/output folder
 - *Example:*
	 - `python3 analysis_duplication_scan.py -c path/to/config.yaml -o path/to/output folder`



 


