"""Testing search tree balancing."""

import random
from st import (
    Ord,
    Tree, Node, Empty,
)


def test_tree() -> None:
    """Test that we still have a working search tree."""
    x: list[int] = random.sample(range(0, 10), 5)
    t = Tree[int]()
    for i, a in enumerate(x):
        t.insert(a)
        print("AFTER INSERTING", x[:i+1], ":", t)
        for b in x[:i+1]:
            assert b in t
    for i, a in enumerate(x):
        print("BEFORE REMOVE", t)
        t.remove(a)
        for b in x[:i+1]:
            assert b not in t
    assert not t


def is_balanced(n: Node[Ord]) -> bool:
    """Check if this tree is balanced."""
    if n is Empty:
        return True
    if not (-2 < n.bf < +2):
        print("FOOOOOOOO", n)
    return -2 < n.bf < +2 and \
        is_balanced(n.left) and is_balanced(n.right)


# This will fail, because the tree isn't balanced
def test_balanced() -> None:
    """Test that we have a balanced tree."""
    x: list[int] = random.sample(range(0, 20), 20)
    t = Tree[int]()
    for a in x:
        t.insert(a)
        print()
        print('hep', t)
        print()
        assert is_balanced(t.root)
    for a in x:
        t.remove(a)
        print()
        print('hep', t)
        print()
        assert is_balanced(t.root)
    assert not t
