from langchain_core.tools import tool


PROJECT_DIR = 'project'


def find_file_by_name(regexp: str) -> str:
    """Find a file by regexp name in the project directory."""
    import os
    import re

    if not os.path.exists(PROJECT_DIR):
        return f"Project directory '{PROJECT_DIR}' does not exist"

    pattern = re.compile(regexp)
    matches = []

    for root, dirs, files in os.walk(PROJECT_DIR):
        for file in files:
            if pattern.search(file):
                matches.append(
                    os.path.join(root, file).replace(f'{PROJECT_DIR}/', '')
                )

    if not matches:
        return f"No files matching pattern '{regexp}' found in {PROJECT_DIR}"

    return f"Found {len(matches)} file(s):\n" + "\n".join(matches)


def find_code_by_regex(pattern: str) -> str:
    """Search for code matching a regex pattern in the project directory."""
    import os
    import re

    if not os.path.exists(PROJECT_DIR):
        return f"Project directory '{PROJECT_DIR}' does not exist"

    regex = re.compile(pattern)
    matches = []

    for root, dirs, files in os.walk(PROJECT_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if regex.search(line):
                            matches.append(
                                f"{filepath.replace(f'{PROJECT_DIR}/', '')}:{i}: {line.strip()}")
            except:
                continue

    if not matches:
        return f"No code matching pattern '{pattern}' found in {PROJECT_DIR}"

    return (
        f"Found {len(matches)} match(es):\n"
        + "\n".join(matches[:50])
        + ("\n... (more matches)" if len(matches) > 50 else "")
    )


@tool
def read_file_lines(filename: str, start_line: int = 1, end_line: int = -1) -> str:
    """Read specific lines from a file in the project directory."""
    import os

    if not os.path.exists(PROJECT_DIR):
        return f"Project directory '{PROJECT_DIR}' does not exist"

    filepath = os.path.join(PROJECT_DIR, filename)
    if not os.path.exists(filepath):
        return f"File '{filename}' not found in {PROJECT_DIR}"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if end_line == -1:
            end_line = len(lines)

        if start_line < 1:
            start_line = 1
        if end_line > len(lines):
            end_line = len(lines)

        selected_lines = lines[start_line - 1: end_line]
        result = []
        for i, line in enumerate(selected_lines, start_line):
            result.append(f"{i}: {line.rstrip()}")

        return f"File: {filepath} (lines {start_line}-{end_line}):\n" + "\n".join(
            result
        )
    except Exception as e:
        return f"Error reading file: {str(e)}"


read_project_tools = [find_code_by_regex, find_file_by_name, read_file_lines]
