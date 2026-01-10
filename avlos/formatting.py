"""
Code formatting utilities for generated code.
"""
import subprocess
import shutil
import sys
from pathlib import Path


def is_clang_format_available() -> bool:
    """Check if clang-format is installed on the system."""
    return shutil.which("clang-format") is not None


def format_c_code(file_path: str, style: str = "LLVM") -> bool:
    """
    Format C/C++ code using clang-format.

    Args:
        file_path: Path to file to format
        style: clang-format style (LLVM, Google, Chromium, Mozilla, WebKit, Microsoft, GNU)

    Returns:
        True if formatting succeeded, False if clang-format not available or failed
    """
    if not is_clang_format_available():
        return False

    try:
        result = subprocess.run(
            ["clang-format", "-i", f"--style={style}", file_path],
            capture_output=True,
            timeout=10,
            check=False
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False


def format_files(file_paths: list, style: str = "LLVM") -> dict:
    """
    Format multiple C/C++ files.

    Args:
        file_paths: List of file paths to format
        style: clang-format style

    Returns:
        Dictionary mapping file path to success status
    """
    results = {}
    for path in file_paths:
        results[path] = format_c_code(path, style)
    return results
