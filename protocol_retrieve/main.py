#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from pathlib import Path
from typing import Dict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# ========= Prompt for Protocol Information Extraction =========
PROTOCOL_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert at extracting protocol information from clinical trial protocol documents. "
     "Extract the following information from the protocol text:\n"
     "- Protocol Number: The official protocol identifier/number\n"
     "- Protocol Title: The full title of the protocol\n"
     "- Protocol Versions: List any protocol versions, amendments, or version changes mentioned. "
     "Note any changes in protocol amendments that affected data analysis.\n"
     "- Protocol Design: Extract the following four subsections:\n"
     "  1) Protocol Objective: The primary objective of the study\n"
     "  2) Protocol Methodology: The methodology used in the study, including study design type, "
     "randomization, blinding, etc.\n"
     "  3) Number of Subjects Planned: Total number of subjects planned and breakdown by group/arm/treatment\n"
     "  4) Study Design Schema: A description or summary of the study design schema, including "
     "treatment groups, phases, periods, and how they relate to ADaM concepts (treatment, analysis period, analysis phase, etc.)\n\n"
     "Return a JSON object with the following keys: protocol_number, protocol_title, protocol_versions, "
     "protocol_objective, protocol_methodology, number_of_subjects, study_design_schema. "
     "If any information is not found, use an empty string for that field."),
    ("human",
     "Extract protocol information from the following protocol document text:\n\n{protocol_text}")
])

# ========= Builders =========
def build_llm(model="gpt-4o-mini", temperature=0):
    # Prefer reading API key from environment to avoid hardcoding secrets.
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)
    return ChatOpenAI(model=model, temperature=temperature)

def build_protocol_agent(llm):
    return PROTOCOL_EXTRACTION_PROMPT | llm | JsonOutputParser()

# ========= PDF Text Extraction =========
def extract_text_from_pdf(pdf_path: Path, max_pages: int = None) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        max_pages: Maximum number of pages to extract (None for all pages)
    
    Returns:
        Extracted text as a string
    """
    try:
        import pdfplumber
    except ImportError:
        print("Error: pdfplumber is required. Install it with: pip install pdfplumber", file=sys.stderr)
        sys.exit(1)
    
    text_parts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            pages_to_extract = min(max_pages, total_pages) if max_pages else total_pages
            
            for i in range(pages_to_extract):
                page = pdf.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            if max_pages and total_pages > max_pages:
                text_parts.append(f"\n[Note: Document has {total_pages} pages, but only first {max_pages} pages were processed]")
    
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")
    
    return "\n\n".join(text_parts)

# ========= Protocol Information Extraction =========
def extract_protocol_info(pdf_path: Path, llm, max_pages: int = None) -> Dict[str, str]:
    """
    Extract protocol information from a PDF using LLM.
    
    Args:
        pdf_path: Path to the protocol PDF file
        llm: Language model instance
        max_pages: Maximum number of pages to process (None for all pages)
    
    Returns:
        Dictionary with protocol information
    """
    print(f"Extracting text from PDF: {pdf_path}...", file=sys.stderr)
    protocol_text = extract_text_from_pdf(pdf_path, max_pages=max_pages)
    
    # Limit text length to avoid token limits (keep first 100k characters as a reasonable limit)
    if len(protocol_text) > 100000:
        print(f"Warning: Protocol text is very long ({len(protocol_text)} chars). "
              f"Truncating to first 100,000 characters.", file=sys.stderr)
        protocol_text = protocol_text[:100000] + "\n\n[Text truncated due to length]"
    
    print("Extracting protocol information using LLM...", file=sys.stderr)
    protocol_agent = build_protocol_agent(llm)
    
    try:
        result = protocol_agent.invoke({"protocol_text": protocol_text})
        return {
            "protocol_number": result.get("protocol_number", ""),
            "protocol_title": result.get("protocol_title", ""),
            "protocol_versions": result.get("protocol_versions", ""),
            "protocol_objective": result.get("protocol_objective", ""),
            "protocol_methodology": result.get("protocol_methodology", ""),
            "number_of_subjects": result.get("number_of_subjects", ""),
            "study_design_schema": result.get("study_design_schema", ""),
        }
    except Exception as e:
        print(f"Error extracting protocol information: {e}", file=sys.stderr)
        return {
            "protocol_number": "",
            "protocol_title": "",
            "protocol_versions": "",
            "protocol_objective": "",
            "protocol_methodology": "",
            "number_of_subjects": "",
            "study_design_schema": "",
        }

# ========= Markdown Generation =========
def generate_markdown(protocol_info: Dict[str, str]) -> str:
    """
    Generate markdown output in the specified format.
    
    Args:
        protocol_info: Dictionary with protocol information
    
    Returns:
        Formatted markdown string
    """
    markdown = """# Protocol Description

## ProtocolNumberand Title

Protocol Number: {protocol_number}

Protocol Title: {protocol_title}

Protocol Versions:

{protocol_versions}


## Protocol Designin Relation to ADaM Concepts

### 1) Protocol Objective

{protocol_objective}

### 2) Protocol Methodology

{protocol_methodology}

### 3) Number of Subjects Planned in Total and by Group

{number_of_subjects}

### 4) Study Design Schema

{study_design_schema}

""".format(
        protocol_number=protocol_info.get("protocol_number", ""),
        protocol_title=protocol_info.get("protocol_title", ""),
        protocol_versions=protocol_info.get("protocol_versions", ""),
        protocol_objective=protocol_info.get("protocol_objective", ""),
        protocol_methodology=protocol_info.get("protocol_methodology", ""),
        number_of_subjects=protocol_info.get("number_of_subjects", ""),
        study_design_schema=protocol_info.get("study_design_schema", ""),
    )
    
    return markdown

# ========= Main Function =========
def main():
    ap = argparse.ArgumentParser(
        description="Extract protocol information from a PDF and generate a markdown file."
    )
    ap.add_argument(
        "--protocol",
        required=True,
        type=Path,
        help="Path to protocol PDF file"
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("protocol_description.md"),
        help="Output markdown file (default: protocol_description.md)"
    )
    ap.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="LLM model name to use (default: gpt-4o-mini)"
    )
    ap.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum number of pages to process (default: all pages)"
    )
    args = ap.parse_args()

    # Validate input file
    if not args.protocol.exists():
        print(f"Error: Protocol PDF file not found: {args.protocol}", file=sys.stderr)
        sys.exit(1)

    # Build LLM
    llm = build_llm(model=args.model, temperature=0)

    # Extract protocol information
    protocol_info = extract_protocol_info(
        args.protocol,
        llm,
        max_pages=args.max_pages
    )

    # Generate markdown
    markdown = generate_markdown(protocol_info)

    # Write output
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown, encoding="utf-8")
    print(f"Wrote protocol description to: {args.out}", file=sys.stderr)

if __name__ == "__main__":
    main()

