#!/usr/bin/env python3
"""
ADaM Scripts Analyzer
Analyzes R scripts in inputs/adam_scripts to extract program names, outputs, and functions used.
"""

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


def extract_output_files(r_code: str) -> List[str]:
    """
    Extract output file names from R code.
    Looks for patterns like:
    - saveRDS(..., "file.rds")
    - write.csv(..., "file.csv")
    - xpt_write(..., "file.xpt")
    - haven::write_xpt(..., "file.xpt")
    """
    outputs = []

    # Pattern for saveRDS, write.csv, write_csv, etc.
    save_patterns = [
        r'saveRDS\s*\([^,]+,\s*file\.path\([^,]+,\s*["\']([^"\']+)["\']',  # saveRDS(obj, file.path(..., "file.rds"))
        r'saveRDS\s*\([^,]+,\s*["\']([^"\']+)["\']',  # saveRDS(obj, "file.rds")
        r'write\.csv\s*\([^,]+,\s*["\']([^"\']+)["\']',  # write.csv(df, "file.csv")
        r'write_csv\s*\([^,]+,\s*["\']([^"\']+)["\']',  # write_csv(df, "file.csv")
        r'xpt_write\s*\([^,]+,\s*["\']([^"\']+)["\']',  # xpt_write(df, "file.xpt")
        r'write_xpt\s*\([^,]+,\s*["\']([^"\']+)["\']',  # write_xpt(df, "file.xpt")
        r'haven::write_xpt\s*\([^,]+,\s*["\']([^"\']+)["\']',  # haven::write_xpt(df, "file.xpt")
    ]

    for pattern in save_patterns:
        matches = re.finditer(pattern, r_code, re.IGNORECASE)
        for match in matches:
            outputs.append(match.group(1))

    # Also check header comments for output documentation
    header_output_match = re.search(r'#\s*Output:\s*(.+)', r_code, re.IGNORECASE)
    if header_output_match:
        output_line = header_output_match.group(1).strip()
        # Extract file names from the output line
        file_names = re.findall(r'[\w\-]+\.\w+', output_line)
        outputs.extend(file_names)

    # Remove duplicates and return
    return list(set(outputs))


def extract_functions(r_code: str) -> Set[str]:
    """
    Extract function names used in R code.
    Returns unique set of functions, excluding variable names and keywords.
    """
    functions = set()

    # First, extract library() calls to get package names
    libraries = set()
    lib_pattern = r'library\s*\(\s*([a-zA-Z][a-zA-Z0-9._]*)\s*\)'
    for match in re.finditer(lib_pattern, r_code):
        libraries.add(match.group(1))

    # Pattern to match function calls: function_name( or package::function_name(
    # This includes both base R and package functions
    func_pattern = r'([a-zA-Z][a-zA-Z0-9._]*(?:::[a-zA-Z][a-zA-Z0-9._]*)?)\s*\('

    # R keywords and operators to exclude
    r_keywords = {
        'if', 'else', 'for', 'while', 'repeat', 'function', 'return',
        'next', 'break', 'TRUE', 'FALSE', 'NULL', 'NA', 'NaN', 'Inf'
    }

    for match in re.finditer(func_pattern, r_code):
        func_name = match.group(1)

        # Skip keywords
        if func_name in r_keywords:
            continue

        # Add the function
        functions.add(func_name)

    return functions


def analyze_r_script(script_path: Path) -> Dict[str, any]:
    """
    Analyze a single R script and extract program name, outputs, and functions.

    Returns:
        Dict with keys: 'program_name', 'outputs', 'functions'
    """
    program_name = script_path.stem  # Get filename without extension

    # Read the R script
    with open(script_path, 'r', encoding='utf-8') as f:
        r_code = f.read()

    # Extract outputs
    outputs = extract_output_files(r_code)

    # Extract functions
    functions = extract_functions(r_code)

    return {
        'program_name': program_name,
        'outputs': outputs,
        'functions': sorted(functions)  # Sort for consistent output
    }


def analyze_all_scripts(scripts_dir: Path) -> List[Dict[str, any]]:
    """
    Analyze all R scripts in the given directory.

    Args:
        scripts_dir: Path to directory containing R scripts

    Returns:
        List of dictionaries with analysis results
    """
    results = []

    # Find all .r and .R files
    r_files = sorted(list(scripts_dir.glob('*.r')) + list(scripts_dir.glob('*.R')))

    for r_file in r_files:
        print(f"Analyzing {r_file.name}...")
        result = analyze_r_script(r_file)
        results.append(result)

    return results


def write_results_to_csv(results: List[Dict[str, any]], output_path: Path) -> None:
    """
    Write analysis results to CSV file.

    Args:
        results: List of analysis results
        output_path: Path to output CSV file
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(['Program Name', 'Output', 'R functions Used'])

        # Write data rows
        for result in results:
            program_name = result['program_name']
            outputs = ', '.join(result['outputs']) if result['outputs'] else ''
            functions = ', '.join(result['functions'][:20])  # Limit to first 20 functions

            # Add "..." if there are more functions
            if len(result['functions']) > 20:
                functions += ', ...'

            writer.writerow([program_name, outputs, functions])

    print(f"\nWrote {output_path} with {len(results)} programs.")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze ADaM R scripts to extract program info, outputs, and functions used.'
    )
    parser.add_argument(
        '--scripts-dir',
        required=True,
        help='Path to directory containing ADaM R scripts (e.g., inputs/adam_scripts)'
    )
    parser.add_argument(
        '--out',
        required=True,
        help='Path to output CSV file (e.g., outputs/adam_programs.csv)'
    )

    args = parser.parse_args()

    # Convert to Path objects
    scripts_dir = Path(args.scripts_dir)
    output_path = Path(args.out)

    # Validate scripts directory exists
    if not scripts_dir.exists():
        print(f"Error: Scripts directory not found: {scripts_dir}")
        return 1

    if not scripts_dir.is_dir():
        print(f"Error: Not a directory: {scripts_dir}")
        return 1

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Analyze all scripts
    print(f"Analyzing R scripts in {scripts_dir}...\n")
    results = analyze_all_scripts(scripts_dir)

    if not results:
        print(f"Warning: No R scripts found in {scripts_dir}")
        return 1

    # Write results to CSV
    write_results_to_csv(results, output_path)

    print(f"\nAnalysis complete!")
    return 0


if __name__ == '__main__':
    exit(main())
