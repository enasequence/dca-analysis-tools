#!/usr/bin/env python3.8

# Copyright [2020] EMBL-European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, sys
import cx_Oracle
import configparser

class DB_connect:

    """
    Setup the connection database.
    """
    def __init__(self, database, config_dir):
        self.database = database
        self.config_dir = config_dir

    def setup_connection(self):
        config = configparser.ConfigParser()
        config.read(self.config_dir)
        client_lib_dir = os.getenv('ORACLE_CLIENT_LIB')
        connection = None
        if self.database.upper() == 'ERAPRO':
            sys.stderr.write('Connecting to ERAPRO\n')
            oracle_usr, oracle_pwd = [config['ERAPRO_DETAILS']['userName'],
                                      config['ERAPRO_DETAILS']['password']]  # get_oracle_usr_pwd
            if not client_lib_dir or not os.path.isdir(client_lib_dir):
                sys.stderr.write("ERROR: Environment variable $ORACLE_CLIENT_LIB must point at a valid directory\n")
                exit(1)
            cx_Oracle.init_oracle_client(lib_dir=client_lib_dir)
            try:
                dsn = cx_Oracle.makedsn(config['ERAPRO_DETAILS']['host'], config['ERAPRO_DETAILS']['port'], service_name=config['ERAPRO_DETAILS']['serviceName'])
                connection = cx_Oracle.connect(oracle_usr, oracle_pwd, dsn, encoding="UTF-8")
                return connection
            except cx_Oracle.Error as error:
                print(error)
        elif self.database.upper() == 'ENAPRO':
            sys.stderr.write('Connecting to ENAPRO\n')
            oracle_usr, oracle_pwd = [config['ENAPRO_DETAILS']['userName'],
                                      config['ENAPRO_DETAILS']['password']]  # get_oracle_usr_pwd
            try:
                dsn = cx_Oracle.makedsn(config['ENAPRO_DETAILS']['host'], config['ENAPRO_DETAILS']['port'], service_name=config['ENAPRO_DETAILS']['serviceName'])
                connection = cx_Oracle.connect(oracle_usr, oracle_pwd, dsn, encoding="UTF-8")
                return connection
            except cx_Oracle.Error as error:
                print(error)