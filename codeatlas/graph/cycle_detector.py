"""Cycle detector for directed graphs using depth-first search."""


class CycleDetector:
    """Detects cycles in a directed graph represented as an adjacency list."""

    @staticmethod
    def detect(graph: dict[str, list[str]]) -> list[list[str]]:
        """Return all cycles found in *graph*.

        Each cycle is represented as a list of node identifiers.  The
        algorithm uses iterative DFS and returns simple cycles.
        """
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: list[list[str]] = []

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbour in graph.get(node, []):
                if neighbour not in visited:
                    dfs(neighbour, path)
                elif neighbour in rec_stack:
                    # Found a cycle — extract it
                    cycle_start = path.index(neighbour)
                    cycle = path[cycle_start:]
                    if cycle not in cycles:
                        cycles.append(list(cycle))

            path.pop()
            rec_stack.discard(node)

        for node in list(graph.keys()):
            if node not in visited:
                dfs(node, [])

        return cycles
