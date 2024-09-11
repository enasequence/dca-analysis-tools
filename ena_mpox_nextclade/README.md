# ENA_Mpox_nextclade

This repository provides a pipeline to download public Mpox data from ENA via API, determine the clade and lineage of each assembly using Nextclade, and keep Nextclade updated.

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/enasequence/dca-analysis-tools.git
   ```

2. **Navigate to the project directory:**
   ```sh
   cd dca-analysis-tools/ena_mpox_nextclade
   ```

3. **Install required Python packages:**
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. **Run the pipeline script:**
   ```sh
   python ena_nextclade.py
   ```

This script performs the following steps:
   - Downloads public Mpox data from ENA using the ENA API.
   - Updates Nextclade automatically, ensuring it always uses the latest version.
   - Determines the clade and lineage of each assembly using Nextclade.

## Explanation of Key Components

- **`ena_nextclade.py`**: The main script that handles data downloading, Nextclade updating and clade and lineage determination.
