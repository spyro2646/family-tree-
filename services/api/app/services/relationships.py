from collections import defaultdict, deque
from collections.abc import Iterable
from uuid import UUID


def relationship_path(edges: Iterable[tuple[UUID, UUID]], start: UUID, target: UUID) -> list[UUID] | None:
    """Return the shortest undirected kinship path, or None if people are disconnected."""
    graph: dict[UUID, set[UUID]] = defaultdict(set)
    for parent, child in edges:
        graph[parent].add(child)
        graph[child].add(parent)
    queue = deque([start])
    previous: dict[UUID, UUID | None] = {start: None}
    while queue:
        current = queue.popleft()
        if current == target:
            path = []
            while current is not None:
                path.append(current)
                current = previous[current]  # type: ignore[assignment]
            return list(reversed(path))
        for neighbor in graph[current]:
            if neighbor not in previous:
                previous[neighbor] = current
                queue.append(neighbor)
    return None


def directed_path_exists(edges: Iterable[tuple[UUID, UUID]], start: UUID, target: UUID) -> bool:
    """Check whether target is already a descendant of start in parent-to-child edges."""
    children: dict[UUID, set[UUID]] = defaultdict(set)
    for parent, child in edges:
        children[parent].add(child)
    pending = [start]
    visited = {start}
    while pending:
        current = pending.pop()
        for child in children[current]:
            if child == target:
                return True
            if child not in visited:
                visited.add(child)
                pending.append(child)
    return False
