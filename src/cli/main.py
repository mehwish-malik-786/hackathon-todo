"""CLI layer: Main entry point and argument parsing."""
import argparse
import sys
from typing import List, Optional
from .commands import (
    handle_add,
    handle_list,
    handle_update,
    handle_delete,
    handle_complete,
)
from src.infrastructure.in_memory_repository import InMemoryTaskRepository
from src.domain.exceptions import TaskNotFoundError


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Task management CLI - Track your todos from the command line",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser(
        "add",
        help="Create a new task",
        description="Create a new task with a title and optional description",
    )
    add_parser.add_argument(
        "title",
        type=str,
        help="Task title (required, 1-200 characters)",
    )
    add_parser.add_argument(
        "--description",
        "-d",
        type=str,
        default=None,
        help="Task description (optional, max 1000 characters)",
    )

    # List command
    subparsers.add_parser(
        "list",
        help="Display all tasks",
        description="Show all tasks with their details",
    )

    # Update command
    update_parser = subparsers.add_parser(
        "update",
        help="Update an existing task",
        description="Update task title and/or description by ID",
    )
    update_parser.add_argument(
        "id",
        type=int,
        help="Task ID to update",
    )
    update_parser.add_argument(
        "--title",
        "-t",
        type=str,
        default=None,
        help="New title (optional)",
    )
    update_parser.add_argument(
        "--description",
        "-d",
        type=str,
        default=None,
        help="New description (optional)",
    )

    # Delete command
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a task",
        description="Remove a task by ID",
    )
    delete_parser.add_argument(
        "id",
        type=int,
        help="Task ID to delete",
    )

    # Complete command
    complete_parser = subparsers.add_parser(
        "complete",
        help="Mark a task as completed",
        description="Mark a task as completed by ID",
    )
    complete_parser.add_argument(
        "id",
        type=int,
        help="Task ID to complete",
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    CLI entry point.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 = success, 1 = error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 1

    # Shared repository instance (in-memory, no persistence)
    repository = InMemoryTaskRepository()

    try:
        if parsed_args.command == "add":
            handle_add(repository, parsed_args.title, parsed_args.description)
        elif parsed_args.command == "list":
            handle_list(repository)
        elif parsed_args.command == "update":
            handle_update(repository, parsed_args.id, parsed_args.title, parsed_args.description)
        elif parsed_args.command == "delete":
            handle_delete(repository, parsed_args.id)
        elif parsed_args.command == "complete":
            handle_complete(repository, parsed_args.id)
        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except TaskNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
