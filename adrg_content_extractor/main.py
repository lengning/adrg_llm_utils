#!/usr/bin/env python3
"""
ADRG Content Extractor - Extracts additional content for ADRG template auto-fill

This module extracts:
1. Dataset descriptions (ADSL and other datasets)
2. Date imputation rules from Methods sheet
3. Source data descriptions
4. Split datasets detection from R scripts
5. Intermediate datasets detection from R scripts
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import re
import json


def read_dataset_description(spec_path: Path, dataset_name: str) -> str:
    """Extract dataset description from ADaM specification Excel file.

    Args:
        spec_path: Path to ADaM spec Excel file
        dataset_name: Name of dataset (e.g., 'ADSL')

    Returns:
        Combined label and structure description
    """
    try:
        df = pd.read_excel(spec_path, sheet_name='Datasets')
        dataset_row = df[df['Dataset'].str.upper() == dataset_name.upper()]

        if dataset_row.empty:
            return f"Dataset {dataset_name} not found in specification."

        label = str(dataset_row.iloc[0]['Label'])
        structure = str(dataset_row.iloc[0]['Structure'])

        # Combine label and structure into a description
        description = f"{label}. {structure}"
        return description

    except Exception as e:
        print(f"Error reading dataset description: {e}", file=sys.stderr)
        return ""


def extract_date_imputation_rules(spec_path: Path) -> str:
    """Extract date imputation rules from Methods sheet.

    Args:
        spec_path: Path to ADaM spec Excel file

    Returns:
        Formatted text describing date imputation rules
    """
    try:
        df = pd.read_excel(spec_path, sheet_name='Methods')

        # Find methods related to date imputation
        date_methods = df[
            df['Description'].str.contains('impute|imputation', case=False, na=False) &
            df['Description'].str.contains('date', case=False, na=False)
        ]

        if date_methods.empty:
            return "No specific date imputation rules documented in the Methods sheet."

        rules = []
        for _, row in date_methods.iterrows():
            name = str(row['Name'])
            desc = str(row['Description'])

            # Extract the imputation logic from description
            if 'impute' in desc.lower():
                rules.append(f"- **{name}**: {desc}")

        if not rules:
            return "Date variables are derived from source data without imputation."

        result = "**Date Imputation Rules:**\n\n" + "\n\n".join(rules)
        return result

    except Exception as e:
        print(f"Error extracting date imputation rules: {e}", file=sys.stderr)
        return ""


def generate_source_data_description(spec_path: Path, protocol_path: Optional[Path] = None) -> str:
    """Generate description of source data used for analysis dataset creation.

    Args:
        spec_path: Path to ADaM spec Excel file
        protocol_path: Optional path to protocol summary

    Returns:
        Description of source data
    """
    try:
        # Get reference data from Datasets sheet
        df = pd.read_excel(spec_path, sheet_name='Datasets')

        reference_data = set()
        for _, row in df.iterrows():
            ref = str(row.get('Reference Data', ''))
            if ref and ref != 'nan' and ref.upper() not in ['NO', 'N/A', 'NONE']:
                # Parse comma-separated reference data
                refs = [r.strip() for r in ref.split(',')]
                reference_data.update(refs)

        # Filter out empty strings
        reference_data = {r for r in reference_data if r}

        if not reference_data:
            description = ("Analysis datasets were derived from SDTM domains collected via "
                          "electronic Case Report Forms (eCRF) and electronic Data Transfer (eDT) sources "
                          "as documented in define.xml.")
        else:
            domains = ', '.join(sorted(reference_data))
            description = (f"Analysis datasets were derived from the following SDTM domains: {domains}. "
                          f"Data were collected via electronic Case Report Forms (eCRF) and "
                          f"electronic Data Transfer (eDT) sources as documented in define.xml.")

        return description

    except Exception as e:
        print(f"Error generating source data description: {e}", file=sys.stderr)
        return ""


def detect_split_datasets(scripts_dir: Path, adam_programs_csv: Optional[Path] = None) -> str:
    """Detect split datasets from R script analysis.

    A split dataset is when a single SDTM domain is split into multiple ADaM datasets
    (e.g., ADAE split into serious and non-serious, or by analysis purpose).

    Args:
        scripts_dir: Directory containing R scripts
        adam_programs_csv: Optional path to adam_programs.csv with dataset info

    Returns:
        Description of split datasets or indication there are none
    """
    try:
        split_datasets = []

        # Check for common split patterns in filenames
        if scripts_dir.exists():
            script_files = list(scripts_dir.glob("*.R")) + list(scripts_dir.glob("*.r"))

            # Look for patterns like ADAES, ADAENR (serious/non-serious AE)
            dataset_groups = {}
            for script in script_files:
                name = script.stem.upper()
                # Extract base dataset name (e.g., ADAE from ADAES)
                if len(name) > 4 and name.startswith('AD'):
                    base = name[:4]  # ADAE, ADLB, etc.
                    suffix = name[4:]
                    if suffix:  # Has a suffix
                        if base not in dataset_groups:
                            dataset_groups[base] = []
                        dataset_groups[base].append(name)

            # Report groups with multiple variants
            for base, variants in dataset_groups.items():
                if len(variants) > 1:
                    split_datasets.append(f"- **{base}**: Split into {', '.join(sorted(variants))}")

        if not split_datasets:
            return "There are no split datasets in this submission."

        result = "**Split Datasets:**\n\n" + "\n".join(split_datasets)
        return result

    except Exception as e:
        print(f"Error detecting split datasets: {e}", file=sys.stderr)
        return "There are no split datasets in this submission."


def detect_intermediate_datasets(scripts_dir: Path) -> str:
    """Detect intermediate datasets from R script analysis.

    Intermediate datasets are temporary datasets created during processing
    but not included in final submission.

    Args:
        scripts_dir: Directory containing R scripts

    Returns:
        Description of intermediate datasets or indication there are none
    """
    try:
        intermediate_patterns = []

        if scripts_dir.exists():
            script_files = list(scripts_dir.glob("*.R")) + list(scripts_dir.glob("*.r"))

            intermediate_keywords = [
                r'\btemp\b', r'\btmp\b', r'_temp\b', r'_tmp\b',
                r'\bintermediate\b', r'\bwork\b', r'_work\b',
                r'\b_int\b', r'\bstaging\b'
            ]

            found_intermediates = set()

            for script in script_files:
                try:
                    content = script.read_text(encoding='utf-8', errors='ignore')

                    # Look for dataset assignments with intermediate naming
                    for keyword in intermediate_keywords:
                        matches = re.findall(rf'(\w*{keyword}\w*)\s*<-', content, re.IGNORECASE)
                        found_intermediates.update(matches)

                    # Look for comments mentioning intermediate datasets
                    comment_matches = re.findall(
                        r'#.*(?:intermediate|temporary|temp|staging).*(?:dataset|data)',
                        content,
                        re.IGNORECASE
                    )
                    if comment_matches:
                        intermediate_patterns.extend(comment_matches[:3])  # Limit to 3

                except Exception as e:
                    print(f"Warning: Could not read {script}: {e}", file=sys.stderr)
                    continue

            if found_intermediates:
                # Clean up and limit the list
                clean_names = [name for name in found_intermediates if len(name) > 2][:10]
                if clean_names:
                    result = ("**Intermediate Datasets:**\n\n"
                             "The following intermediate datasets are created during processing "
                             "but not included in the final submission:\n\n")
                    result += "- " + "\n- ".join(sorted(clean_names)[:5])
                    return result

        return "There are no intermediate datasets. All datasets created during processing are included in the final submission."

    except Exception as e:
        print(f"Error detecting intermediate datasets: {e}", file=sys.stderr)
        return "There are no intermediate datasets. All datasets created during processing are included in the final submission."


def extract_all_content(
    spec_path: Path,
    scripts_dir: Path,
    output_path: Path,
    protocol_path: Optional[Path] = None,
    adam_programs_csv: Optional[Path] = None
):
    """Extract all content and write to output file.

    Args:
        spec_path: Path to ADaM specification Excel file
        scripts_dir: Directory containing R scripts
        output_path: Path to write output JSON file
        protocol_path: Optional path to protocol summary
        adam_programs_csv: Optional path to adam_programs.csv
    """
    print("Extracting ADRG content...")

    content = {}

    # 1. ADSL dataset description
    print("  - Extracting ADSL dataset description...")
    content['adsl_description'] = read_dataset_description(spec_path, 'ADSL')

    # 2. Date imputation rules
    print("  - Extracting date imputation rules...")
    content['date_imputation_rules'] = extract_date_imputation_rules(spec_path)

    # 3. Source data description
    print("  - Generating source data description...")
    content['source_data_description'] = generate_source_data_description(spec_path, protocol_path)

    # 4. Split datasets
    print("  - Detecting split datasets...")
    content['split_datasets'] = detect_split_datasets(scripts_dir, adam_programs_csv)

    # 5. Intermediate datasets
    print("  - Detecting intermediate datasets...")
    content['intermediate_datasets'] = detect_intermediate_datasets(scripts_dir)

    # Write to output file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Content extracted and saved to {output_path}")

    # Also write a human-readable markdown version
    md_path = output_path.with_suffix('.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# ADRG Content Extraction Results\n\n")
        for key, value in content.items():
            title = key.replace('_', ' ').title()
            f.write(f"## {title}\n\n{value}\n\n")

    print(f"✓ Human-readable version saved to {md_path}")


def main():
    """Main entry point for the content extractor."""
    parser = argparse.ArgumentParser(
        description='Extract additional content for ADRG template auto-fill'
    )
    parser.add_argument(
        '--spec',
        required=True,
        help='Path to ADaM specification Excel file'
    )
    parser.add_argument(
        '--scripts-dir',
        required=True,
        help='Directory containing R scripts'
    )
    parser.add_argument(
        '--out',
        required=True,
        help='Output path for extracted content (JSON)'
    )
    parser.add_argument(
        '--protocol',
        required=False,
        help='Optional path to protocol summary markdown'
    )
    parser.add_argument(
        '--adam-programs',
        required=False,
        help='Optional path to adam_programs.csv'
    )

    args = parser.parse_args()

    spec_path = Path(args.spec)
    scripts_dir = Path(args.scripts_dir)
    output_path = Path(args.out)
    protocol_path = Path(args.protocol) if args.protocol else None
    adam_programs_csv = Path(args.adam_programs) if args.adam_programs else None

    if not spec_path.exists():
        print(f"Error: Spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(1)

    if not scripts_dir.exists():
        print(f"Error: Scripts directory not found: {scripts_dir}", file=sys.stderr)
        sys.exit(1)

    extract_all_content(
        spec_path=spec_path,
        scripts_dir=scripts_dir,
        output_path=output_path,
        protocol_path=protocol_path,
        adam_programs_csv=adam_programs_csv
    )


if __name__ == '__main__':
    main()
