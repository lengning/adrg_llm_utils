# Utility Modules for LLM-automated ADRG generation

These utility modules provide the scaffolding for LLM-automated ADRG generation. The ADRG (Analysis Data Reviewer’s Guide) is a companion document that explains the contents, derivations, structure, and intended use of submitted ADaM analysis datasets—capturing provenance, conventions, and known limitations—to help regulators understand and reproduce results.

[Example ADRG](https://github.com/RConsortium/submissions-pilot5-datasetjson-to-fda/blob/main/m5/datasets/rconsortiumpilot5/analysis/adam/datasets/adrg.pdf)

## Requirements

- Python 3.8+
- `pandas`
- `langchain_openai` and `langchain_core` (the code uses `ChatOpenAI` and `ChatPromptTemplate`)

Install required packages (example):

```bash
pip install pandas langchain-openai langchain-core
```

Note: package names may differ depending on your environment. Adjust as needed.

## Configuration

The script will try to read an OpenAI API key from the `OPENAI_API_KEY` environment variable. Set it like this in macOS/zsh:

```bash
export OPENAI_API_KEY="sk-..."
```

If the environment variable is not set, the underlying `ChatOpenAI` client will use its default behavior for locating credentials.

## Modules and Their Usage

### var_filter: 

This repository contains a small tool to audit R scripts and extract three items using an LLM:
- filtering criteria (filters)
- variables used (variables)
- output file names (outputs)

Analyze a folder of `.r` files:

```bash
python -m var_filter.main --folder ./r_scripts --out outputs/output_var_filter_folder.csv --print
```

Analyze a single `.r` file:

```bash
python -m var_filter.main --file r_scripts/tlf-demographic.r --out outputs/output_var_filter_file.csv --print
```

Choose a specific model (default is `gpt-4o-mini`):

```bash
python -m var_filter.main --folder ./r_scripts --model gpt-4o-mini
```


The tool writes a CSV file with columns: `r_file`, `outputs`, `filters`, `variables`.

### Convert renv to a table with package names and versions

A tiny CLI to convert an R renv.lock into a tidy CSV of package names and versions for ADRG workflows.

What it does

- Reads renv.lock (JSON)
- Extracts all packages and their versions (skips the R runtime entry)
- Writes a sorted R_Packages_And_Versions.csv with headers: Package,Version

```bash
python -m renv_to_table.main --renv inputs/renv.lock --out outputs/r_pkg_versions.csv
```

### Write user-friendly package descriptions

This CLI reads a CSV of R package names, fetches each package's CRAN `DESCRIPTION` file,
optionally runs an LLM to produce a one-sentence summary, and writes an output CSV with
`Package`, `Version`, and `Description`.


```bash
Rscript pkg_describer/main.R --input outputs/pkg_descriptions.csv --output outputs/pkg_descriptions.csv
```

If you want to skip LLM calls and only use the CRAN DESCRIPTION text, pass `--no-llm`.

Environment variables:
- `MODEL_NAME` - optional default model name (e.g. `gpt-4o-mini`). Can also be passed via `-m`.

Notes:
- An R script is used instead of python because of the convinience of using `tools` and `btw` r packages

