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

from merger import Merger
import argparse, hashlib, os, subprocess, sys, time
import pandas as pd

parser = argparse.ArgumentParser(prog='Seq_Analysis_grouping.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |  European Nucleotide Archive (ENA) Dashboard Tool  |
        |                                                              |
        |                 |
        + =========================================================== +      
        """)
parser.add_argument('-o', '--output', help='output directory', type=str, required=True)
parser.add_argument('-f', '--file', help='Analysis and Sequence directory', type=str, required=True)
args = parser.parse_args()

def stat_dataframe_sequences(df_analysis,df_sequences, database):
    df_analysis = df_analysis.astype(str)
    df_sequences = df_sequences.astype(str)
    analysis_seq_df = pd.merge(df_analysis, df_sequences, on=['Analysis ID'], how='left')#.fillna('')#.replace('', '0')astype(str)
    GCA_formatting_data = pd.merge(df_analysis, df_sequences, on=['Analysis ID'], how='right')
    print(analysis_seq_df)
    #df = pd.DataFrame.from_dict(APIdata, orient='columns')
    #df['country'] = df['country'].str.split(':').str[0]
    #sql_api_join = pd.merge(analysis_seq_df, df[['accession', 'country']], on='accession', how='left')
    #sql_api_join['Country'] = sql_api_join['Country'].fillna(sql_api_join['country'])
    #sql_api_join.drop(['country'], inplace=True, axis=1)
    merger = Merger(analysis_seq_df, database, GCA_formatting_data)
    analysis_seq_webin = merger[0]
    analysis_seq_webin.to_csv(f"{args.output}/SQL-API.{database}_webin.log.csv", index=False)
    analysis_seq_project = merger[1]
    analysis_seq_project.to_csv(f"{args.output}/SQL-API.{database}_project.log.csv",
                                     index=False)
    center_name_grouped = merger[2]
    center_name_grouped.to_csv(f"{args.output}/SQL-API.{database}_center_names.log.csv",
                               index=False)

if __name__ == "__main__":
    ###########################################
    #                                         #
    #                 MAIN                    #
    #                                         #
    ###########################################

    # fetching analysis data
    sql_output_analysis = pd.read_csv(f"{args.file}/SQL.Analysis.log.csv", sep=",", dtype={"Webin Account": "string", "Project ID": "string", "Project Status ID": int, "Sample ID": "string", "Sample Status ID": int, "Analysis ID": "string" , "Analysis Status ID": int, "Country": "string", "last_updated": "string"})#, header=None, names=['Webin Account', 'Project ID', 'Project Status ID', 'Sample ID', 'Sample Status ID', 'Analysis ID', 'Analysis Status ID', 'Country'])
    sql_output_seq = pd.read_csv(f"{args.file}/SQL.Sequence.log.csv", sep=",", dtype={"Analysis ID": "string", "GC_ID": "string", "GC Status ID": int, "Sequence Accessions Range": "string", "WGS ID": "string"})#, header=None, names=['Analysis ID', 'GC_ID', 'GC Status ID', 'Sequence Accessions Range', 'WGS ID'])
    stat_dataframe_sequences(sql_output_analysis, sql_output_seq,'sequence')


    sys.stderr.write("*************END*************\n")