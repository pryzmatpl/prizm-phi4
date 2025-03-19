import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from agent import Agent

class TestSearchCapabilities(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory with test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name
        
        # Create some test files
        self.create_test_files()
        
        # Initialize an agent with the temp directory
        self.agent = Agent(base_directory=self.test_dir, agent_config="linus")
        self.agent.search_directory()  # Populate search_results for content search tests
    
    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def create_test_files(self):
        # Create Python file
        with open(join(self.test_dir, 'test_code.py'), 'w') as f:
            f.write('def hello_world():\n    print("Hello, World!")\n\nclass TestClass:\n    def test_method(self):\n        return "testing"')
        
        # Create text file
        with open(join(self.test_dir, 'test_data.txt'), 'w') as f:
            f.write('This is a test file.\nIt contains test data.\nPython is a programming language.')
        
        # Create JSON file
        with open(join(self.test_dir, 'config.json'), 'w') as f:
            f.write('{"name": "Test Config", "version": 1.0, "python_compatible": true}')
            
        # Create a subdirectory with more files
        os.makedirs(join(self.test_dir, 'subdir'))
        with open(join(self.test_dir, 'subdir', 'nested_file.txt'), 'w') as f:
            f.write('This is a nested file.\nIn a subdirectory.\nIt also mentions python.')
    
    def test_file_search(self):
        """Test the file search capability"""
        # Test basic directory search
        files = self.agent.search_directory()
        self.assertEqual(len(files), 4)  # Should find all 4 test files
        
        # Test with file extension filter
        python_files = self.agent.search_directory(file_extensions=['.py'])
        self.assertEqual(len(python_files), 1)
        self.assertIn('test_code.py', python_files)
        
        # Test with subdirectory
        subdir_files = self.agent.search_directory(directory=join(self.test_dir, 'subdir'))
        self.assertEqual(len(subdir_files), 1)
        self.assertIn('nested_file.txt', subdir_files)
        
        # Test with non-existent directory
        with self.assertRaises(ValueError):
            self.agent.search_directory(directory="non_existent_dir")
    
    def test_content_search(self):
        """Test the content search capability"""
        # Test case-insensitive search (default)
        python_results = self.agent.find_string_in_files("python")
        self.assertEqual(len(python_results), 2)  # Should find in 2 text files
        
        # Test case-sensitive search
        python_results_case = self.agent.find_string_in_files("Python", case_sensitive=True)
        self.assertEqual(len(python_results_case), 1)  # Should only find in test_data.txt
        
        # Test with a pattern that should match all files
        test_results = self.agent.find_string_in_files("test")
        self.assertGreaterEqual(len(test_results), 3)
        
        # Test with a pattern that shouldn't match any files
        no_results = self.agent.find_string_in_files("nonexistentpattern")
        self.assertEqual(len(no_results), 0)
    
    @patch('agent.Agent.search_web')
    def test_web_search(self, mock_search_web):
        """Test the web search capability with mocked results"""
        # Define mock return value
        mock_results = [
            {"title": "Python Tutorial", "url": "https://www.example.com/python", "source": "Google"},
            {"title": "Learn Python Programming", "url": "https://www.example.com/learn", "source": "Bing"}
        ]
        mock_search_web.return_value = mock_results
        
        # Test the prompt analysis and web search operation
        operation, context = self.agent.analyze_prompt("Search web for Python tutorials")
        self.assertEqual(operation, "web_search")
        self.assertEqual(context, "Python tutorials")
        
        # Test the operation processing
        result = self.agent.process_operation("web_search", "Python tutorials")
        self.assertIn("Python Tutorial", result)
        self.assertIn("https://www.example.com/python", result)
        
    def test_prompt_analysis(self):
        """Test the prompt analysis functionality"""
        # Test file search prompts
        op1, ctx1 = self.agent.analyze_prompt("Can you search the directory?")
        self.assertEqual(op1, "file_search")
        
        op2, ctx2 = self.agent.analyze_prompt("Find files in the folder")
        self.assertEqual(op2, "file_search")
        
        # Test content search prompts
        op3, ctx3 = self.agent.analyze_prompt("Find python in files")
        self.assertEqual(op3, "content_search")
        
        op4, ctx4 = self.agent.analyze_prompt("Search for function inside content")
        self.assertEqual(op4, "content_search")
        
        # Test web search prompts
        op5, ctx5 = self.agent.analyze_prompt("Search web for AI tutorials")
        self.assertEqual(op5, "web_search")
        self.assertEqual(ctx5, "AI tutorials")
        
        # Test unrecognized prompt
        op6, ctx6 = self.agent.analyze_prompt("Hello, how are you today?")
        self.assertIsNone(op6)

if __name__ == "__main__":
    unittest.main() 