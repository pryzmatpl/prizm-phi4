import logging

import bs4
import os
import requests
from typing import List


class AgentTools:

    @classmethod
    def search_files(cls, file_list: List[str]) -> str:
        """
        Simulate a file search operation.
        """
        results = []
        logging.debug(f"searching files {file_list}")
        for file in file_list:
            file_path = os.path.abspath(os.path.normpath(file.strip()))
            if os.path.exists(file_path):
                results.append(f"Found: {file_path}")
            else:
                results.append(f"Not found: {file_path}")
        return "AGENTRESP SEARCH, ".join(results)

    @classmethod
    def search_file_content(cls, search_phrase: str, file_list: List[str]) -> str:
        """
        Simulate a content search operation in files.
        """
        results = []
        logging.debug(f"searching {search_phrase} in {file_list}")
        for file in file_list:
            file_path = os.path.abspath(os.path.normpath(file.strip()))
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
        return "AGENTRESP CONTENTSEARCH, ".join(results)

    @classmethod
    def search_web(cls, query: str, engine: str = "duckduckgo") -> str:
        """
        Perform a real web search using DuckDuckGo or Bing.

        Args:
            query (str): The search query.
            engine (str): The search engine to use ("duckduckgo" or "bing").

        Returns:
            str: A list of search results with titles and links or an error message.
        """
        logging.debug(f"searching {query} and {engine}")
        try:
            if engine.lower() == "duckduckgo":
                # DuckDuckGo API
                search_url = "https://api.duckduckgo.com/"
                params = {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
                response = requests.get(search_url, params=params, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    search_results = data.get("RelatedTopics", [])

                    if not search_results:
                        return f"No results found on DuckDuckGo for: {query}"

                    # Extract top results
                    results = []
                    for result in search_results[:5]:  # Limit to top 5
                        if "Text" in result and "FirstURL" in result:
                            results.append(f"{result['Text']} - {result['FirstURL']}")

                    return "AGENTRESP WEBSEARCH, ".join(results) if results else f"No results found on DuckDuckGo for: {query}"

            elif engine.lower() == "bing":
                # Bing Search API (Free Tier via Microsoft)
                search_url = "https://www.bing.com/search"
                params = {"q": query}
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(search_url, params=params, headers=headers, timeout=5)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    search_results = soup.find_all("li", {"class": "b_algo"})[:5]  # Limit to top 5

                    if not search_results:
                        return f"No results found on Bing for: {query}"

                    results = []
                    for result in search_results:
                        title = result.find("h2").text if result.find("h2") else "No Title"
                        link = result.find("a")["href"] if result.find("a") else "No Link"
                        results.append(f"{title} - {link}")

                    return "AGENTRESP WEBSEARCH, ".join(results) if results else f"No results found on Bing for: {query}"

            else:
                return "Error: Unsupported search engine. Use 'duckduckgo' or 'bing'."

        except requests.exceptions.RequestException as e:
            return f"Error: Web search failed due to {str(e)}."

        except Exception as e:
            return f"Unexpected error: {str(e)}"

        return f"Error: No results returned for {query}."
