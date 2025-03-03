import json
import os
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import quote

class Agent:
    def __init__(self, base_directory: str = os.getcwd(), agent_config: str = None):
        """
        Initialize the Agent with a base directory and optional config file.

        Args:
            base_directory (str): Starting directory for file operations
            agent_config (str): Name of config file (without .json) to load prompt from
        """
        self.base_directory = os.path.abspath(base_directory)
        self.search_results = {}  # Cache for file search results
        self.other_agents = {}
        self.agent_prompt = self.load_agent_config_file(agent_config) if agent_config else {
            "prompt": "I am a general-purpose agent. How can I assist you?",
            "capabilities": ["file_search", "content_search", "web_search"]
        }

    def load_agent_config_file(self, agent_file: str) -> Dict[str, str]:
        """Load system prompt and capabilities from agents/[filename].json."""
        try:
            file_path = os.path.normpath(f'agents/{agent_file}.json')
            with open(file_path, "r", encoding="utf-8") as file:
                config = json.load(file)
                if "prompt" not in config or "capabilities" not in config:
                    raise ValueError("Config must contain 'prompt' and 'capabilities'")
                return config
        except Exception as e:
            raise ValueError(f'Error loading agent file {agent_file}: {str(e)}')

    def register_agent(self, other_agent_name: str, other_agent: "Agent") -> None:
        """Register another agent for potential collaboration."""
        self.other_agents[other_agent_name] = other_agent

    @staticmethod
    def analyze_prompt(self, user_prompt: str) -> Optional[str]:
        """Analyze user prompt to determine intended operation."""
        patterns = {
            "file_search": r"(search|find|look in|explore)\s+(directory|files|folder)",
            "content_search": r"(find|search|look for)\s+(.+?)\s+(in|within|inside)\s+(files|content)",
            "web_search": r"(search|look up|find)\s+(web|internet|online)\s+for\s+(.+)"
        }

        prompt_lower = user_prompt.lower()
        for operation, pattern in patterns.items():
            match = re.search(pattern, prompt_lower)
            if match:
                return operation, match.group(0) if operation != "web_search" else match.group(3)
        return None, None

    def process_operation(self, operation: str, context: str) -> str:
        """Execute the specified operation based on initial analysis."""
        if operation == "file_search":
            files = self.search_directory()
            return f"Found files: {', '.join(files.keys())}"
        elif operation == "content_search":
            search_string = context.split("find")[1].split("in")[0].strip()
            results = self.find_string_in_files(search_string)
            return "\n".join([f"In {k}: {', '.join(v)}" for k, v in results.items()])
        elif operation == "web_search":
            results = self.search_web(context)
            return "\n".join([f"[{r['source']}] {r['title']}: {r['url']}" for r in results])
        return "No operation executed."

    def handle_prompt(self, user_prompt: str) -> str:
        """
        Main pipeline to handle user prompts.

        1. Analyze prompt for specific operations
        2. Execute operation if detected
        3. Return results or generic response
        """
        operation, context = self.analyze_prompt(user_prompt)

        if operation:
            # Internal response directs the operation
            internal_response = f"Perform {operation} with context: {context}"
            operation_result = self.process_operation(operation, context or user_prompt)
            return f"{self.agent_prompt['prompt']}\nOperation result: {operation_result}"
        else:
            # No specific operation detected, return generic response
            return f"{self.agent_prompt['prompt']}\nI can help with file search, content search, or web search. What would you like to do?"

    # Existing methods (unchanged but included for completeness)
    def search_directory(self, directory: str = None, file_extensions: List[str] = None) -> Dict[str, str]:
        search_dir = os.path.abspath(directory) if directory else self.base_directory
        if not os.path.exists(search_dir):
            raise ValueError(f"Directory {search_dir} does not exist")
        found_files = {}
        for root, _, files in os.walk(search_dir):
            for file in files:
                if file_extensions:
                    if any(file.endswith(ext) for ext in file_extensions):
                        full_path = os.path.join(root, file)
                        found_files[file] = full_path
                else:
                    full_path = os.path.join(root, file)
                    found_files[file] = full_path
        self.search_results = found_files
        return found_files

    def find_string_in_files(self, search_string: str, case_sensitive: bool = False) -> Dict[str, List[str]]:
        if not self.search_results:
            raise ValueError("No files have been searched yet. Run search_directory first.")
        results = {}
        flags = 0 if case_sensitive else re.IGNORECASE
        for filename, filepath in self.search_results.items():
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    matching_lines = [line.strip() for line in lines if re.search(search_string, line, flags)]
                    if matching_lines:
                        results[filename] = matching_lines
            except (UnicodeDecodeError, IOError):
                continue
        return results

    @staticmethod
    def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        google_url = f"https://www.google.com/search?q={quote(query)}&num={num_results}"
        bing_url = f"https://www.bing.com/search?q={quote(query)}&count={num_results}"
        results = []

        for url, source in [(google_url, "Google"), (bing_url, "Bing")]:
            try:
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                items = soup.select('div.g' if source == "Google" else 'li.b_algo')[:num_results]
                for item in items:
                    link = item.find('a', href=True)
                    title = item.find('h3' if source == "Google" else 'h2')
                    if link and title:
                        results.append({'title': title.text, 'url': link['href'], 'source': source})
            except Exception as e:
                print(f"{source} search failed: {e}")
        return results[:num_results * 2]

