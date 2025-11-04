import os, glob
from typing import List
import pandas as pd

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# ========= Prompts (Agents) =========
VARIABLE_PROMPT = ChatPromptTemplate.from_messages([
    ("Please review the following R code and identify the variables used for analyses. When outputing variable name, parsing the associated data set name and the variable name, seperated by a dot,"
    "and captialize all characters. Please use the initial source dataset names instead of the intermediate dataset names. no explanation please. "
    "please ensure the condition is included. no line break please. seperate values by ;."
    "only include the variables from datasets whose dataset name starting with the letter a. "),
    ("human",
     "R file: {file}\n\nR code:\n```r\n{code}\n```\n"
     "Return JSON with keys: file, variables (array of strings).")
])

FILTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
    "Please review the following R code and identify the filtering criteria applied. When outputing variable name, parsing the associated data set name and the variable name, seperated by a dot,"
    "and captialize all characters. Please use the initial source dataset names instead of the intermediate dataset names. no explanation please. "
    "please ensure the condition is included. no line break please. seperate values by ;."),
    ("human",
     "R file: {file}\n\nR code:\n```r\n{code}\n```\n"
     "Return JSON with keys: file, filters (array of strings).")
])

OUTPUT_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Please review the following R code and identify the output file name. no explanation please. "),
    ("human",
     "R file: {file}\n\nR code:\n```r\n{code}\n```\n"
     "Return JSON with keys: file, outputs (array of strings).")
])

# ========= Builders =========
def build_llm(model="gpt-4o-mini", temperature=0):
    # Prefer reading API key from environment to avoid hardcoding secrets.
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)
    return ChatOpenAI(model=model, temperature=temperature)

def build_filter_agent(llm):
    return FILTER_PROMPT | llm | JsonOutputParser()

def build_variable_agent(llm):
    return VARIABLE_PROMPT | llm | JsonOutputParser()

def build_output_agent(llm):
    return OUTPUT_PROMPT | llm | JsonOutputParser()

# ========= Orchestration =========
def analyze_r_file(file_path: str, llm) -> dict:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
        code = fh.read()
    filename = os.path.basename(file_path)
    filter_agent = build_filter_agent(llm)
    variable_agent = build_variable_agent(llm)
    output_agent = build_output_agent(llm)
    try:
        filt = filter_agent.invoke({"file": filename, "code": code})
    except Exception:
        filt = {"file": filename, "filters": []}
    try:
        vars = variable_agent.invoke({"file": filename, "code": code})
    except Exception:
        vars = {"file": filename, "variables": []}
    try:
        outs = output_agent.invoke({"file": filename, "code": code})
    except Exception:
        outs = {"file": filename, "outputs": []}
    return {
        "r_file": filename,
        "outputs": "; ".join(outs.get("outputs", [])),
        "filters": "; ".join(filt.get("filters", [])),
        "variables": "; ".join(vars.get("variables", [])),
    }

def audit_folder(folder: str, model="gpt-4o-mini") -> List[dict]:
    files = sorted(glob.glob(os.path.join(folder, "**", "*.r"), recursive=True))
    if not files:
        raise FileNotFoundError(f"No .r files found under: {folder}")
    llm = build_llm(model=model, temperature=0)
    return [analyze_r_file(f, llm) for f in files]

def to_table(reports: List[dict]) -> pd.DataFrame:
    return pd.DataFrame(reports, columns=["r_file", "outputs", "filters", "variables"])


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Audit R scripts (folder or single file)")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--folder", help="Path to folder containing .r files")
    group.add_argument("--file", help="Path to a single .r file to analyze")
    ap.add_argument("--model", default="gpt-4o-mini", help="LLM model name to use")
    ap.add_argument("--out", default="r_code_audit.csv", help="Output CSV filename (for folder results)")
    ap.add_argument("--print", action="store_true", help="Print results to stdout")
    args = ap.parse_args()

    if args.file:
        llm = build_llm(model=args.model, temperature=0)
        report = analyze_r_file(args.file, llm)
        df = to_table([report])
        if args.print:
            print(df.to_string(index=False))
        df.to_csv(args.out, index=False)
        print(f"Wrote {args.out} (1 row) for file: {args.file}")
    else:
        # folder
        reports = audit_folder(args.folder, model=args.model)
        df = to_table(reports)
        df.to_csv(args.out, index=False)
        if args.print:
            print(df.to_string(index=False))
        print(f"Wrote {args.out} with {len(df)} rows.")
