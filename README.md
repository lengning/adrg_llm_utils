# Utility Modules for LLM-automated ADRG generation

These utility modules provide the scaffolding for LLM-automated ADRG generation. The ADRG (Analysis Data Reviewer's Guide) is a companion document that explains the contents, derivations, structure, and intended use of submitted ADaM analysis datasets—capturing provenance, conventions, and known limitations—to help regulators understand and reproduce results.

[Example ADRG](https://github.com/RConsortium/submissions-pilot5-datasetjson-to-fda/blob/main/m5/datasets/rconsortiumpilot5/analysis/adam/datasets/adrg.pdf)

## Requirements

- Python 3.8+
- `pandas`
- `langchain_openai` and `langchain_core` (for LLM-based modules)
- `pdfplumber` (for protocol PDF extraction)
- `markdown` (or `markdown2`) for optional HTML rendering of the filled ADRG
- Quarto CLI (optional; required if you plan to render the filled ADRG to PDF or HTML)
- R (for `pkg_describer` module) with packages: `optparse`, `btw`, `ellmer`, `tools`

Install required Python packages:

```bash
pip install pandas langchain-openai langchain-core pdfplumber openpyxl markdown
```
If you prefer `markdown2`, install it instead of `markdown`.

For the `pkg_describer` module, install required R packages:

```r
install.packages(c("optparse", "btw", "ellmer", "tools"))
```

Note: Package names may differ depending on your environment. Adjust as needed.

Install the Quarto CLI by following the [official instructions](https://quarto.org/docs/get-started/) or, on macOS, by running:

```bash
brew install quarto
```

## Configuration

All LLM-based modules read the OpenAI API key from the `OPENAI_API_KEY` environment variable. Set it like this in macOS/zsh:

```bash
export OPENAI_API_KEY="sk-..."
```

If the environment variable is not set, the underlying `ChatOpenAI` client will use its default behavior for locating credentials.

For the `pkg_describer` module, you can also set `MODEL_NAME` as an environment variable to specify a default model name.

## Modules and Their Usage

### var_filter

**Description:** Audits R scripts and extracts filtering criteria, variables used, and output file names using an LLM.

**What it does:**
- Analyzes R script files (`.r` extension)
- Extracts filtering criteria applied in the code
- Identifies variables used for analyses
- Extracts output file names
- Uses an LLM to parse and extract structured information

**Usage:**

Analyze a folder of `.r` files:
```bash
python -m var_filter.main --folder inputs/r_scripts --out outputs/output_var_filter_folder.csv
```

Analyze a single `.r` file:
```bash
python -m var_filter.main --file inputs/r_scripts/tlf-demographic.r --out outputs/output_var_filter_file.csv
```

**Options:**
- `--folder PATH`: Path to folder containing `.r` files (mutually exclusive with `--file`)
- `--file PATH`: Path to a single `.r` file to analyze (mutually exclusive with `--folder`)
- `--model NAME`: LLM model name to use (default: `gpt-4o-mini`)
- `--out PATH`: Output CSV filename (default: `r_code_audit.csv`)
- `--print`: Print results to stdout

**Output:** CSV file with columns: `r_file`, `outputs`, `filters`, `variables`

**Example:**
```bash
python -m var_filter.main --folder inputs/r_scripts --out outputs/output_var_filter_folder.csv --model gpt-4o-mini --print
```

---

### adam_info

**Description:** Extracts variable descriptions from ADaM spec files and analyzes dataset dependencies by examining the Methods sheet.

**What it does:**
- Reads ADaM specification Excel files (with Datasets, Variables, and Methods sheets)
- Extracts variable descriptions for key variables or variables from an input CSV file
- Analyzes the Methods sheet to determine dataset dependencies
- Outputs unique variable names (without dataset prefix) with their descriptions
- Generates a dataset dependency table showing which datasets depend on which other datasets

**Usage:**

Extract variable descriptions from key variables in Datasets sheet:
```bash
python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv
```

Extract variable descriptions from variables in an input CSV file (e.g., from var_filter output):
```bash
python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --input outputs/output_var_filter_folder.csv --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv
```

**Options:**
- `--spec PATH`: Path to ADaM spec Excel file with Datasets, Variables, and Methods sheets (required)
- `--out PATH`: Path to output CSV file for variable descriptions (required)
- `--input PATH`: Optional path to input CSV file with `variables` column (e.g., output from `var_filter`). If not provided, uses key variables from Datasets sheet.
- `--deps-out PATH`: Optional path to output CSV file for dataset dependencies
- `--print`: Print results to stdout

**Output:** 
- Variable descriptions CSV: `Variable Name`, `Variable Description` (unique variables without dataset prefix)
- Dataset dependencies CSV (if `--deps-out` provided): `dataset name`, `depend on the following datasets`

**Notes:**
- Variables are extracted as unique names (dataset prefix removed)
- Dataset dependencies are inferred by analyzing references in the Methods sheet
- If a variable appears in multiple datasets, only one entry is output (first description found)

**Example:**
```bash
# Extract from key variables in Datasets sheet
python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv --print

# Extract from variables found in R scripts (via var_filter output)
python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --input outputs/output_var_filter_folder.csv --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv --print
```

---

### renv_to_table

**Description:** Converts an R `renv.lock` file into a tidy CSV of package names and versions for ADRG workflows.

**What it does:**
- Reads `renv.lock` (JSON format)
- Extracts all packages and their versions
- Skips the R runtime entry
- Writes a sorted CSV with package names and versions

**Usage:**
```bash
python -m renv_to_table.main --renv inputs/renv.lock --out outputs/r_pkg_versions.csv
```

**Options:**
- `--renv PATH`: Path to `renv.lock` file (required)
- `--out PATH`: Output CSV path (optional; if omitted, uses `$R_PACKAGES_OUT` environment variable or places `R_Packages_And_Versions.csv` next to the `renv.lock` file; use `-` to write to stdout)

**Output:** CSV file with columns: `Package`, `Version`

**Example:**
```bash
python -m renv_to_table.main --renv inputs/renv.lock --out outputs/r_pkg_versions.csv
```

---

### pkg_describer

**Description:** Reads a CSV of R package names, fetches each package's CRAN DESCRIPTION file, and optionally uses an LLM to produce user-friendly one-sentence summaries.

**What it does:**
- Reads a CSV file with package names (and optionally versions)
- Fetches each package's CRAN DESCRIPTION file using `tools::CRAN_package_db()`
- Optionally uses an LLM to generate one-sentence summaries of package functionality
- Writes an output CSV with package information and descriptions

**Usage:**
```bash
Rscript pkg_describer/main.R --input outputs/r_pkg_versions.csv --output outputs/pkg_descriptions.csv
```

**Options:**
- `-i, --input PATH`: Input CSV path with a column of package names (required)
- `-o, --output PATH`: Output CSV path (required)
- `-m, --model NAME`: LLM model name to use (default: `gpt-4o-mini`)
- `--no-llm`: Skip LLM calls; only use local CRAN DESCRIPTION text

**Environment variables:**
- `MODEL_NAME`: Optional default model name (e.g., `gpt-4o-mini`). Can also be passed via `-m` option.
- `OPENAI_API_KEY`: OpenAI API key for LLM calls (required if not using `--no-llm`)

**Output:** CSV file with columns: `Package`, `Version`, `Description`

**Notes:**
- An R script is used instead of Python because of the convenience of using `tools` and `btw` R packages
- If `--no-llm` is used, the Description column will contain the raw CRAN DESCRIPTION text

**Example:**
```bash
Rscript pkg_describer/main.R --input outputs/r_pkg_versions.csv --output outputs/pkg_descriptions.csv --model gpt-4o-mini
```

---

### sdtm_medra_version

**Description:** Extracts SDTM Implementation Guide version, SDTM model version, MedDRA version, and Define-XML version from Define-XML files.

**What it does:**
- Parses Define-XML files
- Extracts SDTM Implementation Guide version
- Maps SDTM IG version to corresponding SDTM model version
- Detects MedDRA version from Define-XML
- Extracts Define-XML version (DefineVersion attribute)
- Outputs results in a clean CSV format

**Usage:**
```bash
python -m sdtm_medra_version.main --define inputs/define.xml --out outputs/standards_from_define.csv
```

**Options:**
- `--define PATH`: Path to `define.xml` file (required)
- `--out PATH`: Output CSV file (default: `standards_from_define.csv`)

**Output:** CSV file with columns: `Standard or Dictionary`, `Versions Used`. Contains rows for:
- SDTM (Implementation Guide Version and SDTM Version)
- Medical Events Dictionary (MedDRA version)
- Define-XML (Define version)

**Example:**
```bash
python -m sdtm_medra_version.main --define inputs/define.xml --out outputs/standards_from_define.csv
```

---

### protocol_retrieve

**Description:** Extracts protocol information from clinical trial protocol PDF documents and generates a structured markdown file for ADRG workflows.

**What it does:**
- Extracts text from protocol PDF files using `pdfplumber`
- Uses an LLM to extract structured protocol information:
  - Protocol Number
  - Protocol Title
  - Protocol Versions (including amendments and changes affecting data analysis)
  - Protocol Design in Relation to ADaM Concepts
- Generates a markdown file in the ADRG protocol description format

**Usage:**
```bash
python -m protocol_retrieve.main --protocol inputs/protocol_cdiscpilot01.pdf --out outputs/protocol_description.md
```

**Options:**
- `--protocol PATH`: Path to protocol PDF file (required)
- `--out PATH`: Output markdown file (default: `protocol_description.md`)
- `--model NAME`: LLM model name to use (default: `gpt-4o-mini`)
- `--max-pages N`: Maximum number of pages to process (optional; useful for very long PDFs; default: all pages)

**Output:** Markdown file with sections for Protocol Number and Title, Protocol Versions, and Protocol Design in Relation to ADaM Concepts

**Example:**
```bash
python -m protocol_retrieve.main --protocol inputs/protocol_cdiscpilot01.pdf --out outputs/protocol_description.md --model gpt-4o-mini --max-pages 50
```

---

## Workflow Example

A typical workflow might involve:

1. **Extract R package versions:**
   ```bash
   python -m renv_to_table.main --renv inputs/renv.lock --out outputs/r_pkg_versions.csv
   ```

2. **Generate package descriptions:**
   ```bash
   Rscript pkg_describer/main.R --input outputs/r_pkg_versions.csv --output outputs/pkg_descriptions.csv
   ```

3. **Extract protocol information:**
   ```bash
   python -m protocol_retrieve.main --protocol inputs/protocol_cdiscpilot01.pdf --out outputs/protocol_description.md
   ```

4. **Extract SDTM/MedDRA versions:**
   ```bash
   python -m sdtm_medra_version.main --define inputs/define.xml --out outputs/standards_from_define.csv
   ```

5. **Analyze R scripts:**
   ```bash
   python -m var_filter.main --folder inputs/r_scripts --out outputs/output_var_filter_folder.csv
   ```

6. **Extract variable descriptions and dataset dependencies:**
   ```bash
   python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --input outputs/output_var_filter_folder.csv --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv
   ```

### Using `generate_adrg.py`

Once you have run the individual modules (or if you prefer to orchestrate them in one shot), you can create a filled ADRG document with `generate_adrg/main.py`:

1. Review or create a pipeline configuration JSON (see `adrg_doc/example_pipeline_config.json` for a relative-path example). Ensure it includes the sections `sdtm_medra_version`, `protocol_retrieve`, `var_filter`, `adam_info`, `renv_to_table`, `pkg_describer`, and `template` with appropriate inputs/outputs.
2. Run the generator:
   ```bash
   python generate_adrg/main.py --config adrg_doc/example_pipeline_config.json --skip-sdtm --skip-protocol --skip-var-filter --skip-adam-info --skip-renv --skip-pkg-describer
   ```
3. The script runs the SDTM/MedDRA, protocol, R-script analysis, ADaM variable summarisation, and R package documentation steps (unless skipped) and replaces the placeholders `{sdtm medra version table}`, `{protocol info md}`, `{analysis output table}`, `{variable description table}`, `{data dependency table}`, and `{r package table}` in the Quarto template `adrg_doc/adrg-template.qmd`. The ADaM step automatically feeds the `{analysis output table}` CSV into `adam_info` as the `--input` argument, while the R package documentation step runs `renv_to_table` followed by `pkg_describer` to convert `renv.lock` and describe the packages.
4. The filled ADRG document is written to the Quarto output path specified in the template configuration (e.g., `outputs/adrg-filled.qmd`). To render the filled document to PDF (or HTML), use the Quarto CLI. For example:

   ```bash
   quarto render outputs/adrg-filled.qmd --to pdf
   ```