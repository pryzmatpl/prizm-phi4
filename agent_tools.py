
import os
from typing import List


class AgentTools:
    def search_files(file_list: List[str]) -> str:
        """
        Simulate a file search operation.

        Args:
            file_list: List of file names to search for.

        Returns:
            A string simulating the result of the file search.
        """
        try:
            # Simulated search result
            results = [f"Found: {file}" for file in file_list if os.path.exists(file)]
            return "\n".join(results) if results else "No files found."
        except Exception as e:
            return f"Error during file search: {str(e)}"

    def search_file_content(search_phrase: str, file_list: List[str]) -> str:
        """
        Simulate a content search operation in files.

        Args:
            search_phrase: The phrase to search for.
            file_list: List of file names to search in.

        Returns:
            A string simulating the result of the content search.
        """
        try:
            # Simulated content search result
            results = []
            for file in file_list:
                if os.path.exists(file):
                    with open(file, 'r') as f:
                        content = f.read()
                        if search_phrase in content:
                            results.append(f"Phrase found in: {file}")
            return "\n".join(results) if results else "Phrase not found in any files."
        except Exception as e:
            return f"Error during content search: {str(e)}"
