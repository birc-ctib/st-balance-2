"""A balanced search Node."""

from __future__ import annotations
from abc import (
    ABC,
    abstractmethod
)
from dataclasses import (
    dataclass
)
from typing import (
    Protocol, TypeVar, Generic,
    Optional,
    Any,
    cast
)


# Some type stuff
class Ordered(Protocol):
    """Types that support < comparison."""

    def __lt__(self: Ord, other: Ord) -> bool:
        """Determine if self is < other."""
        ...


Ord = TypeVar('Ord', bound=Ordered)

# Node structure


class Node(Generic[Ord], ABC):
    """Abstract Node."""

    parent: Optional[InnerNode[Ord]]  # Pointer to the node's parent

    @property
    @abstractmethod
    def value(self) -> Ord:
        """Get the value in the root of the node."""
        ...

    @property
    @abstractmethod
    def left(self) -> Node[Ord]:
        """Get the left sub-tree."""
        ...

    @property
    @abstractmethod
    def right(self) -> Node[Ord]:
        """Get the right sub-tree."""
        ...

    @property
    @abstractmethod
    def height(self) -> int:
        """Get the tree height."""
        ...

    @property
    def bf(self) -> int:
        """Get the balancing factor."""
        return self.right.height - self.left.height

    @property
    def is_left(self) -> bool:
        """Tell us if this is a left child."""
        return self.parent is not None and self.parent.left == self

    @property
    def is_right(self) -> bool:
        """Tell us if this is a right child."""
        return self.parent is not None and self.parent.right == self


class EmptyClass(Node[Ord]):
    """Empty tree."""

    # This is some magick to ensure we never have more
    # than one empty Node.
    _instance: Optional[EmptyClass[Any]] = None

    def __new__(cls) -> EmptyClass[Any]:
        """Create a new empty tree."""
        if cls._instance is None:
            cls._instance = super(EmptyClass, cls).__new__(cls)
            cls._instance.parent = None
        return cls._instance

    def __repr__(self) -> str:
        """Return 'Empty'."""
        return "Empty"

    @property
    def value(self) -> Ord:
        """Raise an exception."""
        raise AttributeError("No value on an empty tree")

    @property
    def left(self) -> Node[Ord]:
        """Return an empty tree."""
        return Empty

    @property
    def right(self) -> Node[Ord]:
        """Return an empty tree."""
        return Empty

    @property
    def bf(self) -> int:
        """Get the balance factor."""
        return 0

    @property
    def height(self) -> int:
        """Get the tree height."""
        return 0

    def __str__(self) -> str:
        """Return textual representation."""
        return "*"


# This is the one and only empty Node
Empty = EmptyClass()


@dataclass
class InnerNode(Node[Ord]):
    """
    Inner node in the search tree.

    All the _attr attributes are mutable, and you are supposed to update
    nodes instead of creating new ones (except for the new leaves you will
    obviously have to make when you insert values into a tree).

    The balancing factor, _bf, replaces the _height now. We don't want to
    have to keep track of the height when we move trees around.
    """

    _value: Ord
    _left: Node[Ord] = Empty
    _right: Node[Ord] = Empty
    _height: int = 0
    parent: Optional[InnerNode[Ord]] = None

    def __post_init__(self) -> None:
        """Connect parent pointers."""
        self._left.parent = self
        self._right.parent = self
        self._height = max(self.left.height, self.right.height) + 1

    @property
    def value(self) -> Ord:
        """Get the value in the node."""
        return self._value

    @value.setter
    def value(self, val: Ord) -> None:
        """Set the value in the node."""
        self._value = val

    @property
    def left(self) -> Node[Ord]:
        """Get the left sub-tree."""
        return self._left

    @left.setter
    def left(self, val: Node[Ord]) -> None:
        """Set the left child."""
        self._left = val
        self._left.parent = self
        self._height = max(self.left.height, self.right.height) + 1

    @property
    def right(self) -> Node[Ord]:
        """Get the right sub-tree."""
        return self._right

    @right.setter
    def right(self, val: Node[Ord]) -> None:
        """Set the right child."""
        self._right = val
        self._right.parent = self
        self._height = max(self.left.height, self.right.height) + 1

    @property
    def height(self) -> int:
        """Get the height of this tree."""
        return self._height

    def __str__(self) -> str:
        """Return textual representation."""
        return f"({self.left}, {self.value}[{self.bf}], {self.right})"


