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
python -m var_filter.main --folder inputs/tlf_scripts --out outputs/output_var_filter_folder.csv
```

Analyze a single `.r` file:
```bash
python -m var_filter.main --file inputs/tlf_scripts/tlf-demographic.r --out outputs/output_var_filter_file.csv
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
python -m var_filter.main --folder inputs/tlf_scripts --out outputs/output_var_filter_folder.csv --model gpt-4o-mini --print
```

---

### adam_info

**Description:** Extracts variable descriptions from ADaM spec files, analyzes dataset dependencies by examining the Methods sheet, and generates a dataset inventory table.

**What it does:**
- Reads ADaM specification Excel files (with Datasets, Variables, and Methods sheets)
- Extracts variable descriptions for key variables or variables from an input CSV file
- Analyzes the Methods sheet to determine dataset dependencies
- Outputs unique variable names (without dataset prefix) with their descriptions
- Generates a dataset dependency table showing which datasets depend on which other datasets
- **NEW**: Generates a dataset inventory table with purpose flags (Efficacy, Safety, PK/PD, etc.)

**Usage:**

Extract variable descriptions from key variables in Datasets sheet:
```bash
python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv --inventory-out outputs/dataset_inventory.csv
```

Extract variable descriptions from variables in an input CSV file (e.g., from var_filter output):
```bash
python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --input outputs/output_var_filter_folder.csv --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv --inventory-out outputs/dataset_inventory.csv
```

**Options:**
- `--spec PATH`: Path to ADaM spec Excel file with Datasets, Variables, and Methods sheets (required)
- `--out PATH`: Path to output CSV file for variable descriptions (required)
- `--input PATH`: Optional path to input CSV file with `variables` column (e.g., output from `var_filter`). If not provided, uses key variables from Datasets sheet.
- `--deps-out PATH`: Optional path to output CSV file for dataset dependencies
- `--inventory-out PATH`: Optional path to output CSV file for dataset inventory table
- `--print`: Print results to stdout

**Output:**
- Variable descriptions CSV: `Variable Name`, `Variable Description` (unique variables without dataset prefix)
- Dataset dependencies CSV (if `--deps-out` provided): `dataset name`, `depend on the following datasets`
- Dataset inventory CSV (if `--inventory-out` provided): Dataset inventory table with purpose flags (Efficacy, Safety, Baseline/subject characteristics, PK/PD, Primary Objective) and structure

**Notes:**
- Variables are extracted as unique names (dataset prefix removed)
- Dataset dependencies are inferred by analyzing references in the Methods sheet
- If a variable appears in multiple datasets, only one entry is output (first description found)

**Example:**
```bash
# Extract from key variables in Datasets sheet
python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv --inventory-out outputs/dataset_inventory.csv --print

