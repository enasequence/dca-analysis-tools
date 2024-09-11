import pandas as pd
import requests
import os
import datetime
import concurrent.futures

# API query URL
# https://docs.google.com/document/d/10DSo6Q2vEl4u3MPxTPFn4S8Saq2l1S9BdjmnTUB0_oU/edit to update the project ID ask Jasmine
project = ['PRJEB43947','PRJEB45554','PRJEB45619','PRJEB55349','PRJEB55355','PRJEB55356','PRJEB57995','PRJEB57993','PRJEB57992','PRJEB59443','PRJEB59444','PRJEB59445','PRJEB61667','PRJEB61668','PRJEB61669','PRJEB70460','PRJEB70461','PRJEB70462']
jproject = '%22%20OR%20study_accession%3D%22'.join(project)

API_query = f"https://www.ebi.ac.uk/ena/portal/api/search?result=analysis&query=tax_eq(2697049)%20AND%20(study_accession%3D%22{jproject}%22)&fields=submitted_ftp&limit=0&format=json"

print (API_query)

ref_data = pd.read_csv('output/public_consensus_pango_lineages.csv',  low_memory=False , on_bad_lines='skip')
ref_data['run_accession'] = ref_data['run_accession'].astype(str).fillna('')
ref_run = ' '.join(list(ref_data['run_accession']))


def fetch_data():
    # Execute the API request
    response = requests.get(API_query)

    # Check the status of the request
    if response.status_code == 200:
        # Convert the response to JSON
        data = response.json()

        # Create a DataFrame
        df = pd.DataFrame(data)

        # Display the DataFrame
        return df
    else:
        print("Error with the API request:", response.status_code)

def data_prep(submitted_ftp):
    if 'fasta' not in submitted_ftp : 
        return
    try:
        run_accession = submitted_ftp.split('/')
        run_accession = run_accession[len(run_accession)-1].split('_')[0]
        if run_accession not in ref_run :
            with open('accession.txt','a') as f:
                f.write(f'{submitted_ftp}\n')
            os.system(f"cd output ; curl -o {run_accession}_consensus.fasta.gz {submitted_ftp}")
            os.system(f"cd output ; pangolin --threads 8 --outfile {run_accession}_consensus.csv {run_accession}_consensus.fasta.gz")
            print (f'{run_accession} -> pangolin done')
            df = pd.read_csv(f'output/{run_accession}_consensus.csv')
            scorpio_call = str(df['scorpio_call'][0])
            who = ''
            if '(' in scorpio_call :
                who = scorpio_call.split('(')[0]
            result = str(open(f'output/{run_accession}_consensus.csv','r').read().split('\n')[1])+f',{run_accession},{who}'
            with open('output/public_consensus_pango_lineages.csv','a') as file:
                file.write(f'\n{result}')
            os.system (f'rm -rf output/{run_accession}*')
    except Exception as e:
        print (f'Error : {e}')


def main():
    data = fetch_data() 
    #os.system('cat /nfs/production/cochrane/ena/data/covid19/public_consensus_pango_lineages.csv > output/public_consensus_pango_lineages.csv')

    max_workers = 500
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(data_prep, data['submitted_ftp'])
    now = datetime.datetime.now()
    now_str = now.strftime("%d%m%y")
    print ('file correction')
    finaldata = pd.read_csv('output/public_consensus_pango_lineages.csv', low_memory=False, on_bad_lines='skip')
    finaldata.to_csv(f'/nfs/production/cochrane/ena/data/covid19/public_consensus_pango_lineages_{now_str}.csv', index=False)
    #os.system(f'cp output/public_consensus_pango_lineages.csv /nfs/production/cochrane/ena/data/covid19/public_consensus_pango_lineages_{now_str}.csv')
    os.system(f'cd /nfs/production/cochrane/ena/data/covid19 ; ln -sfn public_consensus_pango_lineages_{now_str}.csv public_consensus_pango_lineages.csv ; chmod +777 * ')

main()

