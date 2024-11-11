import os
import sys
import yaml
import subprocess
from typing import List
import unittest


class GitVisualizer:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.repo_path = self.config['repo_path']
        self.output_file = self.config['output_file']
        self.branch_name = self.config['branch_name']
        self.graphviz_path = self.config['graphviz_path']

    def load_config(self, config_path: str) -> dict:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def get_commits(self) -> List[dict]:
        """
        Получает список коммитов из указанной ветки.
        """
        original_cwd = os.getcwd()
        os.chdir(self.repo_path)
        try:
            cmd = [
                'git',
                'log',
                self.branch_name,
                '--pretty=format:%H|%s|%P'
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 2)
                    if len(parts) == 3:
                        commit_hash, message, parent_hashes = parts
                    else:
                        commit_hash, message = parts
                        parent_hashes = ''
                    parents = parent_hashes.strip().split()
                    commits.append({
                        'hash': commit_hash,
                        'message': message,
                        'parents': parents
                    })
            return commits
        finally:
            os.chdir(original_cwd)

    def build_graph(self, commits: List[dict]) -> str:
        """
        Строит граф в формате PlantUML.
        """
        graph = ['@startuml']
        graph.append('skinparam rectangle {')
        graph.append('   BackgroundColor #FDF6E3')
        graph.append('}')

        commit_defs = {}
        for idx, commit in enumerate(reversed(commits)):
            commit_id = f'Commit{idx + 1}'
            commit_defs[commit['hash']] = commit_id
            graph.append(f'rectangle "{commit["message"]}" as {commit_id}')

        # Добавляем связи между коммитами
        for commit in reversed(commits):
            child_id = commit_defs[commit['hash']]
            for parent_hash in commit['parents']:
                if parent_hash in commit_defs:
                    parent_id = commit_defs[parent_hash]
                    graph.append(f'{parent_id} <|-- {child_id}')

        graph.append('@enduml')
        return '\n'.join(graph)

    def save_output(self, content: str):
        with open(self.output_file, 'w') as file:
            file.write(content)

    def run(self):
        commits = self.get_commits()
        graph_content = self.build_graph(commits)
        self.save_output(graph_content)
        print(f"PlantUML code has been written to {self.output_file}")


# Если скрипт запускается напрямую
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_config.yaml>")
        sys.exit(1)
    config_path = sys.argv[1]
    visualizer = GitVisualizer(config_path)
    visualizer.run()
