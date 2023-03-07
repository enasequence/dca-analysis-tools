# SARS-CoV-2 Pangolin Lineages Workflows

The workflows in this repository are created using Snakemake workflow management system to process the SARS-CoV-2 pangolin lineages data held in ENA. 

The workflows includes:
 - **Private analysis lineages workflow:** To process the lineages of the private systematic analysis data.
 - **Public analysis lineages workflow:** To process the lineages of the public systematic analysis data .
 - **Public seq lineages workflow:** To process the lineages of the public sequence ( submitted sequences).

## Getting Started

 - Install a Conda-based Python3 distribution, miniconda is recommended (see the link below)
   [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
 - Installation of snakemake, please follow the guideline below:      
   [https://snakemake.readthedocs.io/en/stable/getting_started/installation.html]
   (https://snakemake.readthedocs.io/en/stable/getting_started/installation.html)
 - Install pangolin software to your conda environment (please follow the link below)   
   [https://cov-lineages.org/resources/pangolin/installation.html](https://cov-lineages.org/resources/pangolin/installation.html)
 - Clone the repository  
   ```
   git clone <repository>
   ```

>**Note:**
 -The metadata folder needs to be cleaned regularly ```(path/to/workflow_dir/workflow/.snakemake/metadata)```
 -Pangolin version needs to be updated regularly, to update pangolin please follow the guideline:
   [https://cov-lineages.org/resources/pangolin/updating.html](https://cov-lineages.org/resources/pangolin/updating.html) 
   

## Running the workflow:

 - Activate conda environment

```
source path/to/conda/bin/activate
```

 - Activate the pangolin environment

```
Conda activate <env name>
```
### Setting up your Environment

***Modify the config file (config.yaml) in the folder (config->config.yaml) by including the appropriate values for each variable as below:***

**For all the configFiles:**

 - ***chunks :*** ```<integer number>``` -> reflect to the number of multifasta generated and pangolin lsf jobs in the workflow
 - ***output_dir :***  ``` “<path/to/outputFolder >”``` -> The absolute path to the output of the workflow
 - ***workflow_dir :*** ```“</path/to/workflowFolder >”``` -> The absolute path to the workflow folder
 - ***temp_dir :*** ```“<path/to/temp>”``` -> The absolute path to prefer temporary file directory

**For private analysis configFile:**

 - ***host :*** ```"<database Hostname>"``` -> The hostname for ERAPRO

 - ***portal :*** ```<port number>``` -> ERAPRO port number

 - ***serviceName :*** ```”<database service name>” ```-> ERPRO service name

**For both public analysis and public sequences configFile:**

 - ***final_output_dir:*** ```“<path/to/outputFolder>”``` -> The path for the final output file ( pangolin concatenated file) destination (it can be the same as the ```output_dir```)

**For public sequence configFile:**

 - ***transfer_input:*** ```“<path/to/accession_list.txt>”``` - > The path for the list of public sequence accessions provided by the presentation team

 - ***days:*** ```<integer number>``` -> collect sequences with submission date in the period of the number of days specify past the current date.

**For public analysis configFile:**
  - ***project_ids:*** ```<PRJEB#####,PRJEB####,PRJEB####>``` -> The project ids that contains the analysis of interest (The analysis to be fetched) separated by comma without spaces 


***Modify the configFile path in the *Snakefile* to direct to your current *config.yaml* file
   ``` configfile: "<path/to/config.yaml>" ```

### Run the Workflow
***To run the workflow just run the following command:***

```snakemake --profile lsf -s <path/to/Snakefile> --latency-wait 60 --rerun-incomplete```

***To integrate the workflow in a routine job please add the ```--forceall``` flag as following***

```snakemake --profile lsf -s <path/to/Snakefile> --latency-wait 60 --rerun-incomplete --forceall```

*for further instruction on how to use snakemake, please check snakemake guideline (link below):*

https://snakemake.readthedocs.io/en/stable/index.html

```Snakemake v7.0.0```, ```Python 3.9```,  ```pangolin v4.1.3```
