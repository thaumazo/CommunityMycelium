import os
import ast
import importlib.util
from pathlib import Path
from collections import defaultdict, deque
import sys

SEEDPACKS_DIR = Path(__file__).resolve().parents[3] / "seedpacks"

def ensure_utf8_encoding():
    if sys.getdefaultencoding() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

ensure_utf8_encoding()

def discover_seedpacks():
    return [p for p in SEEDPACKS_DIR.iterdir() if p.is_dir() and any(p.glob("seed_*.py"))]

def get_requires(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            node = ast.parse(f.read(), filename=str(path))
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if target.id == "REQUIRES":
                        return [elt.s for elt in item.value.elts if isinstance(elt, ast.Str)]
    except Exception:
        pass
    return []

def get_seed_order(seedpack_dir):
    seed_files = {f.stem: f for f in seedpack_dir.glob("seed_*.py")}
    graph = defaultdict(set)
    reverse_graph = defaultdict(set)

    for name, path in seed_files.items():
        requires = get_requires(path)
        for dep in requires:
            graph[f"seed_{dep}"].add(name)
            reverse_graph[name].add(f"seed_{dep}")
        if name not in reverse_graph:
            reverse_graph[name] = set()

    order = []
    queue = deque([n for n in seed_files if not reverse_graph[n]])

    while queue:
        current = queue.popleft()
        order.append(current)
        for dependent in graph[current]:
            reverse_graph[dependent].remove(current)
            if not reverse_graph[dependent]:
                queue.append(dependent)

    if len(order) != len(seed_files):
        raise ValueError("Cyclic dependencies detected in seedpack.")

    return [seed_files[o] for o in order]