# Extract from variables found in R scripts (via var_filter output)
python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --input outputs/output_var_filter_folder.csv --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv --inventory-out outputs/dataset_inventory.csv --print
```

---

### adam_scripts_analyzer

**Description:** Analyzes ADaM R scripts to extract program names, output files, and dataset descriptions.

**What it does:**
- Scans a directory of R scripts (`.r` or `.R` files)
- Extracts program names (from filenames)
- Identifies output files generated by each script (e.g., saveRDS, write.csv)
- Retrieves dataset descriptions from ADaM specification file
- Generates a table documenting the analysis programs with their descriptions

**Usage:**

Analyze ADaM R scripts with dataset descriptions:
```bash
python -m adam_scripts_analyzer.main --scripts-dir inputs/adam_scripts --out outputs/adam_programs.csv --spec inputs/adam-pilot-5.xlsx
```

Analyze without spec file (descriptions will be empty):
```bash
python -m adam_scripts_analyzer.main --scripts-dir inputs/adam_scripts --out outputs/adam_programs.csv
```

**Options:**
- `--scripts-dir PATH`: Path to directory containing ADaM R scripts (required)
- `--out PATH`: Path to output CSV file (required)
- `--spec PATH`: Path to ADaM specification Excel file for dataset descriptions (optional)

**Output:** CSV file with columns: `Program Name`, `Output`, `Dataset Description`

**Example:**
```bash
python -m adam_scripts_analyzer.main --scripts-dir inputs/adam_scripts --out outputs/adam_programs.csv --spec inputs/adam-pilot-5.xlsx
```

**Notes:**
- The module analyzes both header comments and actual code to extract outputs
- Dataset descriptions are retrieved from the "Datasets" sheet in the ADaM spec file
- Program names are matched to dataset names (e.g., `adsl.r` → `ADSL` dataset)
- Supports common R save functions: saveRDS, write.csv, write_csv, xpt_write, write_xpt

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

### adrg_question_filler

**Description:** Intelligently fills in yes/no questions in the ADRG template by analyzing pipeline data files and using LLM to answer questions automatically.

**What it does:**
- Automatically detects all `<Yes/No>` placeholders in the ADRG template
- Analyzes multiple data sources from both **input** and **output** files:
  - **Output files**: Protocol descriptions, variable descriptions, dataset dependencies, analysis program details, R packages
  - **Input files**: define.xml (metadata), ADaM spec XLSX (detailed specifications), renv.lock (R environment), R scripts (sample code)
- Uses LLM to intelligently interpret data and answer yes/no questions
- Skips questions that cannot be answered automatically (keeps `<Yes/No>` placeholder)

**Usage:**

Basic usage:
```bash
python adrg_question_filler/main.py
```

Custom configuration:
```bash
python adrg_question_filler/main.py \
  --config path/to/config.json \
  --template path/to/template.qmd \
  --out path/to/output.qmd \
  --model gpt-4o
```

**Options:**
- `--config PATH`: Path to pipeline configuration JSON (default: `adrg_doc/example_pipeline_config.json`)
- `--template PATH`: Path to ADRG template file (default: `adrg_doc/adrg-template.qmd`)
- `--out PATH`: Output path for filled template (default: `outputs/adrg-filled.qmd`)
- `--model NAME`: OpenAI model to use (default: `gpt-4o-mini`)

**Questions typically answered:**
- Treatment variable equivalence (ARM vs TRTxxP, ACTARM vs TRTxxA)
- Use of planned vs actual treatment variables
- Treatment grouping variables usage
- Windowing usage (if data available)
- Unscheduled visits (if data available)
- Date imputation rules (if documented)
- Screen failure data inclusion (if data available)
- Ongoing study status (if documented in protocol)
- Protocol objective support (if analysis complete)

**Output:** Filled ADRG template with `<Yes/No>` markers replaced by actual answers and explanations. The output file overwrites or is written to the path specified by `--out`.

**Example:**

Input template:
```markdown
- ARM versus TRTxxP
Are the values of ARM equivalent in meaning to values of TRTxxP?
<Yes/No> (insert additional text here)
```

Filled output:
```markdown
- ARM versus TRTxxP
Are the values of ARM equivalent in meaning to values of TRTxxP?
**Yes.** In this study, the treatment groups include placebo, xanomeline low dose,
and xanomeline high dose, which are reflected in both ARM and TRTxxP variables.
```

**Notes:**
- Run after the main pipeline to ensure all data files are available
- **Enhanced context**: Reads both input files (XML, XLSX, JSON, R scripts) and output files for comprehensive data analysis
- Questions that cannot be answered automatically will retain their `<Yes/No>` placeholder
- Answers are formatted as **bold** (e.g., `**Yes.**` or `**No.**`) followed by explanation text
- Review LLM-generated answers before finalizing the document
- For better accuracy, consider using GPT-4 with `--model gpt-4o`
- When integrated with `generate_adrg`, the output file is overwritten in place
- **Typical success rate**: 5-7 out of 10 questions answered automatically (depending on data availability)

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
   python -m var_filter.main --folder inputs/tlf_scripts --out outputs/output_var_filter_folder.csv
   ```

6. **Extract variable descriptions, dataset dependencies, and dataset inventory:**
   ```bash
   python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --input outputs/output_var_filter_folder.csv --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv --inventory-out outputs/dataset_inventory.csv
   ```

7. **Analyze ADaM R scripts:**
   ```bash
   python -m adam_scripts_analyzer.main --scripts-dir inputs/adam_scripts --out outputs/adam_programs.csv --spec inputs/adam-pilot-5.xlsx
   ```

