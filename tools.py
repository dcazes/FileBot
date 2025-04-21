# file_tools.py
import os
import shutil
import zipfile
from pathlib import Path
from pydantic_ai import Agent
import logging

logger = logging.getLogger(__name__)

allowed_paths = [Path(p) for p in os.getenv("ALLOWED_PATHS", "").split(",") if p]

def is_allowed(path: str) -> bool:
    path_obj = Path(path)
    return any(path_obj.is_relative_to(allowed) for allowed in allowed_paths)

agent = Agent()  # Will be configured in agent.py

@agent.tool_plain
def rename_file(old_path: str, new_path: str) -> str:
    """
    Rename a file from old_path to new_path.

    :param old_path: Current path of the file.
    :param new_path: New path for the file.
    :return: Success message or error.
    """
    try:
        if not is_allowed(old_path) or not is_allowed(new_path):
            return "Error: Paths not allowed"
        os.rename(old_path, new_path)
        logger.info(f"Renamed {old_path} to {new_path}")
        return f"Successfully renamed {old_path} to {new_path}"
    except Exception as e:
        logger.error(f"Error renaming {old_path}: {e}")
        return f"Error: {str(e)}"

@agent.tool_plain
def move_file(source: str, destination: str) -> str:
    """
    Move a file from source to destination.

    :param source: Source path of the file.
    :param destination: Destination path for the file.
    :return: Success message or error.
    """
    try:
        if not is_allowed(source) or not is_allowed(destination):
            return "Error: Paths not allowed"
        shutil.move(source, destination)
        logger.info(f"Moved {source} to {destination}")
        return f"Successfully moved {source} to {destination}"
    except Exception as e:
        logger.error(f"Error moving {source}: {e}")
        return f"Error: {str(e)}"

@agent.tool_plain
def copy_file(source: str, destination: str) -> str:
    """
    Copy a file from source to destination.

    :param source: Source path of the file.
    :param destination: Destination path for the file.
    :return: Success message or error.
    """
    try:
        if not is_allowed(source) or not is_allowed(destination):
            return "Error: Paths not allowed"
        shutil.copy2(source, destination)
        logger.info(f"Copied {source} to {destination}")
        return f"Successfully copied {source} to {destination}"
    except Exception as e:
        logger.error(f"Error copying {source}: {e}")
        return f"Error: {str(e)}"

@agent.tool_plain
def delete_file(path: str) -> str:
    """
    Delete a file at the specified path.

    :param path: Path of the file to delete.
    :return: Success message or error.
    """
    try:
        if not is_allowed(path):
            return "Error: Path not allowed"
        os.remove(path)
        logger.info(f"Deleted {path}")
        return f"Successfully deleted {path}"
    except Exception as e:
        logger.error(f"Error deleting {path}: {e}")
        return f"Error: {str(e)}"

@agent.tool_plain
def create_file(path: str, content: str = "") -> str:
    """
    Create a new file with optional content.

    :param path: Path for the new file.
    :param content: Content to write to the file.
    :return: Success message or error.
    """
    try:
        if not is_allowed(path):
            return "Error: Path not allowed"
        with open(path, "w") as f:
            f.write(content)
        logger.info(f"Created file {path}")
        return f"Successfully created {path}"
    except Exception as e:
        logger.error(f"Error creating {path}: {e}")
        return f"Error: {str(e)}"

@agent.tool_plain
def create_directory(path: str) -> str:
    """
    Create a new directory.

    :param path: Path for the new directory.
    :return: Success message or error.
    """
    try:
        if not is_allowed(path):
            return "Error: Path not allowed"
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory {path}")
        return f"Successfully created {path}"
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return f"Error: {str(e)}"

@agent.tool_plain
def zip_files(zip_path: str, file_paths: list[str]) -> str:
    """
    Create a zip file containing specified files.

    :param zip_path: Path for the zip file.
    :param file_paths: List of file paths to zip.
    :return: Success message or error.
    """
    try:
        if not is_allowed(zip_path) or not all(is_allowed(p) for p in file_paths):
            return "Error: Paths not allowed"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in file_paths:
                zf.write(path, os.path.basename(path))
        logger.info(f"Created zip {zip_path}")
        return f"Successfully created zip {zip_path}"
    except Exception as e:
        logger.error(f"Error creating zip {zip_path}: {e}")
        return f"Error: {str(e)}"

@agent.tool_plain
def search_files(query: str) -> str:
    """
    Search files by name or metadata (placeholder).

    :param query: Search query (e.g., name pattern).
    :return: List of matching files or error.
    """
    try:
        # Placeholder: Implement Graphiti search
        return "Search not implemented"
    except Exception as e:
        logger.error(f"Error searching files: {e}")
        return f"Error: {str(e)}"