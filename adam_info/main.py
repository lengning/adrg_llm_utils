#!/usr/bin/env python3
"""
Extract variable descriptions from spec file based on key variables from Datasets sheet.
Analyze Methods sheet to determine dataset dependencies.
Generate dataset inventory table with purpose flags.

Usage:
  # Using key variables from Datasets sheet:
  python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv --inventory-out outputs/dataset_inventory.csv

  # Using variables from input CSV file:
  python -m adam_info.main --spec inputs/adam-pilot-5.xlsx --input outputs/output_var_filter_file.csv --out outputs/var_descriptions.csv --deps-out outputs/dataset_dependencies.csv --inventory-out outputs/dataset_inventory.csv
"""

import argparse
import os
import re
import sys
from typing import Dict, List, Set, Tuple

import pandas as pd


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


def extract_key_variables_from_datasets(spec_file: str) -> Set[Tuple[str, str]]:
    """
    Extract key variables from the Datasets sheet.
    
    Args:
        spec_file: Path to Excel file with Datasets sheet
        
    Returns:
        Set of tuples (dataset, variable) for key variables
    """
    try:
        df = pd.read_excel(spec_file, sheet_name='Datasets')
    except FileNotFoundError:
        sys.exit(f"ERROR: Spec file not found at: {spec_file}")
    except ValueError as e:
        sys.exit(f"ERROR: Could not read Datasets sheet from {spec_file}: {e}")
    
    if 'Key Variables' not in df.columns:
        sys.exit(f"ERROR: Datasets sheet must have a 'Key Variables' column. Found columns: {df.columns.tolist()}")
    
    if 'Dataset' not in df.columns:
        sys.exit(f"ERROR: Datasets sheet must have a 'Dataset' column. Found columns: {df.columns.tolist()}")
    
    key_variables = set()
    
    for _, row in df.iterrows():
        dataset = str(row['Dataset']).strip() if pd.notna(row['Dataset']) else None
        key_vars_str = row['Key Variables'] if pd.notna(row['Key Variables']) else None
        
        if dataset and key_vars_str:
            # Parse comma-separated variable names
            variables = [v.strip() for v in str(key_vars_str).split(',')]
            for variable in variables:
                if variable:  # Skip empty strings
                    key_variables.add((dataset, variable))
    
    return key_variables


def extract_dataset_dependencies_from_methods(spec_file: str) -> Dict[str, Set[str]]:
    """
    Analyze Methods sheet to determine which datasets depend on which other datasets.
    
    Args:
        spec_file: Path to Excel file with Methods and Datasets sheets
        
    Returns:
        Dictionary mapping dataset -> set of dependent datasets
    """
    try:
        methods_df = pd.read_excel(spec_file, sheet_name='Methods')
        datasets_df = pd.read_excel(spec_file, sheet_name='Datasets')
    except FileNotFoundError:
        sys.exit(f"ERROR: Spec file not found at: {spec_file}")
    except ValueError as e:
        sys.exit(f"ERROR: Could not read required sheets from {spec_file}: {e}")
    
    # Get all dataset names
    all_datasets = set(datasets_df['Dataset'].dropna().str.strip().unique())
    
    # Initialize dependencies - each dataset starts with no dependencies
    dependencies: Dict[str, Set[str]] = {ds: set() for ds in all_datasets}
    
    # Pattern to match DATASET.VARIABLE format
    dataset_var_pattern = r'\b([A-Z]{2,5})\.([A-Z][A-Z0-9]+)\b'
    
    # Analyze each method
    for _, row in methods_df.iterrows():
        method_id = row['ID'] if pd.notna(row['ID']) else ''
        
        # Extract target dataset from method ID (e.g., ADADAS.ADT -> ADADAS)
        if '.' not in str(method_id):
            continue
        
        target_dataset = str(method_id).split('.')[0].strip()
        
        # Skip if target dataset is not in our list
        if target_dataset not in all_datasets:
            continue
        
        # Check Description column for dataset references
        if pd.notna(row['Description']):
            desc = str(row['Description'])
            # Find all DATASET.VARIABLE patterns
            matches = re.findall(dataset_var_pattern, desc)
            for dataset, variable in matches:
                dataset = dataset.strip()
                # If we found a reference to another dataset (not the target itself)
                if dataset in all_datasets and dataset != target_dataset:
                    dependencies[target_dataset].add(dataset)
        
        # Check Expression Code column if it exists
        if 'Expression Code' in methods_df.columns and pd.notna(row.get('Expression Code')):
            expr = str(row['Expression Code'])
            matches = re.findall(dataset_var_pattern, expr)
            for dataset, variable in matches:
                dataset = dataset.strip()
                if dataset in all_datasets and dataset != target_dataset:
                    dependencies[target_dataset].add(dataset)
        
        # Also check for dataset references in other formats
        # Look for patterns like "from ADSL" or "ADSL dataset" or "ADSL data"
        if pd.notna(row['Description']):
            desc = str(row['Description'])
            for dataset in all_datasets:
                if dataset != target_dataset:
                    # Look for dataset name in various contexts
                    patterns = [
                        rf'\bfrom\s+{dataset}\b',
                        rf'\b{dataset}\s+dataset\b',
                        rf'\b{dataset}\s+data\b',
                        rf'\b{dataset}\s+table\b',
                        rf'\bjoin.*{dataset}\b',
                        rf'\bmerge.*{dataset}\b',
                    ]
                    for pattern in patterns:
                        if re.search(pattern, desc, re.IGNORECASE):
                            dependencies[target_dataset].add(dataset)
                            break
    
    return dependencies


