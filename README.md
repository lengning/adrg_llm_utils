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
python -m var_filter.main --folder ./r_scripts --out audit.csv --print
```

Analyze a single `.r` file:

```bash
python -m var_filter.main --file r_scripts/tlf-demographic.r --out one_row.csv --print
```

Choose a specific model (default is `gpt-4o-mini`):

```bash
python -m var_filter.main --folder ./r_scripts --model gpt-4o-mini
```


The tool writes a CSV file with columns: `r_file`, `outputs`, `filters`, `variables`.

### Next module
