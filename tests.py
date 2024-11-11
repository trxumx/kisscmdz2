import unittest
from unittest.mock import patch, MagicMock
from main import GitVisualizer


class TestGitVisualizer(unittest.TestCase):
    def setUp(self):
        # Замените 'config.yaml' на актуальный путь к вашему файлу конфигурации
        self.visualizer = GitVisualizer('config.yaml')

    @patch('main.GitVisualizer.load_config')
    def test_load_config(self, mock_load_config):
        mock_load_config.return_value = {
            'repo_path': '/path/to/repo',
            'output_file': 'output.puml',
            'branch_name': 'main',
            'graphviz_path': '/usr/local/bin/plantuml'
        }
        config = self.visualizer.load_config('config.yaml')
        self.assertEqual(config['repo_path'], '/path/to/repo')

    @patch('main.subprocess.run')
    def test_get_commits(self, mock_subproc_run):
        mock_subproc_run.return_value = MagicMock(stdout='hash1|Initial commit|\nhash2|Second commit|hash1')
        commits = self.visualizer.get_commits()
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0]['message'], 'Initial commit')

    def test_build_graph(self):
        commits = [
            {'hash': 'hash1', 'message': 'Initial commit', 'parents': []},
            {'hash': 'hash2', 'message': 'Second commit', 'parents': ['hash1']}
        ]
        graph = self.visualizer.build_graph(commits)
        expected_graph = '''@startuml
skinparam rectangle {
   BackgroundColor #FDF6E3
}
rectangle "Second commit" as Commit1
rectangle "Initial commit" as Commit2
Commit2 <|-- Commit1
@enduml'''
        self.assertEqual(graph.strip(), expected_graph.strip())

    @patch('builtins.print')
    @patch('main.GitVisualizer.save_output')
    @patch('main.GitVisualizer.build_graph')
    @patch('main.GitVisualizer.get_commits')
    def test_run(self, mock_get_commits, mock_build_graph, mock_save_output, mock_print):
        mock_get_commits.return_value = []
        mock_build_graph.return_value = '@startuml\n@enduml'
        self.visualizer.run()
        mock_get_commits.assert_called_once()
        mock_build_graph.assert_called_once()
        mock_save_output.assert_called_once_with('@startuml\n@enduml')
        mock_print.assert_called_once_with('PlantUML code has been written to output.puml')


if __name__ == '__main__':
    unittest.main()
