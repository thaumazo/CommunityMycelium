import os
import sys
import ast
from collections import defaultdict, deque

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Prints an ordered list of seed commands based on declared REQUIRES metadata"

    def handle(self, *args, **options):
        base_path = os.path.join(settings.BASE_DIR, "apps")
        commands = {}
        graph = defaultdict(set)
        reverse_graph = defaultdict(set)

        for app in os.listdir(base_path):
            cmd_path = os.path.join(base_path, app, "management", "commands", f"seed_{app}.py")
            if not os.path.isfile(cmd_path):
                continue

            cmd_name = f"seed_{app}"
            commands[cmd_name] = cmd_path

            requires = self.get_requires_from_file(cmd_path)
            for dep in requires:
                dep_cmd = f"seed_{dep}"
                graph[dep_cmd].add(cmd_name)
                reverse_graph[cmd_name].add(dep_cmd)

                if dep_cmd not in commands:
                    commands[dep_cmd] = None  # virtual node

        # Topological sort
        order = []
        queue = deque([cmd for cmd in commands if not reverse_graph[cmd]])

        while queue:
            current = queue.popleft()
            order.append(current)
            for dependent in graph[current]:
                reverse_graph[dependent].remove(current)
                if not reverse_graph[dependent]:
                    queue.append(dependent)

        if len(order) != len(commands):
            self.stderr.write("Cyclic dependency detected!\n")
            sys.exit(1)

        for cmd in order:
            print(cmd)

    def get_requires_from_file(self, path):
        """Parses the seed file using ast to extract the REQUIRES variable, if it exists."""
        try:
            with open(path, "r") as f:
                node = ast.parse(f.read(), filename=path)

            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "REQUIRES":
                            if isinstance(item.value, ast.List):
                                return [elt.s for elt in item.value.elts if isinstance(elt, ast.Str)]
            return []
        except Exception as e:
            self.stderr.write(f"Error parsing {path}: {e}")
            return []