def parse_variables_from_input_csv(input_file: str) -> Set[Tuple[str, str]]:
    """
    Parse variables from input CSV file (like output_var_filter_file.csv).
    
    Args:
        input_file: Path to CSV file with 'variables' column containing DATASET.VARIABLE format
        
    Returns:
        Set of tuples (dataset, variable) found in the input file
    """
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        sys.exit(f"ERROR: Input file not found at: {input_file}")
    
    if 'variables' not in df.columns:
        sys.exit(f"ERROR: Input file must have a 'variables' column. Found columns: {df.columns.tolist()}")
    
    variables = set()
    dataset_var_pattern = r'\b([A-Z]{2,5})\.([A-Z][A-Z0-9]+)\b'
    
    for _, row in df.iterrows():
        vars_text = row['variables'] if pd.notna(row['variables']) else ''
        if vars_text:
            # Find all DATASET.VARIABLE patterns
            matches = re.findall(dataset_var_pattern, str(vars_text))
            for dataset, variable in matches:
                variables.add((dataset.strip(), variable.strip()))
    
    return variables


def extract_variable_descriptions(
    spec_file: str,
    output_file: str,
    input_file: str = None
) -> pd.DataFrame:
    """
    Extract variable descriptions from spec file.
    If input_file is provided, extract variables from that CSV file.
    Otherwise, extract key variables from Datasets sheet.
    Output only unique variable names (without dataset prefix).
    
    Args:
        spec_file: Path to Excel file with Datasets and Variables sheets
        output_file: Path to output CSV file
        input_file: Optional path to CSV file with variables column (e.g., output_var_filter_file.csv)
        
    Returns:
        DataFrame with Variable Name and Variable Description columns
    """
    # Load spec mapping
    spec_mapping = load_spec_mapping(spec_file)
    
    # Extract variables from input file or from Datasets sheet
    if input_file:
        variables = parse_variables_from_input_csv(input_file)
    else:
        variables = extract_key_variables_from_datasets(spec_file)
    
    # Build a dictionary of unique variables (variable_name -> description)
    # If a variable appears in multiple datasets, use the first description found
    unique_variables: Dict[str, str] = {}
    
    for dataset, variable in sorted(variables):
        # Look up description from Variables sheet
        # Try to find description for this dataset-variable pair
        label = spec_mapping.get((dataset, variable), '')
        
        # If not found, try to find in any dataset with the same variable name
        if not label:
            for (ds, var), desc in spec_mapping.items():
                if var == variable and desc:
                    label = desc
                    break
        
        # Only add if we haven't seen this variable name before
        # (variables with the same name across datasets should have the same description)
        if variable not in unique_variables:
            unique_variables[variable] = label
        elif not unique_variables[variable] and label:
            # If we have an empty description but found one later, use it
            unique_variables[variable] = label
    
    # Build output rows from unique variables
    output_rows = []
    for variable in sorted(unique_variables.keys()):
        output_rows.append({
            'Variable Name': variable,
            'Variable Description': unique_variables[variable]
        })
    
    # Create output DataFrame
    output_df = pd.DataFrame(output_rows)
    
    # Write to CSV
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    output_df.to_csv(output_file, index=False)
    
    return output_df


