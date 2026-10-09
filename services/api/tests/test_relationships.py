from uuid import uuid4

from app.services.relationships import directed_path_exists, relationship_path


def test_relationship_path_finds_shortest_path() -> None:
    grandparent, parent, child, cousin = (uuid4() for _ in range(4))
    edges = [(grandparent, parent), (parent, child), (grandparent, cousin)]
    assert relationship_path(edges, child, cousin) == [child, parent, grandparent, cousin]


def test_relationship_path_returns_none_for_separate_branches() -> None:
    first, second, third = (uuid4() for _ in range(3))
    assert relationship_path([(first, second)], first, third) is None


def test_cycle_detection_follows_parent_to_child_direction() -> None:
    parent, child, sibling = (uuid4() for _ in range(3))
    edges = [(parent, child), (parent, sibling)]
    # Adding child as parent of parent would close the parent -> child path into a cycle.
    assert directed_path_exists(edges, parent, child)
    # Sibling and child share a parent, but that alone does not form a directed cycle.
    assert not directed_path_exists(edges, child, sibling)
