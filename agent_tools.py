
import os
from typing import List


class AgentTools:
    @classmethod
    def search_files(cls, file_list: List[str]) -> str:
        """
        Simulate a file search operation.
        """
        results = []
        for file in file_list:
            file_path = os.path.normpath(file.strip())
            if os.path.exists(file_path):
                results.append(f"Found: {file_path}")
            else:
                results.append(f"Not found: {file_path}")
        return "\n".join(results)

    @classmethod
    def search_file_content(cls, search_phrase: str, file_list: List[str]) -> str:
        """
        Simulate a content search operation in files.
        """
        results = []
        for file in file_list:
            file_path = os.path.normpath(file.strip())
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if search_phrase in content:
                            results.append(f"Phrase found in: {file_path}")
                        else:
                            results.append(f"Phrase not found in: {file_path}")
                except Exception as e:
                    results.append(f"Error reading {file_path}: {str(e)}")
            else:
                results.append(f"File not found: {file_path}")
        return "\n".join(results)