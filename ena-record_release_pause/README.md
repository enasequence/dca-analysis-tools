# ENA Record Release Pause

## Introduction

This script is using ENA Oracle database (ERAPRO) to pause the release of projects and studies during the holiday period. 
The script contains three files: 
-  **.env file:** Contains ERAPRO credentials.
-  **query.sql:** Contains the SQL Query.
-  **script.sh:** Bash script to run the query into the database.

## Getting Started

- **Setting up the Oracle database enviroment**
The ERA database is an Oracle database. In order to query the db, this script uses the `sql plus`, which requires a little setup.
 
 -- The [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client.html) is a requirement. remmber to choose the version that contains sqlplus
 
 -- Once the instant client is downloaded, Unzip the `instantclient` and Find the path for the unzipped `instantclient`  and save it.
    
For more details, see: [https://cx oracle.readthedocs.io/en/latest/user_guide/installation.html](https://cxoracle.readthedocs.io/en/latest/user_guide/installation.html)

- **Clone the repository**
	```
	git clone <repository>
	```
	
### Setting up your Environment
- Modify the `.env` file by adding the ERAPRO details and credentials ( make sure that the details are with writting permission)
- Modify the dates in the `query.sql` file to include the date when all the data should be release and the period when the release is paused. 
- Modify the paths in the `script.sh` file to direct for the output log, unzipped instantclient, .env file and query.sql file.

-- replace all /path/to/the/output.log with your preffered output path

-- replace all /path/to/the/<instantclient-version> for your own local unzipped instantclient path

-- replace all /path/to/the/query.sql for your local  query.sql path 

-- replace all /path/to/the/.env for your local .env path

### Run the script
run the shell script

`sh script.sh`