# With a mutable search tree, we want to hold a pointer to the
# root at all times, so we wrap it in an object.
class Tree(Generic[Ord]):
    """A binary search tree over Ord."""

    root: Node[Ord]

    def __init__(self) -> None:
        """Create an empty tree."""
        self.root = Empty

    def _set_parent(self, new: Node[Ord], old: Node[Ord]) -> None:
        """
        Update the parent pointer.

        This method handles some special cases such as when the parent is
        None and we need to point the tree's root at new, and it handles
        connecting new to the parent of old by replacing old as a child of
        parent.
        """
        if old.parent is None:
            self.root = new
            new.parent = None
            return

        new.parent = old.parent
        if old.is_left:
            new.parent.left = new
        else:
            new.parent.right = new

    def _rot_left(self, x: InnerNode[Ord]) -> InnerNode[Ord]:
        """Rotate n left."""
        y = x.right
        b = y.left
        assert isinstance(y, InnerNode)

        self._set_parent(y, x)  # connect y with x's parent
        x.right = b
        y.left = x

        return y

    def _rot_right(self, x: InnerNode[Ord]) -> InnerNode[Ord]:
        """Rotate n right."""
        y = x.left
        b = y.right
        assert isinstance(y, InnerNode)

        self._set_parent(y, x)  # connect y with x's parent
        x.left = b
        y.right = x

        return y

    def _balance_node(self, n: InnerNode[Ord]) -> InnerNode[Ord]:
        """Re-organize n to balance it."""
        if n.bf == +2 and n.right.bf >= 0:
            n = self._rot_left(n)
        elif n.bf == +2 and n.right.bf == -1:
            assert isinstance(n.right, InnerNode)
            self._rot_right(n.right)
            n = self._rot_left(n)
        elif n.bf == -2 and n.left.bf <= 0:
            n = self._rot_right(n)
        elif n.bf == -2 and n.left.bf == +1:
            assert isinstance(n.left, InnerNode)
            self._rot_left(n.left)
            n = self._rot_right(n)
        assert -2 < n.bf < +2
        return n

    def _rebalance(self, n: Node[Ord]) -> None:
        """Rebalance tree from n after its height is changed by change."""
        while (p := n.parent):
            p = self._balance_node(p)
            n = p

    def _set_child(self,
                   parent: Optional[InnerNode[Ord]],
                   child: Node[Ord], is_left: bool) -> None:
        """
        Set a child of a node.

        This method wraps several special cases to make updates
        a lot easier.
        """
        if parent is None:
            # Modify the root
            self.root = child
            # Nothing to do after this
            return

        if is_left:
            parent.left = child
        else:
            parent.right = child

        self._rebalance(child)

    def insert(self, val: Ord) -> None:
        """Insert val in tree."""
        t, p = self.root, None
        went_left = True  # arbitrary at first
        while t is not Empty:
            if val == t.value:
                return  # Nothing to insert
            if val < t.value:
                t, p, went_left = t.left, cast(InnerNode[Ord], t), True
            else:
                t, p, went_left = t.right, cast(InnerNode[Ord], t), False

        self._set_child(p, InnerNode(val), went_left)

    def _remove(self, val: Ord,
                t: Node[Ord], p: Optional[InnerNode[Ord]],
                went_left: bool) -> None:
        """
        Insert val in sub-tree t with parent p.

        The extra parameters are needed when removing rightmost in a tree,
        and we don't want them in the general interface.
        """
        while t is not Empty:
            n = cast(InnerNode[Ord], t)

            if val == t.value:
                if n.left is Empty:
                    self._set_child(p, n.right, went_left)
                elif n.right is Empty:
                    self._set_child(p, n.left, went_left)
                else:
                    n.value = rightmost(n.left)
                    self._remove(n.value, n.left, n, True)
                return  # We have removed the value

            if val < n.value:
                t, p, went_left = n.left, n, True
            else:
                t, p, went_left = n.right, n, False

    def remove(self, val: Ord) -> None:
        """Remove val from tree."""
        self._remove(val, self.root, None, True)

    def __contains__(self, val: Ord) -> bool:
        """Test if val is in tree."""
        t = self.root
        while True:
            if t is Empty:
                return False
            if t.value == val:
                return True
            if val < t.value:
                t = t.left
            else:
                t = t.right

    def __bool__(self) -> bool:
        """Test if tree is non-empty."""
        return self.root is not Empty

    def __str__(self) -> str:
        """Print tree."""
        return str(self.root)


def rightmost(t: Node[Ord]) -> Ord:
    """Get the rightmost value in t."""
    assert t is not Empty
    while t.right is not Empty:
        t = t.right
    return t.value
