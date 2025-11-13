"""
Multi-Agent ADRG Generation Framework

This module provides a multi-agent workflow for generating ADRG documents.
It orchestrates specialized agents that work collaboratively to process
various input files and generate a comprehensive ADRG document.

Agents:
- Definexml Extraction Agent: SDTM/MedDRA versions from define.xml
- Protocol Analysis Agent: Protocol information from PDF
- Code Analysis Agent: R script analysis (TLF and ADaM scripts)
- ADaM Specification Agent: Variable descriptions and dependencies
- Package Documentation Agent: R package versions and descriptions
- Question Answering Agent: Yes/no questions in ADRG template
- Document Assembly Agent: Final document assembly and integration
"""

from multi_agent_adrg.agent_framework import (
    Agent,
    Task,
    Crew,
    TaskResult,
    TaskStatus
)

__all__ = [
    'Agent',
    'Task',
    'Crew',
    'TaskResult',
    'TaskStatus',
]
