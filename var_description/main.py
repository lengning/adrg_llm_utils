#!/usr/bin/env python3
"""
Extract variable descriptions from spec file based on variables found in filters.

Usage:
  python -m adam_info.main --input outputs/output_var_filter_folder.csv \
      --spec inputs/adam-pilot-5.xlsx --out outputs/var_descriptions.csv
"""

import argparse
import os
import re
import sys
from typing import Dict, Set, Tuple

import pandas as pd


def parse_variables_from_filters(filters_text: str) -> Set[Tuple[str, str]]:
    """
    Parse variable names from filter expressions.
    
    Args:
        filters_text: String containing filter expressions like "ADSL.STUDYID == 'CDISCPILOT01'"
        
    Returns:
        Set of tuples (dataset, variable) found in the filters
    """
    if pd.isna(filters_text) or not filters_text.strip():
        return set()
    
    # Pattern to match DATASET.VARIABLE (e.g., ADSL.STUDYID, ADLB.TRTPN)
    pattern = r'([A-Z][A-Z0-9]+)\.([A-Z][A-Z0-9]+)'
    matches = re.findall(pattern, filters_text)
    return set(matches)


def load_spec_mapping(spec_file: str) -> Dict[Tuple[str, str], str]:
    """
    Load variable descriptions from spec file.
    
    Args:
        spec_file: Path to Excel file with Variables sheet
        
    Returns:
        Dictionary mapping (dataset, variable) -> label
    """
    try:
        df = pd.read_excel(spec_file, sheet_name='Variables')
    except FileNotFoundError:
        sys.exit(f"ERROR: Spec file not found at: {spec_file}")
    except ValueError as e:
        sys.exit(f"ERROR: Could not read Variables sheet from {spec_file}: {e}")
    
    # Create mapping from (Dataset, Variable) to Label
    mapping = {}
    for _, row in df.iterrows():
        dataset = str(row['Dataset']).strip() if pd.notna(row['Dataset']) else None
        variable = str(row['Variable']).strip() if pd.notna(row['Variable']) else None
        label = str(row['Label']).strip() if pd.notna(row['Label']) else ''
        
        if dataset and variable:
            mapping[(dataset, variable)] = label
    
    return mapping


def map_dataset_name(dataset: str) -> str:
    """
    Map abbreviated dataset names to full names used in spec file.
    
    Common mappings:
    - ADAS -> ADADAS
    - ADLB -> ADLBC
    - ADTEE -> ADTTE
    - ADSL -> ADSL (no change)
    
    Args:
        dataset: Dataset name from filters
        
    Returns:
        Mapped dataset name
    """
    dataset_mappings = {
        'ADAS': 'ADADAS',
        'ADLB': 'ADLBC',
        'ADTEE': 'ADTTE',
        'ADSL': 'ADSL',
    }
    return dataset_mappings.get(dataset, dataset)


def extract_variable_descriptions(
    input_file: str,
    spec_file: str,
    output_file: str
) -> pd.DataFrame:
    """
    Extract variable descriptions from spec file based on variables in filters.
    
    Args:
        input_file: Path to CSV file with filters column
        spec_file: Path to Excel file with Variables sheet
        output_file: Path to output CSV file
        
    Returns:
        DataFrame with Variable Name and Variable Description columns
    """
    # Read input CSV
    try:
        input_df = pd.read_csv(input_file)
    except FileNotFoundError:
        sys.exit(f"ERROR: Input file not found at: {input_file}")
    
    if 'filters' not in input_df.columns:
        sys.exit(f"ERROR: Input file must have a 'filters' column. Found columns: {input_df.columns.tolist()}")
    
    # Load spec mapping
    spec_mapping = load_spec_mapping(spec_file)
    
    # Collect all unique variables from filters
    all_variables = set()
    for filters_text in input_df['filters']:
        variables = parse_variables_from_filters(filters_text)
        all_variables.update(variables)
    
    # Build output rows
    output_rows = []
    for dataset, variable in sorted(all_variables):
        # Try to find label with original dataset name first
        mapped_dataset = map_dataset_name(dataset)
        
        # Try both original and mapped dataset names
        label = None
        if (dataset, variable) in spec_mapping:
            label = spec_mapping[(dataset, variable)]
        elif (mapped_dataset, variable) in spec_mapping:
            label = spec_mapping[(mapped_dataset, variable)]
        else:
            # If not found, use empty string or a placeholder
            label = ''
        
        # Format variable name as DATASET.VARIABLE
        var_name = f"{dataset}.{variable}"
        output_rows.append({
            'Variable Name': var_name,
            'Variable Description': label
        })
    
    # Create output DataFrame
    output_df = pd.DataFrame(output_rows)
    
    # Write to CSV
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    output_df.to_csv(output_file, index=False)
    
    return output_df


def main():
    parser = argparse.ArgumentParser(
        description="Extract variable descriptions from spec file based on variables in filters"
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input CSV file with filters column (e.g., outputs/output_var_filter_folder.csv)'
    )
    parser.add_argument(
        '--spec',
        required=True,
        help='Path to spec Excel file with Variables sheet (e.g., inputs/adam-pilot-5.xlsx)'
    )
    parser.add_argument(
        '--out',
        required=True,
        help='Path to output CSV file'
    )
    parser.add_argument(
        '--print',
        action='store_true',
        help='Print results to stdout'
    )
    
    args = parser.parse_args()
    
    output_df = extract_variable_descriptions(args.input, args.spec, args.out)
    
    if args.print:
        print(output_df.to_string(index=False))
    
    print(f"Wrote {args.out} with {len(output_df)} variables.")


if __name__ == "__main__":
    main()