def extract_dataset_dependencies(
    spec_file: str,
    output_file: str
) -> pd.DataFrame:
    """
    Extract dataset dependencies by analyzing Methods sheet.
    
    Args:
        spec_file: Path to Excel file with Datasets and Methods sheets
        output_file: Path to output CSV file
        
    Returns:
        DataFrame with dataset name and dependencies columns
    """
    # Get dependencies from Methods sheet
    dependencies = extract_dataset_dependencies_from_methods(spec_file)
    
    # Build output rows
    output_rows = []
    for dataset in sorted(dependencies.keys()):
        deps = sorted(dependencies[dataset])
        deps_str = ', '.join(deps) if deps else ''
        output_rows.append({
            'dataset name': dataset,
            'depend on the following datasets': deps_str
        })
    
    # Create output DataFrame
    output_df = pd.DataFrame(output_rows)
    
    # Write to CSV
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    output_df.to_csv(output_file, index=False)
    
    return output_df


def determine_dataset_purpose(dataset_name: str, label: str, class_name: str) -> Dict[str, str]:
    """
    Determine the purpose flags for a dataset based on its name, label, and class.

    Args:
        dataset_name: Dataset name (e.g., ADSL, ADAE, ADADAS)
        label: Dataset label/description
        class_name: ADaM class (e.g., ADSL, BDS, OCCDS)

    Returns:
        Dictionary with purpose flags (Efficacy, Safety, etc.)
    """
    dataset_upper = dataset_name.upper()
    label_lower = label.lower() if pd.notna(label) else ''
    class_upper = class_name.upper() if pd.notna(class_name) else ''

    purposes = {
        'Efficacy': '',
        'Safety': '',
        'Baseline or other subject characteristics': '',
        'PK/PD': '',
        'Primary Objective': ''
    }

    # ADSL is always for subject characteristics
    if dataset_upper == 'ADSL':
        purposes['Baseline or other subject characteristics'] = 'X'
        return purposes

    # Safety datasets - typically adverse events, concomitant meds, etc.
    safety_indicators = ['adverse', 'ae', 'safety', 'conmed', 'medication', 'vital']
    if any(ind in dataset_upper.lower() for ind in ['adae', 'adcm', 'advs']):
        purposes['Safety'] = 'X'
    elif any(ind in label_lower for ind in safety_indicators):
        purposes['Safety'] = 'X'

    # Efficacy datasets - typically named with disease/condition abbreviations
    efficacy_indicators = ['efficacy', 'adas', 'mmse', 'response', 'outcome', 'endpoint']
    if any(ind in dataset_upper.lower() for ind in ['adeff', 'adas', 'admh', 'adqs']):
        purposes['Efficacy'] = 'X'
    elif any(ind in label_lower for ind in efficacy_indicators):
        purposes['Efficacy'] = 'X'

    # Time-to-event datasets can be efficacy or safety
    if 'adtte' in dataset_upper.lower() or 'time' in label_lower:
        if 'adverse' in label_lower or 'ae' in label_lower or 'safety' in label_lower:
            purposes['Safety'] = 'X'
        else:
            purposes['Efficacy'] = 'X'

    # Lab data can be efficacy or safety
    if any(ind in dataset_upper.lower() for ind in ['adlb', 'adlbc']):
        # Lab data is typically both efficacy and safety
        purposes['Efficacy'] = 'X'
        purposes['Safety'] = 'X'

    # PK/PD datasets
    pkpd_indicators = ['pk', 'pd', 'pharmacokinetic', 'pharmacodynamic', 'concentration']
    if any(ind in dataset_upper.lower() for ind in ['adpc', 'adpp', 'adpk']):
        purposes['PK/PD'] = 'X'
    elif any(ind in label_lower for ind in pkpd_indicators):
        purposes['PK/PD'] = 'X'

    # Primary objective - this would need to be specified explicitly
    # For now, we'll leave it empty unless explicitly stated
    if 'primary' in label_lower:
        purposes['Primary Objective'] = 'X'

    return purposes


