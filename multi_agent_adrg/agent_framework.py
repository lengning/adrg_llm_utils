#!/usr/bin/env python3
"""
Multi-Agent Framework for ADRG Generation
Uses LangChain agents to orchestrate parallel and sequential tasks
"""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import subprocess
import sys


class TaskStatus(Enum):
    """Status of a task execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskResult:
    """Result of a task execution"""
    task_id: str
    status: TaskStatus
    output_path: Optional[Path] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Agent:
    """
    Base Agent class representing a specialized worker in the ADRG generation pipeline.
    Each agent is responsible for a specific task and has access to specific tools.
    """

    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[str]] = None,
        verbose: bool = True
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.verbose = verbose

    def __repr__(self):
        return f"Agent(name='{self.name}', role='{self.role}')"

    def execute_task(self, task: 'Task', context: Dict[str, Any]) -> TaskResult:
        """
        Execute a task using this agent's capabilities.

        Args:
            task: The task to execute
            context: Shared context dictionary with inputs from previous tasks

        Returns:
            TaskResult with output path and metadata
        """
        if self.verbose:
            print(f"\n[{self.name}] Starting task: {task.description}")
            print(f"[{self.name}] Goal: {self.goal}")

        try:
            # Execute the task's action
            result = task.action(context)

            if self.verbose:
                print(f"[{self.name}] ✓ Task completed successfully")

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                output_path=result.get('output_path'),
                metadata=result
            )

        except Exception as e:
            if self.verbose:
                print(f"[{self.name}] ✗ Task failed: {str(e)}")

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )


class Task:
    """
    Represents a task to be executed by an agent.
    """

    def __init__(
        self,
        task_id: str,
        description: str,
        agent: Agent,
        action: Callable[[Dict[str, Any]], Dict[str, Any]],
        dependencies: Optional[List[str]] = None,
        config_key: Optional[str] = None,
        skippable: bool = False
    ):
        self.task_id = task_id
        self.description = description
        self.agent = agent
        self.action = action
        self.dependencies = dependencies or []
        self.config_key = config_key
        self.skippable = skippable
        self.status = TaskStatus.PENDING

    def can_execute(self, completed_tasks: List[str]) -> bool:
        """Check if all dependencies are satisfied"""
        return all(dep in completed_tasks for dep in self.dependencies)

    def __repr__(self):
        return f"Task(id='{self.task_id}', agent='{self.agent.name}', dependencies={self.dependencies})"


class Crew:
    """
    Orchestrates multiple agents to complete a complex workflow.
    Manages task dependencies and parallel execution where possible.
    """

    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        config: Dict[str, Any],
        verbose: bool = True
    ):
        self.agents = {agent.name: agent for agent in agents}
        self.tasks = {task.task_id: task for task in tasks}
        self.config = config
        self.verbose = verbose
        self.context = {}
        self.results = {}

    def kickoff(self, skip_flags: Optional[Dict[str, bool]] = None) -> Dict[str, TaskResult]:
        """
        Execute the workflow by running all tasks in dependency order.

        Args:
            skip_flags: Dictionary of task_id -> bool indicating which tasks to skip

        Returns:
            Dictionary of task_id -> TaskResult
        """
        skip_flags = skip_flags or {}
        completed_tasks = []
        failed_tasks = []

        if self.verbose:
            print("\n" + "="*80)
            print("🚀 Multi-Agent ADRG Generation Workflow")
            print("="*80)
            print(f"\nTotal agents: {len(self.agents)}")
            print(f"Total tasks: {len(self.tasks)}")
            print("\nAgents:")
            for agent in self.agents.values():
                print(f"  - {agent.name}: {agent.role}")
            print("\n" + "="*80 + "\n")

        # Continue until all tasks are completed or failed
        while len(completed_tasks) + len(failed_tasks) < len(self.tasks):
            # Find tasks that can be executed
            executable_tasks = []

            for task_id, task in self.tasks.items():
                if task_id in completed_tasks or task_id in failed_tasks:
                    continue

                # Skip if requested
                if skip_flags.get(task_id, False):
                    if self.verbose:
                        print(f"⏭️  Skipping task: {task.task_id}")
                    completed_tasks.append(task_id)
                    self.results[task_id] = TaskResult(
                        task_id=task_id,
                        status=TaskStatus.SKIPPED
                    )
                    continue

                # Check if dependencies are satisfied
                if task.can_execute(completed_tasks):
                    executable_tasks.append(task)

            # If no tasks can be executed, we have a problem
            if not executable_tasks:
                remaining_tasks = set(self.tasks.keys()) - set(completed_tasks) - set(failed_tasks)
                if remaining_tasks:
                    error_msg = f"Workflow stuck. Cannot execute remaining tasks: {remaining_tasks}"
                    if self.verbose:
                        print(f"\n❌ {error_msg}\n")
                    raise RuntimeError(error_msg)
                break

            # Execute all executable tasks (they can run in parallel conceptually)
            for task in executable_tasks:
                result = task.agent.execute_task(task, self.context)
                self.results[task.task_id] = result

                if result.status == TaskStatus.COMPLETED:
                    completed_tasks.append(task.task_id)
                    # Store outputs in context for downstream tasks
                    if result.output_path:
                        self.context[task.task_id] = {
                            'output_path': result.output_path,
                            'metadata': result.metadata
                        }
                elif result.status == TaskStatus.FAILED:
                    failed_tasks.append(task.task_id)
                    if not task.skippable:
                        # If task is not skippable, fail the entire workflow
                        if self.verbose:
                            print(f"\n❌ Critical task failed: {task.task_id}")
                            print(f"   Error: {result.error}\n")
                        raise RuntimeError(f"Critical task '{task.task_id}' failed: {result.error}")

        if self.verbose:
            print("\n" + "="*80)
            print("✅ Workflow Completed!")
            print("="*80)
            print(f"\nCompleted tasks: {len(completed_tasks)}")
            print(f"Failed tasks: {len(failed_tasks)}")
            print(f"Skipped tasks: {len([r for r in self.results.values() if r.status == TaskStatus.SKIPPED])}")
            print()

        return self.results

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result of a specific task"""
        return self.results.get(task_id)


def run_python_module(module_path: str, args: List[str]) -> subprocess.CompletedProcess:
    """Helper to run a Python module"""
    cmd = [sys.executable, module_path] + args
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def resolve_path(path_value: str, root_dir: Path) -> Path:
    """Resolve a path from config (handles both absolute and relative)"""
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        path = root_dir / path
    return path