### Using `generate_adrg.py`

Once you have run the individual modules (or if you prefer to orchestrate them in one shot), you can create a filled ADRG document with `generate_adrg/main.py`:

1. Review or create a pipeline configuration JSON (see `adrg_doc/example_pipeline_config.json` for a relative-path example). Ensure it includes the sections `sdtm_medra_version`, `protocol_retrieve`, `var_filter`, `adam_info`, `adam_scripts_analyzer`, `renv_to_table`, `pkg_describer`, and `template` with appropriate inputs/outputs.

2. Run the generator:
   ```bash
   python generate_adrg/main.py --config adrg_doc/example_pipeline_config.json
   ```

3. To include automatic yes/no question filling, add the `--fill-questions` flag:
   ```bash
   python generate_adrg/main.py --config adrg_doc/example_pipeline_config.json --fill-questions
   ```

   Options for question filling:
   - `--fill-questions`: Enable yes/no question filling
   - `--question-model MODEL`: Specify LLM model for questions (default: gpt-4o-mini)

4. If you already have output files from previous runs, skip steps using flags:
   ```bash
   python generate_adrg/main.py --config adrg_doc/example_pipeline_config.json \
     --skip-sdtm --skip-protocol --skip-var-filter --skip-adam-info \
     --skip-adam-scripts --skip-renv --skip-pkg-describer --fill-questions
   ```

5. The script runs the SDTM/MedDRA, protocol, R-script analysis, ADaM variable summarisation, ADaM scripts analysis, and R package documentation steps (unless skipped) and replaces the placeholders `{sdtm medra version table}`, `{protocol info md}`, `{analysis output table}`, `{variable description table}`, `{data dependency table}`, `{dataset inventory table}`, `{adam programs table}`, and `{r package table}` in the Quarto template `adrg_doc/adrg-template.qmd`. The ADaM step automatically feeds the `{analysis output table}` CSV into `adam_info` as the `--input` argument, generates the dataset inventory table with purpose flags, while the ADaM scripts analyzer extracts program information from R scripts in `inputs/adam_scripts`, and the R package documentation step runs `renv_to_table` followed by `pkg_describer` to convert `renv.lock` and describe the packages.

6. The filled ADRG document is written to the Quarto output path specified in the template configuration (e.g., `outputs/adrg-filled.qmd`). If `--fill-questions` is specified, the yes/no questions are filled in the same file.

7. To render the filled document to PDF (or HTML), use the Quarto CLI:
   ```bash
   quarto render outputs/adrg-filled.qmd --to pdf
   ```

## Multi-Agent Workflow (NEW!)

The project now includes a **multi-agent framework** that redesigns the workflow using specialized agents that work collaboratively. This provides better organization, parallel task execution capabilities, and clearer separation of concerns.

### Agent Architecture

The multi-agent system consists of 7 specialized agents:

1. **Definexml Extraction Agent**
   - **Role**: SDTM/MedDRA Metadata Specialist
   - **Responsibility**: Extract study standards and versions from define.xml files
   - **Tools**: XML parser, define.xml reader
   - **Output**: SDTM/MedDRA version table

2. **Protocol Analysis Agent**
   - **Role**: Clinical Protocol Analyst
   - **Responsibility**: Extract and summarize protocol information from PDF documents
   - **Tools**: PDF reader, LLM summarizer
   - **Output**: Protocol description markdown

3. **Code Analysis Agent**
   - **Role**: R Programming Specialist
   - **Responsibility**: Analyze R scripts (both TLF and ADaM) to extract variables, outputs, and functions
   - **Tools**: R script parser, function extractor, var_filter, adam_scripts_analyzer
   - **Output**: Analysis output table, ADaM programs table

4. **ADaM Specification Agent**
   - **Role**: ADaM Standards Expert
   - **Responsibility**: Process ADaM specification Excel files
   - **Tools**: Excel reader, variable extractor, dependency analyzer
   - **Output**: Variable descriptions, dataset dependencies, dataset inventory

5. **Package Documentation Agent**
   - **Role**: R Package Documentation Specialist
   - **Responsibility**: Document R packages and their versions
   - **Tools**: renv.lock parser, package describer, CRAN API
   - **Output**: R package table with descriptions

