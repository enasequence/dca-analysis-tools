from package.download_data import DownData
from package.nexclade import nextclade
import logging
import yaml 
import sys
from datetime import datetime ,date
import os
import csv


logging.basicConfig(filename='output.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def pathogens ():
    try:
        with open('/nfs/production/cochrane/ena/data/monkeypox/mpx_nextstrain_nextclade/pathogens.yaml', 'r') as file:
            pathogens = yaml.safe_load(file)
            monkeypox = str(pathogens['Monkeypox'])
            return monkeypox
    except Exception as ex:
        logging.error(f'Exception for:\n {ex}')
        sys.exit()

###################################### Generat of the public_sequence_pango_lineages[date] file.

def generate_final_file(input_filename):
    with open(input_filename, "r") as input_file:
        input_lines = input_file.readlines()

    current_date = date.today()
    new_file = f"/nfs/production/cochrane/ena/data/monkeypox/public_sequence_pango_lineages_{current_date.day}{current_date.month}{current_date.year}.csv"

    with open(f"{new_file}", "w", newline='') as output_file:
        csv_writer = csv.writer(output_file)
        csv_writer.writerow(["accession", "clade", "lineage"])

        for line in input_lines[1:]:  # Skip the header line
            if line.strip():  # Check if the line is not empty
                columns = line.split("\t")
                if len(columns) >= 4:
                    accession = columns[1]
                    clade = columns[2]
                    lineage = columns[4]
                    csv_writer.writerow([accession, clade, lineage])

    return new_file




def main():
    try:
        monkeypox = pathogens()
        DownData.downdata( monkeypox , '/nfs/production/cochrane/ena/data/monkeypox/mpx_nextstrain_nextclade/data/mpxv')
        DownData.fataprep('/nfs/production/cochrane/ena/data/monkeypox/mpx_nextstrain_nextclade/data/mpxv','/nfs/production/cochrane/ena/data/monkeypox/mpx_nextstrain_nextclade/data/all_consensus/')
        nextclade.nextclade_new_version('/nfs/production/cochrane/ena/data/monkeypox/mpx_nextstrain_nextclade/package/nextclade')
        nextclade.Downloaddataset('/nfs/production/cochrane/ena/data/monkeypox/mpx_nextstrain_nextclade/package/datasets/mpxv')
        nextclade.run_nextclade('/nfs/production/cochrane/ena/data/monkeypox/mpx_nextstrain_nextclade/package/datasets/mpxv','/nfs/production/cochrane/ena/data/monkeypox/mpx_nextstrain_nextclade/data/all_consensus/sequences.fasta','/nfs/production/cochrane/ena/data/monkeypox/mpx_nextstrain_nextclade/output/nextclade.tsv')
        new_file = generate_final_file ("/nfs/production/cochrane/ena/data/monkeypox/mpx_nextstrain_nextclade/output/nextclade.tsv" )
        os.system("cd .. ; ln -sf  "+new_file+"  /nfs/production/cochrane/ena/data/monkeypox/public_sequence_pango_lineages.csv")
    except Exception as ex:
        logging.error(f'Exception for:\n {ex}')

if __name__ == '__main__':
    main()
