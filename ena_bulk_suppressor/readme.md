# ENA Analysis Supress and Cancel Tool

## Background
This tool is to suppress and cancel analysis objects in bulk from ENA by directly changing the status in the database. sequence and read suppressions are not implemented here yet.

## Getting Started

`This script needs to be run through the VPN`
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
 - Provide the *database statusComment* in the config file  (*config.yaml*)
 - Run the script using the following flags
 
	 - `--config/-c`: path/ to/config file
	 - `--file/-f`: path /to/the/inputFile ( list of accessions to be suppressed/cancelled
	 - `--database/-db`: The dataset type: erapro or enapro
	 - `--action/-a`:  Action type: suppress or cancel
 - *Example:*
	 - `python3 ena-suppress-cancel.py -c path/to/config.yaml -f path/to/inputFile -db erapro -a cancel`


