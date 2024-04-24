#!/usr/bin/env bash
export ORACLE_HOME=/path/to/the/<instantclient-version>
# Load database connection info
set -o allexport
source /path/to/the/.env
set +o allexport

# Read sql query into a variable
sql="$(<"/path/to/the/query.sql")"

# Connect to the database, run the query, then disconnect


DATE=$(date +%y.%m.%d-%H.%M.%S)
echo "************************************************" >> /path/to/the/output.log
echo "Command Execution date: ${DATE}." >> /path/to/the/output.log
echo -e "SET FEEDBACK ON\n ${sql}" | \
/path/to/the/<instantclient-version>/sqlplus -S -L ${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_DATABASE} >> /path/to/the/output.log
echo "************************************************" >> /path/to/the/output.log
