"""File system tools for agent.

This module provides tools for reading and writing files in the `files/` directory,
located at the project root.
"""

import os
from pathlib import Path
from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool

from agent.prompts import (
    LS_DESCRIPTION,
    READ_FILE_DESCRIPTION,
    WRITE_FILE_DESCRIPTION,
)


@tool(description=LS_DESCRIPTION)
def ls() -> str:
    """List all files in the files/ directory."""
    result = []
    files_dir = Path('files')
    if not files_dir.exists():
        return "Files directory is empty or does not exist"

    for root, _, files in os.walk(files_dir):
        for file in files:
            full_path = Path(root) / file
            relative_path = full_path.relative_to(files_dir)
            result.append(str(relative_path).replace(os.sep, '/'))

    return "\n".join(sorted(result)) if result else "Files directory is empty"


@tool(description=READ_FILE_DESCRIPTION, parse_docstring=True)
def read_file(
    file_path: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
    offset: int = 0,
    limit: int = 2000,
) -> ToolMessage:
    """Read file content from files/ directory with optional offset and limit.

    Args:
        file_path: Path to the file to read (relative to files/)
        tool_call_id: Tool call identifier for message response (injected in tool node)
        offset: Line number to start reading from (default: 0)
        limit: Maximum number of lines to read (default: 2000)

    Returns:
        ToolMessage with formatted file content with line numbers, or error message
    """
    full_path = Path('files') / file_path

    if not full_path.exists():
        return ToolMessage(
            content=f"Error: File '{file_path}' not found",
            tool_call_id=tool_call_id
        )

    try:
        content = full_path.read_text(encoding='utf-8')
    except Exception as e:
        return ToolMessage(
            content=f"Error reading file: {e}",
            tool_call_id=tool_call_id
        )

    if not content:
        return ToolMessage(
            content="System reminder: File exists but has empty contents",
            tool_call_id=tool_call_id
        )

    lines = content.splitlines()
    start_idx = offset
    end_idx = min(start_idx + limit, len(lines))

    if start_idx >= len(lines):
        return ToolMessage(
            content=f"Error: Line offset {offset} exceeds file length ({len(lines)} lines)",
            tool_call_id=tool_call_id
        )

    result_lines = []
    for i in range(start_idx, end_idx):
        line_content = lines[i][:2000]  # Truncate long lines
        result_lines.append(f"{i + 1:6d}\t{line_content}")

    return ToolMessage(
        content="\n".join(result_lines),
        tool_call_id=tool_call_id
    )


@tool(description=WRITE_FILE_DESCRIPTION, parse_docstring=True)
def write_file(
    file_path: str,
    content: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> ToolMessage:
    """Write content to a file in the files/ directory.

    Args:
        file_path: Path where the file should be created/updated (relative to files/)
        content: Content to write to the file
        tool_call_id: Tool call identifier for message response (injected in tool node)

    Returns:
        ToolMessage confirming the file was written
    """
    full_path = Path('files') / file_path

    # Create directory if it doesn't exist
    full_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        full_path.write_text(content, encoding='utf-8')
    except Exception as e:
        return ToolMessage(
            content=f"Error writing file: {e}",
            tool_call_id=tool_call_id
        )

    return ToolMessage(
        content=f"Successfully wrote to {file_path}",
        tool_call_id=tool_call_id
    )
