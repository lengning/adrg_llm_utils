#!/usr/bin/env python3
"""
Multi-Agent ADRG Generation Workflow
Orchestrates specialized agents to generate ADRG documents automatically
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from multi_agent_adrg.agent_framework import (
    Agent, Task, Crew, TaskResult, TaskStatus,
    run_python_module, resolve_path
)
import json


def create_agents() -> Dict[str, Agent]:
    """Create all specialized agents for ADRG generation"""

    agents = {
        "definexml_agent": Agent(
            name="Definexml Extraction Agent",
            role="SDTM/MedDRA Metadata Specialist",
            goal="Extract study standards and metadata from define.xml files",
            backstory="You are an expert in clinical trial data standards (SDTM, MedDRA, CDASH). "
                     "You excel at parsing XML files and extracting version information.",
            tools=["xml_parser", "define_xml_reader"]
        ),

        "protocol_agent": Agent(
            name="Protocol Analysis Agent",
            role="Clinical Protocol Analyst",
            goal="Extract and summarize protocol information from PDF documents",
            backstory="You are a clinical research expert who excels at reading protocol documents "
                     "and extracting key information like objectives, endpoints, and study design.",
            tools=["pdf_reader", "llm_summarizer"]
        ),

        "code_analysis_agent": Agent(
            name="Code Analysis Agent",
            role="R Programming Specialist",
            goal="Analyze R scripts to extract variables, outputs, and functions used",
            backstory="You are an expert R programmer who can analyze code to understand "
                     "data processing workflows, variable usage, and output generation.",
            tools=["r_script_parser", "function_extractor", "var_filter", "adam_scripts_analyzer"]
        ),

        "adam_spec_agent": Agent(
            name="ADaM Specification Agent",
            role="ADaM Standards Expert",
            goal="Process ADaM specification files to extract variables, dependencies, and inventory",
            backstory="You are an expert in CDISC ADaM standards and Excel data analysis. "
                     "You excel at processing specification sheets and understanding dataset relationships.",
            tools=["excel_reader", "variable_extractor", "dependency_analyzer"]
        ),

        "package_doc_agent": Agent(
            name="Package Documentation Agent",
            role="R Package Documentation Specialist",
            goal="Document R packages and their versions used in the analysis",
            backstory="You are an expert in R package ecosystems and documentation. "
                     "You can parse renv.lock files and generate comprehensive package descriptions.",
            tools=["renv_parser", "package_describer", "cran_api"]
        ),

        "question_agent": Agent(
            name="Question Answering Agent",
            role="ADRG Question Specialist",
            goal="Answer yes/no questions in ADRG templates using protocol, ADaM specs, and R scripts",
            backstory="You are an expert at understanding clinical trial documentation requirements. "
                     "You can analyze protocol PDFs, ADaM specifications, R scripts, and data files "
                     "to answer regulatory questions accurately.",
            tools=["llm_qa", "data_context_builder", "template_parser", "protocol_reader", "spec_reader"]
        ),

        "assembly_agent": Agent(
            name="Document Assembly Agent",
            role="Document Integration Coordinator",
            goal="Assemble all components into a final ADRG document",
            backstory="You are a technical writer and document specialist who excels at "
                     "integrating multiple data sources into a cohesive regulatory document.",
            tools=["template_filler", "markdown_renderer", "csv_to_table_converter"]
        ),
    }

    return agents


def create_metadata_extraction_task(agent: Agent, config: Dict[str, Any]) -> Task:
    """Task for extracting SDTM/MedDRA versions"""

    def action(context: Dict[str, Any]) -> Dict[str, Any]:
        sdtm_cfg = config["sdtm_medra_version"]
        define_path = resolve_path(sdtm_cfg["define"], ROOT_DIR)
        output_path = resolve_path(sdtm_cfg["out"], ROOT_DIR)

        script_path = ROOT_DIR / "sdtm_medra_version" / "main.py"
        run_python_module(
            str(script_path),
            ["--define", str(define_path), "--out", str(output_path)]
        )

        return {"output_path": output_path}

    return Task(
        task_id="extract_metadata",
        description="Extract SDTM/MedDRA versions from define.xml",
        agent=agent,
        action=action,
        config_key="sdtm_medra_version"
    )


def create_protocol_extraction_task(agent: Agent, config: Dict[str, Any]) -> Task:
    """Task for extracting protocol information"""

    def action(context: Dict[str, Any]) -> Dict[str, Any]:
        protocol_cfg = config["protocol_retrieve"]
        protocol_path = resolve_path(protocol_cfg["protocol"], ROOT_DIR)
        output_path = resolve_path(protocol_cfg["out"], ROOT_DIR)

        script_path = ROOT_DIR / "protocol_retrieve" / "main.py"
        args = ["--protocol", str(protocol_path), "--out", str(output_path)]

        if protocol_cfg.get("model"):
            args.extend(["--model", protocol_cfg["model"]])
        if protocol_cfg.get("max_pages") is not None:
            args.extend(["--max-pages", str(protocol_cfg["max_pages"])])

        run_python_module(str(script_path), args)

        return {"output_path": output_path}

    return Task(
        task_id="extract_protocol",
        description="Extract protocol information from PDF",
        agent=agent,
        action=action,
        config_key="protocol_retrieve"
    )


def create_var_filter_task(agent: Agent, config: Dict[str, Any]) -> Task:
    """Task for analyzing TLF R scripts"""

    def action(context: Dict[str, Any]) -> Dict[str, Any]:
        var_filter_cfg = config["var_filter"]
        output_path = resolve_path(var_filter_cfg["out"], ROOT_DIR)

        script_path = ROOT_DIR / "var_filter" / "main.py"
        args = []

        if "folder" in var_filter_cfg:
            folder_path = resolve_path(var_filter_cfg["folder"], ROOT_DIR)
            args.extend(["--folder", str(folder_path)])
        elif "file" in var_filter_cfg:
            file_path = resolve_path(var_filter_cfg["file"], ROOT_DIR)
            args.extend(["--file", str(file_path)])

        if var_filter_cfg.get("model"):
            args.extend(["--model", var_filter_cfg["model"]])

        args.extend(["--out", str(output_path)])

        run_python_module(str(script_path), args)

        return {"output_path": output_path}

    return Task(
        task_id="analyze_tlf_scripts",
        description="Analyze TLF R scripts for variables and outputs",
        agent=agent,
        action=action,
        config_key="var_filter"
    )


def create_adam_info_task(agent: Agent, config: Dict[str, Any]) -> Task:
    """Task for extracting ADaM variable information"""

    def action(context: Dict[str, Any]) -> Dict[str, Any]:
        adam_cfg = config["adam_info"]
        spec_path = resolve_path(adam_cfg["spec"], ROOT_DIR)
        output_path = resolve_path(adam_cfg["out"], ROOT_DIR)
        deps_path = resolve_path(adam_cfg["deps_out"], ROOT_DIR)

        # Get var_filter output from previous task
        var_filter_output = context["analyze_tlf_scripts"]["output_path"]

        script_path = ROOT_DIR / "adam_info" / "main.py"
        args = [
            "--spec", str(spec_path),
            "--input", str(var_filter_output),
            "--out", str(output_path),
            "--deps-out", str(deps_path)
        ]

        if "inventory_out" in adam_cfg:
            inventory_path = resolve_path(adam_cfg["inventory_out"], ROOT_DIR)
            args.extend(["--inventory-out", str(inventory_path)])

        run_python_module(str(script_path), args)

        return {
            "output_path": output_path,
            "deps_path": deps_path,
            "inventory_path": inventory_path if "inventory_out" in adam_cfg else None
        }

    return Task(
        task_id="extract_adam_info",
        description="Extract ADaM variable descriptions and dataset dependencies",
        agent=agent,
        action=action,
        dependencies=["analyze_tlf_scripts"],
        config_key="adam_info"
    )


def create_adam_scripts_task(agent: Agent, config: Dict[str, Any]) -> Task:
    """Task for analyzing ADaM R scripts"""

    def action(context: Dict[str, Any]) -> Dict[str, Any]:
        adam_scripts_cfg = config["adam_scripts_analyzer"]
        scripts_dir = resolve_path(adam_scripts_cfg["scripts_dir"], ROOT_DIR)
        output_path = resolve_path(adam_scripts_cfg["out"], ROOT_DIR)

        script_path = ROOT_DIR / "adam_scripts_analyzer" / "main.py"
        args = [
            "--scripts-dir", str(scripts_dir),
            "--out", str(output_path)
        ]

        # Add spec file if provided
        if "spec" in adam_scripts_cfg:
            spec_path = resolve_path(adam_scripts_cfg["spec"], ROOT_DIR)
            args.extend(["--spec", str(spec_path)])

        run_python_module(str(script_path), args)

        return {"output_path": output_path}

    return Task(
        task_id="analyze_adam_scripts",
        description="Analyze ADaM R scripts for programs and functions",
        agent=agent,
        action=action,
        config_key="adam_scripts_analyzer"
    )


def create_renv_task(agent: Agent, config: Dict[str, Any]) -> Task:
    """Task for extracting R package versions"""

    def action(context: Dict[str, Any]) -> Dict[str, Any]:
        renv_cfg = config["renv_to_table"]
        renv_path = resolve_path(renv_cfg["renv"], ROOT_DIR)
        output_path = resolve_path(renv_cfg["out"], ROOT_DIR)

        script_path = ROOT_DIR / "renv_to_table" / "main.py"
        run_python_module(
            str(script_path),
            ["--renv", str(renv_path), "--out", str(output_path)]
        )

        return {"output_path": output_path}

    return Task(
        task_id="extract_renv",
        description="Extract R package versions from renv.lock",
        agent=agent,
        action=action,
        config_key="renv_to_table"
    )


def create_pkg_describer_task(agent: Agent, config: Dict[str, Any]) -> Task:
    """Task for generating package descriptions"""

    def action(context: Dict[str, Any]) -> Dict[str, Any]:
        pkg_cfg = config["pkg_describer"]
        output_path = resolve_path(pkg_cfg["out"], ROOT_DIR)

        # Get renv output from previous task
        renv_output = context["extract_renv"]["output_path"]

        script_path = ROOT_DIR / "pkg_describer" / "main.r"
        args = [
            "Rscript",
            str(script_path),
            "--input", str(renv_output),
            "--output", str(output_path)
        ]

        if pkg_cfg.get("model"):
            args.extend(["--model", pkg_cfg["model"]])
        if pkg_cfg.get("no_llm"):
            args.append("--no-llm")

        import subprocess
        subprocess.run(args, check=True)

        return {"output_path": output_path}

    return Task(
        task_id="generate_pkg_descriptions",
        description="Generate R package descriptions",
        agent=agent,
        action=action,
        dependencies=["extract_renv"],
        config_key="pkg_describer"
    )


def create_assembly_task(agent: Agent, config: Dict[str, Any]) -> Task:
    """Task for assembling the final ADRG document"""

    def action(context: Dict[str, Any]) -> Dict[str, Any]:
        # Import the csv_to_markdown_table function
        sys.path.insert(0, str(ROOT_DIR / "generate_adrg"))
        from generate_adrg.main import csv_to_markdown_table, build_filled_template, extract_protocol_number

        # Get all output files - either from context or from config paths
        def get_output_path(task_id: str, config_key: str, output_key: str) -> Path:
            """Get output path from context if task was run, otherwise from config"""
            if task_id in context:
                return context[task_id]["output_path"]
            else:
                # Task was skipped, read from config
                return resolve_path(config[config_key][output_key], ROOT_DIR)

        sdtm_output = get_output_path("extract_metadata", "sdtm_medra_version", "out")
        protocol_output = get_output_path("extract_protocol", "protocol_retrieve", "out")
        var_filter_output = get_output_path("analyze_tlf_scripts", "var_filter", "out")
        adam_info_output = get_output_path("extract_adam_info", "adam_info", "out")
        adam_info_deps = resolve_path(config["adam_info"]["deps_out"], ROOT_DIR)
        adam_info_inventory = resolve_path(config["adam_info"]["inventory_out"], ROOT_DIR) if "inventory_out" in config["adam_info"] else None
        adam_scripts_output = get_output_path("analyze_adam_scripts", "adam_scripts_analyzer", "out")
        pkg_output = get_output_path("generate_pkg_descriptions", "pkg_describer", "out")

        # Convert all CSVs to markdown tables (with error handling for missing files)
        def safe_read_csv(path: Path) -> str:
            """Read CSV and convert to markdown, return empty table if file missing"""
            if path.exists():
                return csv_to_markdown_table(path)
            else:
                return "| Column |\n| --- |\n| (no data) |"

        def safe_read_text(path: Path) -> str:
            """Read text file, return placeholder if missing"""
            if path.exists():
                return path.read_text(encoding="utf-8")
            else:
                return "(Protocol information not available)"

        table_md = safe_read_csv(sdtm_output)
        protocol_md = safe_read_text(protocol_output)
        analysis_md = safe_read_csv(var_filter_output)
        var_table_md = safe_read_csv(adam_info_output)
        deps_table_md = safe_read_csv(adam_info_deps)
        r_packages_md = safe_read_csv(pkg_output)
        adam_programs_md = safe_read_csv(adam_scripts_output)

        # Handle inventory table
        if adam_info_inventory and adam_info_inventory.exists():
            inventory_table_md = csv_to_markdown_table(adam_info_inventory)
        else:
            inventory_table_md = "| Dataset\nDataset Label | Class | Efficacy | Safety | Baseline or other subject characteristics | PK/PD | Primary Objective | Structure |\n| --- | --- | --- | --- | --- | --- | --- | --- |"

        # Extract protocol number (only if protocol file exists and we want to use it)
        # Note: Disabled for now as template may not have the placeholder
        protocol_number = None  # extract_protocol_number(protocol_md) if protocol_output.exists() else None

        # Build filled template
        template_cfg = config["template"]
        template_path = resolve_path(template_cfg["path"], ROOT_DIR)
        output_path = resolve_path(template_cfg["output"], ROOT_DIR)

        filled_text = build_filled_template(
            template_path,
            table_md,
            protocol_md,
            analysis_md,
            var_table_md,
            deps_table_md,
            r_packages_md,
            inventory_table_md,
            adam_programs_md,
            protocol_number=protocol_number
        )

        # Write filled document
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(filled_text, encoding="utf-8")

        return {"output_path": output_path}

    return Task(
        task_id="assemble_document",
        description="Assemble all components into final ADRG document",
        agent=agent,
        action=action,
        dependencies=[
            "extract_metadata",
            "extract_protocol",
            "analyze_tlf_scripts",
            "extract_adam_info",
            "analyze_adam_scripts",
            "generate_pkg_descriptions"
        ],
        config_key="template"
    )


def create_question_answering_task(agent: Agent, config: Dict[str, Any], config_path: Path) -> Task:
    """
    Task for answering yes/no questions in ADRG.

    Uses data context from:
    - Protocol PDF (extracted markdown)
    - ADaM specification files
    - R scripts
    - Variable descriptions
    - Dataset dependencies
    - Package information
    """

    def action(context: Dict[str, Any]) -> Dict[str, Any]:
        # Get the assembled document from previous task
        assembled_doc = context["assemble_document"]["output_path"]

        # The question filler will automatically load data context from the config,
        # including protocol information from protocol_retrieve.out,
        # ADaM specs, R scripts, and all other available data sources
        script_path = ROOT_DIR / "adrg_question_filler" / "main.py"
        args = [
            "--config", str(config_path),
            "--template", str(assembled_doc),
            "--out", str(assembled_doc),  # Overwrite same file
            "--model", "gpt-4o-mini"
        ]

        run_python_module(str(script_path), args)

        return {"output_path": assembled_doc}

    return Task(
        task_id="answer_questions",
        description="Answer yes/no questions using protocol, ADaM specs, and R scripts data",
        agent=agent,
        action=action,
        dependencies=[
            "assemble_document",
            "extract_protocol",  # Explicitly require protocol extraction
            "extract_adam_info",  # Require ADaM info for better context
            "analyze_adam_scripts"  # Require ADaM scripts analysis
        ],
        skippable=True  # This task is optional
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Multi-Agent ADRG Generation Workflow"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT_DIR / "config" / "pipeline_config.json",
        help="Path to pipeline configuration JSON"
    )
    parser.add_argument(
        "--skip-sdtm",
        action="store_true",
        help="Skip SDTM/MedDRA extraction"
    )
    parser.add_argument(
        "--skip-protocol",
        action="store_true",
        help="Skip protocol extraction"
    )
    parser.add_argument(
        "--skip-var-filter",
        action="store_true",
        help="Skip TLF script analysis"
    )
    parser.add_argument(
        "--skip-adam-info",
        action="store_true",
        help="Skip ADaM info extraction"
    )
    parser.add_argument(
        "--skip-adam-scripts",
        action="store_true",
        help="Skip ADaM scripts analysis"
    )
    parser.add_argument(
        "--skip-renv",
        action="store_true",
        help="Skip renv.lock processing"
    )
    parser.add_argument(
        "--skip-pkg-describer",
        action="store_true",
        help="Skip package description generation"
    )
    parser.add_argument(
        "--fill-questions",
        action="store_true",
        help="Fill yes/no questions in template"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Enable verbose output"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Load configuration
    with open(args.config, 'r') as f:
        config = json.load(f)

    # Create all agents
    agents_dict = create_agents()

    # Create all tasks
    tasks = [
        create_metadata_extraction_task(agents_dict["definexml_agent"], config),
        create_protocol_extraction_task(agents_dict["protocol_agent"], config),
        create_var_filter_task(agents_dict["code_analysis_agent"], config),
        create_adam_info_task(agents_dict["adam_spec_agent"], config),
        create_adam_scripts_task(agents_dict["code_analysis_agent"], config),
        create_renv_task(agents_dict["package_doc_agent"], config),
        create_pkg_describer_task(agents_dict["package_doc_agent"], config),
        create_assembly_task(agents_dict["assembly_agent"], config),
    ]

    # Add question answering task if requested
    if args.fill_questions:
        tasks.append(
            create_question_answering_task(
                agents_dict["question_agent"],
                config,
                args.config
            )
        )

    # Create crew
    crew = Crew(
        agents=list(agents_dict.values()),
        tasks=tasks,
        config=config,
        verbose=args.verbose
    )

    # Set up skip flags
    skip_flags = {
        "extract_metadata": args.skip_sdtm,
        "extract_protocol": args.skip_protocol,
        "analyze_tlf_scripts": args.skip_var_filter,
        "extract_adam_info": args.skip_adam_info,
        "analyze_adam_scripts": args.skip_adam_scripts,
        "extract_renv": args.skip_renv,
        "generate_pkg_descriptions": args.skip_pkg_describer,
    }

    # Run the workflow
    try:
        results = crew.kickoff(skip_flags=skip_flags)

        # Print final summary
        print("\n" + "="*80)
        print("📊 Workflow Results Summary")
        print("="*80)

        for task_id, result in results.items():
            status_emoji = {
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.SKIPPED: "⏭️"
            }.get(result.status, "❓")

            print(f"{status_emoji} {task_id}: {result.status.value}")
            if result.output_path:
                print(f"   Output: {result.output_path}")
            if result.error:
                print(f"   Error: {result.error}")

        # Print final output location
        if "assemble_document" in results:
            final_output = results["assemble_document"].output_path
            print(f"\n🎉 Final ADRG document: {final_output}")
            print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Workflow failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