def extract_dataset_inventory(
    spec_file: str,
    output_file: str
) -> pd.DataFrame:
    """
    Extract dataset inventory table from Datasets sheet.

    Creates a table with:
    - Dataset Dataset Label (combined)
    - Class
    - Efficacy (X or empty)
    - Safety (X or empty)
    - Baseline or other subject characteristics (X or empty)
    - PK/PD (X or empty)
    - Primary Objective (X or empty)
    - Structure

    Args:
        spec_file: Path to Excel file with Datasets sheet
        output_file: Path to output CSV file

    Returns:
        DataFrame with dataset inventory
    """
    try:
        df = pd.read_excel(spec_file, sheet_name='Datasets')
    except FileNotFoundError:
        sys.exit(f"ERROR: Spec file not found at: {spec_file}")
    except ValueError as e:
        sys.exit(f"ERROR: Could not read Datasets sheet from {spec_file}: {e}")

    # Check required columns
    required_columns = ['Dataset', 'Label', 'Class', 'Structure']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        sys.exit(f"ERROR: Datasets sheet is missing required columns: {missing_columns}")

    # Build output rows
    output_rows = []

    for _, row in df.iterrows():
        dataset = str(row['Dataset']).strip() if pd.notna(row['Dataset']) else ''
        label = str(row['Label']).strip() if pd.notna(row['Label']) else ''
        class_name = str(row['Class']).strip() if pd.notna(row['Class']) else ''
        structure = str(row['Structure']).strip() if pd.notna(row['Structure']) else ''

        if not dataset:
            continue

        # Determine purpose flags
        purposes = determine_dataset_purpose(dataset, label, class_name)

        # Combine dataset and label for first column
        dataset_label = f"{label} | {dataset}" if label else dataset

        output_rows.append({
            'Dataset\nDataset Label': dataset_label,
            'Class': class_name,
            'Efficacy': purposes['Efficacy'],
            'Safety': purposes['Safety'],
            'Baseline or other subject characteristics': purposes['Baseline or other subject characteristics'],
            'PK/PD': purposes['PK/PD'],
            'Primary Objective': purposes['Primary Objective'],
            'Structure': structure
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
        description="Extract variable descriptions and dataset dependencies from spec file"
    )
    parser.add_argument(
        '--spec',
        required=True,
        help='Path to spec Excel file with Datasets, Variables, and Methods sheets (e.g., inputs/adam-pilot-5.xlsx)'
    )
    parser.add_argument(
        '--out',
        required=True,
        help='Path to output CSV file for variable descriptions'
    )
    parser.add_argument(
        '--input',
        help='Path to input CSV file with variables column (e.g., outputs/output_var_filter_file.csv). If not provided, uses key variables from Datasets sheet.'
    )
    parser.add_argument(
        '--deps-out',
        help='Path to output CSV file for dataset dependencies (optional)'
    )
    parser.add_argument(
        '--inventory-out',
        help='Path to output CSV file for dataset inventory table (optional)'
    )
    parser.add_argument(
        '--print',
        action='store_true',
        help='Print results to stdout'
    )

    args = parser.parse_args()
    
    # Extract variable descriptions
    output_df = extract_variable_descriptions(args.spec, args.out, args.input)
    
    if args.print:
        print("Variable Descriptions:")
        print(output_df.to_string(index=False))
        print()
    
    print(f"Wrote {args.out} with {len(output_df)} variables.")
    
    # Extract dataset dependencies if requested
    if args.deps_out:
        deps_df = extract_dataset_dependencies(args.spec, args.deps_out)

        if args.print:
            print("\nDataset Dependencies:")
            print(deps_df.to_string(index=False))
            print()

        print(f"Wrote {args.deps_out} with {len(deps_df)} datasets.")

    # Extract dataset inventory if requested
    if args.inventory_out:
        inventory_df = extract_dataset_inventory(args.spec, args.inventory_out)

        if args.print:
            print("\nDataset Inventory:")
            print(inventory_df.to_string(index=False))
            print()

        print(f"Wrote {args.inventory_out} with {len(inventory_df)} datasets.")


if __name__ == "__main__":
    main()
