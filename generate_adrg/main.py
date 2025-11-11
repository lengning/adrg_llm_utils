#!/usr/bin/env python3
"""Utility for generating a filled ADRG document from the project template.

This script orchestrates the following steps:

1. Read a JSON configuration file that specifies input/output paths and options for
   the supporting utilities.
2. Execute ``sdtm_medra_version.main`` to extract study standard/version metadata
   into a CSV file.
3. Execute ``protocol_retrieve.main`` to extract protocol details into a Markdown file.
4. Execute ``var_filter.main`` to analyse R programs, ``adam_info.main`` to
   summarise ADaM variables and dataset dependencies, and ``renv_to_table.main`` /
   ``pkg_describer.main`` to document open source R packages.
5. Inject the outputs of those steps into ``adrg-template.qmd`` by replacing the
   placeholders ``{sdtm medra version table}``, ``{protocol info md}``,
   ``{analysis output table}``, ``{variable description table}``,
   ``{data dependency table}``, and ``{r package table}``.

The filled document is written to the output path defined in the configuration.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
PLACEHOLDER_TABLE = "{sdtm medra version table}"
PLACEHOLDER_PROTOCOL_MD = "{protocol info md}"
PLACEHOLDER_ANALYSIS_TABLE = "{analysis output table}"
PLACEHOLDER_VAR_TABLE = "{variable description table}"
PLACEHOLDER_DEP_TABLE = "{data dependency table}"
PLACEHOLDER_R_PACKAGES = "{r package table}"
PLACEHOLDER_PROTOCOL_NUMBER = "Study <Protocol Number>"

PKG_DESCRIBER_SCRIPT = ROOT_DIR / "pkg_describer" / "main.r"


class PipelineError(RuntimeError):
    """Raised when an individual pipeline step fails."""


def load_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        raise PipelineError(f"Configuration file not found: {config_path}")
    try:
        with config_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise PipelineError(f"Invalid JSON configuration at {config_path}: {exc}")


def ensure_parent(path: Path) -> None:
    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)


def run_command(argv: Iterable[str]) -> None:
    try:
        subprocess.run(list(argv), check=True)
    except subprocess.CalledProcessError as exc:
        cmd = " ".join(map(str, exc.cmd)) if exc.cmd else "<unknown>"
        raise PipelineError(f"Command failed with exit code {exc.returncode}: {cmd}") from exc


def resolve_path(path_value: str) -> Path:
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        path = ROOT_DIR / path
    return path


def run_sdtm_medra(config: Dict[str, Any]) -> Path:
    define_path = resolve_path(config["define"])
    output_path = resolve_path(config.get("out", "standards_from_define.csv"))

    if not define_path.exists():
        raise PipelineError(f"define.xml not found: {define_path}")

    ensure_parent(output_path)
    script_path = ROOT_DIR / "sdtm_medra_version" / "main.py"
    argv = [
        sys.executable,
        str(script_path),
        "--define",
        str(define_path),
        "--out",
        str(output_path),
    ]
    run_command(argv)
    if not output_path.exists():
        raise PipelineError(
            "Expected SDTM/MedDRA output missing after script execution: "
            f"{output_path}"
        )
    return output_path


def run_protocol_retrieve(config: Dict[str, Any]) -> Path:
    protocol_pdf = resolve_path(config["protocol"])
    if not protocol_pdf.exists():
        raise PipelineError(f"Protocol PDF not found: {protocol_pdf}")

    output_md = resolve_path(config.get("out", "protocol_description.md"))
    ensure_parent(output_md)

    script_path = ROOT_DIR / "protocol_retrieve" / "main.py"
    argv = [
        sys.executable,
        str(script_path),
        "--protocol",
        str(protocol_pdf),
        "--out",
        str(output_md),
    ]

    model = config.get("model")
    if model:
        argv.extend(["--model", str(model)])

    max_pages = config.get("max_pages")
    if max_pages is not None:
        argv.extend(["--max-pages", str(max_pages)])

    run_command(argv)
    if not output_md.exists():
        raise PipelineError(
            "Expected protocol markdown output missing after script execution: "
            f"{output_md}"
        )
    return output_md


def run_var_filter(config: Dict[str, Any]) -> Path:
    has_folder = "folder" in config
    has_file = "file" in config
    if not has_folder and not has_file:
        raise PipelineError(
            "var_filter configuration must include either 'folder' or 'file'"
        )
    if has_folder and has_file:
        raise PipelineError(
            "var_filter configuration must not include both 'folder' and 'file'"
        )

    script_path = ROOT_DIR / "var_filter" / "main.py"
    argv = [sys.executable, str(script_path)]

    if has_folder:
        folder_path = resolve_path(config["folder"])
        argv.extend(["--folder", str(folder_path)])
    else:
        file_path = resolve_path(config["file"])
        argv.extend(["--file", str(file_path)])

    if "model" in config and config["model"]:
        argv.extend(["--model", str(config["model"])])

    output_csv = resolve_path(config.get("out", "r_code_audit.csv"))
    ensure_parent(output_csv)
    argv.extend(["--out", str(output_csv)])

    if config.get("print"):
        argv.append("--print")

    run_command(argv)
    if not output_csv.exists():
        raise PipelineError(
            "Expected var_filter CSV missing after script execution: "
            f"{output_csv}"
        )
    return output_csv


def run_adam_info(config: Dict[str, Any], var_filter_csv: Path) -> Tuple[Path, Path]:
    if not var_filter_csv.exists():
        raise PipelineError(
            "var_filter CSV required for adam_info not found: "
            f"{var_filter_csv}"
        )

    try:
        spec_value = config["spec"]
    except KeyError as exc:
        raise PipelineError("adam_info configuration missing 'spec' entry") from exc

    spec_path = resolve_path(spec_value)
    if not spec_path.exists():
        raise PipelineError(f"ADaM spec file not found: {spec_path}")

    output_csv = resolve_path(config.get("out", "var_descriptions.csv"))
    ensure_parent(output_csv)

    try:
        deps_value = config["deps_out"]
    except KeyError as exc:
        raise PipelineError("adam_info configuration missing 'deps_out' entry") from exc
    deps_path = resolve_path(deps_value)
    ensure_parent(deps_path)

    script_path = ROOT_DIR / "adam_info" / "main.py"
    argv = [
        sys.executable,
        str(script_path),
        "--spec",
        str(spec_path),
        "--out",
        str(output_csv),
        "--input",
        str(var_filter_csv),
    ]

    argv.extend(["--deps-out", str(deps_path)])

    if config.get("print"):
        argv.append("--print")

    run_command(argv)
    if not output_csv.exists():
        raise PipelineError(
            "Expected adam_info CSV missing after script execution: "
            f"{output_csv}"
        )
    if not deps_path.exists():
        raise PipelineError(
            "Expected adam_info dependencies CSV missing after script execution: "
            f"{deps_path}"
        )
    return output_csv, deps_path


def run_renv_to_table(config: Dict[str, Any]) -> Path:
    try:
        renv_value = config["renv"]
    except KeyError as exc:
        raise PipelineError("renv_to_table configuration missing 'renv' entry") from exc

    renv_path = resolve_path(renv_value)
    if not renv_path.exists():
        raise PipelineError(f"renv.lock not found: {renv_path}")

    output_csv = resolve_path(config.get("out", "r_pkg_versions.csv"))
    ensure_parent(output_csv)

    script_path = ROOT_DIR / "renv_to_table" / "main.py"
    argv = [
        sys.executable,
        str(script_path),
        "--renv",
        str(renv_path),
        "--out",
        str(output_csv),
    ]

    run_command(argv)
    if not output_csv.exists():
        raise PipelineError(
            "Expected renv_to_table CSV missing after script execution: "
            f"{output_csv}"
        )
    return output_csv


def run_pkg_describer(config: Dict[str, Any], packages_csv: Path) -> Path:
    if not packages_csv.exists():
        raise PipelineError(
            "R package versions CSV not found for pkg_describer input: "
            f"{packages_csv}"
        )

    output_csv = resolve_path(config.get("out", "pkg_descriptions.csv"))
    ensure_parent(output_csv)

    argv = [
        "Rscript",
        str(PKG_DESCRIBER_SCRIPT),
        "--input",
        str(packages_csv),
        "--output",
        str(output_csv),
    ]

    model = config.get("model")
    if model:
        argv.extend(["--model", str(model)])

    if config.get("no_llm"):
        argv.append("--no-llm")

    run_command(argv)
    if not output_csv.exists():
        raise PipelineError(
            "Expected pkg_describer CSV missing after script execution: "
            f"{output_csv}"
        )
    return output_csv


def escape_pipes(value: str) -> str:
    return value.replace("|", "\\|")


def csv_to_markdown_table(csv_path: Path) -> str:
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)

    if not rows:
        raise PipelineError(f"SDTM/MedDRA CSV is empty: {csv_path}")

    header = rows[0]
    body = rows[1:]

    header_line = "| " + " | ".join(escape_pipes(cell) for cell in header) + " |"
    separator_line = "| " + " | ".join("---" for _ in header) + " |"
    body_lines = [
        "| " + " | ".join(escape_pipes(cell) for cell in row) + " |"
        for row in body
    ]

    table_lines = [header_line, separator_line]
    table_lines.extend(body_lines)
    return "\n".join(table_lines)


def build_filled_template(
    template_path: Path,
    table_md: str,
    protocol_md: str,
    analysis_md: str,
    var_table_md: str,
    deps_table_md: str,
    r_packages_md: str,
    protocol_number: Optional[str] = None,
) -> str:
    template_text = template_path.read_text(encoding="utf-8")
    if PLACEHOLDER_TABLE not in template_text:
        raise PipelineError(
            f"Placeholder {PLACEHOLDER_TABLE!r} not found in template {template_path}"
        )
    if PLACEHOLDER_PROTOCOL_MD not in template_text:
        raise PipelineError(
            f"Placeholder {PLACEHOLDER_PROTOCOL_MD!r} not found in template {template_path}"
        )
    if PLACEHOLDER_ANALYSIS_TABLE not in template_text:
        raise PipelineError(
            f"Placeholder {PLACEHOLDER_ANALYSIS_TABLE!r} not found in template {template_path}"
        )
    if PLACEHOLDER_VAR_TABLE not in template_text:
        raise PipelineError(
            f"Placeholder {PLACEHOLDER_VAR_TABLE!r} not found in template {template_path}"
        )
    if PLACEHOLDER_DEP_TABLE not in template_text:
        raise PipelineError(
            f"Placeholder {PLACEHOLDER_DEP_TABLE!r} not found in template {template_path}"
        )
    if PLACEHOLDER_R_PACKAGES not in template_text:
        raise PipelineError(
            f"Placeholder {PLACEHOLDER_R_PACKAGES!r} not found in template {template_path}"
        )
    if protocol_number and PLACEHOLDER_PROTOCOL_NUMBER not in template_text:
        raise PipelineError(
            f"Placeholder {PLACEHOLDER_PROTOCOL_NUMBER!r} not found in template {template_path}"
        )

    filled = template_text.replace(PLACEHOLDER_TABLE, table_md)
    filled = filled.replace(PLACEHOLDER_PROTOCOL_MD, protocol_md.strip())
    filled = filled.replace(PLACEHOLDER_ANALYSIS_TABLE, analysis_md.strip())
    filled = filled.replace(PLACEHOLDER_VAR_TABLE, var_table_md.strip())
    filled = filled.replace(PLACEHOLDER_DEP_TABLE, deps_table_md.strip())
    filled = filled.replace(PLACEHOLDER_R_PACKAGES, r_packages_md.strip())
    if protocol_number:
        replacement = f"Study {protocol_number}"
        filled = filled.replace(PLACEHOLDER_PROTOCOL_NUMBER, replacement)
    return filled


def extract_protocol_number(protocol_md: str) -> Optional[str]:
    match = re.search(r"Protocol\s*Number\s*:\s*(.+)", protocol_md, flags=re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def run_question_filler(
    config_path: Path,
    template_path: Path,
    output_path: Path,
    model: str = "gpt-4o-mini"
) -> Path:
    """
    Run the adrg_question_filler to fill yes/no questions in the template.

    Args:
        config_path: Path to pipeline configuration JSON
        template_path: Path to template file to fill
        output_path: Path for output filled template
        model: LLM model to use for question answering

    Returns:
        Path to filled template
    """
    script_path = ROOT_DIR / "adrg_question_filler" / "main.py"
    if not script_path.exists():
        raise PipelineError(
            f"Question filler script not found: {script_path}"
        )

    ensure_parent(output_path)

    argv = [
        sys.executable,
        str(script_path),
        "--config",
        str(config_path),
        "--template",
        str(template_path),
        "--out",
        str(output_path),
        "--model",
        str(model),
    ]

    run_command(argv)

    if not output_path.exists():
        raise PipelineError(
            "Expected filled template missing after question filler execution: "
            f"{output_path}"
        )

    return output_path


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a filled ADRG document using configured utilities."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT_DIR / "config" / "pipeline_config.json",
        help="Path to pipeline JSON configuration file."
    )
    parser.add_argument(
        "--skip-sdtm",
        action="store_true",
        help="Skip running sdtm_medra_version (use existing CSV output)."
    )
    parser.add_argument(
        "--skip-protocol",
        action="store_true",
        help="Skip running protocol_retrieve (use existing Markdown output)."
    )
    parser.add_argument(
        "--skip-var-filter",
        action="store_true",
        help="Skip running var_filter (use existing CSV output)."
    )
    parser.add_argument(
        "--skip-adam-info",
        action="store_true",
        help="Skip running adam_info (use existing variable description CSV)."
    )
    parser.add_argument(
        "--skip-renv",
        action="store_true",
        help="Skip running renv_to_table (use existing R package versions CSV)."
    )
    parser.add_argument(
        "--skip-pkg-describer",
        action="store_true",
        help="Skip running pkg_describer (use existing package description CSV)."
    )
    parser.add_argument(
        "--fill-questions",
        action="store_true",
        help="Run adrg_question_filler to fill yes/no questions in template."
    )
    parser.add_argument(
        "--question-model",
        default="gpt-4o-mini",
        help="LLM model to use for question answering (default: gpt-4o-mini)."
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    config = load_config(args.config)

    sdtm_cfg = config.get("sdtm_medra_version")
    protocol_cfg = config.get("protocol_retrieve")
    var_filter_cfg = config.get("var_filter")
    adam_info_cfg = config.get("adam_info")
    renv_cfg = config.get("renv_to_table")
    pkg_cfg = config.get("pkg_describer")
    template_cfg = config.get("template")

    if not isinstance(sdtm_cfg, dict):
        raise PipelineError("Missing or invalid 'sdtm_medra_version' configuration")
    if not isinstance(protocol_cfg, dict):
        raise PipelineError("Missing or invalid 'protocol_retrieve' configuration")
    if not isinstance(var_filter_cfg, dict):
        raise PipelineError("Missing or invalid 'var_filter' configuration")
    if not isinstance(adam_info_cfg, dict):
        raise PipelineError("Missing or invalid 'adam_info' configuration")
    if not isinstance(renv_cfg, dict):
        raise PipelineError("Missing or invalid 'renv_to_table' configuration")
    if not isinstance(pkg_cfg, dict):
        raise PipelineError("Missing or invalid 'pkg_describer' configuration")
    if not isinstance(template_cfg, dict):
        raise PipelineError("Missing or invalid 'template' configuration")

    if not args.skip_sdtm:
        sdtm_output = run_sdtm_medra(sdtm_cfg)
    else:
        sdtm_output = resolve_path(sdtm_cfg.get("out", "standards_from_define.csv"))
    if not sdtm_output.exists():
        raise PipelineError(
            "SDTM/MedDRA CSV not found; either run the step or update the configuration: "
            f"{sdtm_output}"
        )

    if not args.skip_protocol:
        protocol_output = run_protocol_retrieve(protocol_cfg)
    else:
        protocol_output = resolve_path(protocol_cfg.get("out", "protocol_description.md"))
    if not protocol_output.exists():
        raise PipelineError(
            "Protocol markdown not found; either run the step or update the configuration: "
            f"{protocol_output}"
        )

    if not args.skip_var_filter:
        var_filter_output = run_var_filter(var_filter_cfg)
    else:
        var_filter_output = resolve_path(var_filter_cfg.get("out", "r_code_audit.csv"))
    if not var_filter_output.exists():
        raise PipelineError(
            "var_filter CSV not found; either run the step or update the configuration: "
            f"{var_filter_output}"
        )

    if not args.skip_adam_info:
        var_desc_output, deps_output = run_adam_info(adam_info_cfg, var_filter_output)
    else:
        var_desc_output = resolve_path(adam_info_cfg.get("out", "var_descriptions.csv"))
        if not var_desc_output.exists():
            raise PipelineError(
                "adam_info CSV not found; either run the step or update the configuration: "
                f"{var_desc_output}"
            )
        try:
            deps_value = adam_info_cfg["deps_out"]
        except KeyError as exc:
            raise PipelineError(
                "adam_info configuration missing 'deps_out' entry for existing outputs"
            ) from exc
        deps_output = resolve_path(deps_value)
    if not deps_output.exists():
        raise PipelineError(
            "adam_info dependencies CSV not found; either run the step or update the configuration: "
            f"{deps_output}"
        )

    if not args.skip_renv:
        renv_output = run_renv_to_table(renv_cfg)
    else:
        renv_output = resolve_path(renv_cfg.get("out", "r_pkg_versions.csv"))
    if not renv_output.exists():
        raise PipelineError(
            "R package versions CSV not found; either run the step or update the configuration: "
            f"{renv_output}"
        )

    if not args.skip_pkg_describer:
        pkg_output = run_pkg_describer(pkg_cfg, renv_output)
    else:
        pkg_output = resolve_path(pkg_cfg.get("out", "pkg_descriptions.csv"))
        if not pkg_output.exists():
            raise PipelineError(
                "pkg_describer CSV not found; either run the step or update the configuration: "
                f"{pkg_output}"
            )

    table_md = csv_to_markdown_table(sdtm_output)
    protocol_md = protocol_output.read_text(encoding="utf-8")
    analysis_md = csv_to_markdown_table(var_filter_output)
    var_table_md = csv_to_markdown_table(var_desc_output)
    deps_table_md = csv_to_markdown_table(deps_output)
    r_packages_md = csv_to_markdown_table(pkg_output)
    protocol_number = extract_protocol_number(protocol_md)

    template_path = resolve_path(template_cfg["path"])
    if not template_path.exists():
        raise PipelineError(f"Template file not found: {template_path}")

    filled_text = build_filled_template(
        template_path,
        table_md,
        protocol_md,
        analysis_md,
        var_table_md,
        deps_table_md,
        r_packages_md,
        protocol_number=protocol_number,
    )

    output_path = resolve_path(template_cfg.get("output", "adrg-filled.qmd"))
    ensure_parent(output_path)
    output_path.write_text(filled_text, encoding="utf-8")
    print(f"Filled ADRG document written to: {output_path}")

    # Optionally run question filler to fill yes/no questions
    if args.fill_questions:
        print("\nRunning question filler to fill yes/no questions...")
        filled_question_path = run_question_filler(
            config_path=args.config,
            template_path=output_path,  # Use the already filled template as input
            output_path=output_path,  # Overwrite the same file
            model=args.question_model
        )
        print(f"Yes/no questions filled in: {filled_question_path}")


if __name__ == "__main__":
    try:
        main()
    except PipelineError as exc:
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        sys.exit(1)