6. **Question Answering Agent**
   - **Role**: ADRG Question Specialist
   - **Responsibility**: Answer yes/no questions in ADRG templates using available data
   - **Tools**: LLM QA, data context builder, template parser
   - **Output**: Answered questions in template

7. **Document Assembly Agent**
   - **Role**: Document Integration Coordinator
   - **Responsibility**: Assemble all components into final ADRG document
   - **Tools**: Template filler, markdown renderer, CSV to table converter
   - **Output**: Filled ADRG document

### Task Dependencies

The workflow manages task dependencies automatically:

```
┌─────────────────────┐
│ Definexml Extraction│ (Independent)
└─────────┬───────────┘
          │
┌─────────────────────┐
│ Protocol Analysis   │ (Independent)
└─────────┬───────────┘
          │
┌─────────────────────┐
│ TLF Script Analysis │ (Independent)
└─────────┬───────────┘
          │
          ├─────────────────────────────┐
          │                             │
┌─────────▼───────────┐       ┌─────────▼───────────┐
│ ADaM Info Extract   │       │ ADaM Scripts Analyze│
└─────────┬───────────┘       └─────────┬───────────┘
          │                             │
┌─────────────────────┐                 │
│ Package Doc (renv)  │ (Independent)   │
└─────────┬───────────┘                 │
          │                             │
┌─────────▼───────────┐                 │
│ Package Descriptions│                 │
└─────────┬───────────┘                 │
          │                             │
          └─────────────┬───────────────┘
                        │
              ┌─────────▼───────────┐
              │ Document Assembly   │
              └─────────┬───────────┘
                        │
              ┌─────────▼───────────┐
              │ Question Answering  │ (Optional)
              └─────────────────────┘
```

### Usage

Run the multi-agent workflow:

```bash
python multi_agent_adrg/main.py --config adrg_doc/example_pipeline_config.json
```

With question filling:
```bash
python multi_agent_adrg/main.py --config adrg_doc/example_pipeline_config.json --fill-questions
```

Skip specific tasks:
```bash
python multi_agent_adrg/main.py --config adrg_doc/example_pipeline_config.json \
  --skip-sdtm --skip-protocol --skip-var-filter \
  --skip-adam-info --skip-adam-scripts --skip-renv --skip-pkg-describer
```

### Benefits of Multi-Agent Approach

1. **Clear Separation of Concerns**: Each agent has a specific role and responsibility
2. **Easier Maintenance**: Changes to one agent don't affect others
3. **Better Error Handling**: Failed tasks are isolated and reported clearly
4. **Extensibility**: Easy to add new agents or modify existing ones
5. **Dependency Management**: Automatic task ordering based on dependencies
6. **Parallel Execution Ready**: Framework supports parallel task execution where dependencies allow
7. **Better Logging**: Each agent provides detailed progress updates
8. **Professional Architecture**: Follows agent-based system design patterns

### Agent Framework Features

The custom agent framework (`multi_agent_adrg/agent_framework.py`) provides:

- **Agent Class**: Represents specialized workers with roles, goals, and tools
- **Task Class**: Encapsulates work units with dependencies and actions
- **Crew Class**: Orchestrates agents and manages workflow execution
- **Task Status Tracking**: PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
- **Dependency Resolution**: Automatic task ordering based on dependencies
- **Context Passing**: Agents can access outputs from previous tasks
- **Skip Flags**: Ability to skip individual tasks
- **Verbose Logging**: Detailed progress tracking

### Comparison: Traditional vs Multi-Agent

| Aspect | Traditional Pipeline | Multi-Agent Workflow |
|--------|---------------------|---------------------|
| Architecture | Sequential script execution | Agent-based collaborative system |
| Code Organization | Procedural functions | Object-oriented agents |
| Error Handling | Try-catch blocks | Task-level failure isolation |
| Extensibility | Add new functions | Add new agents with minimal changes |
| Dependency Management | Manual ordering | Automatic resolution |
| Progress Tracking | Print statements | Structured agent logging |
| Testability | Integration tests | Unit test per agent/task |
| Maintainability | Good | Excellent |