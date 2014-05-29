from itertools import izip_longest


class AVLNode(object):
    """A node in an AVL tree."""
    def __init__(self, end=None, time=None):
        self.key = end

        self.left = None
        self.right = None
        self.parent = None

        self.balance = 0

    def __repr__(self):
        return str(self.key)


class AVLTree(object):
    """Self-balancing binary search tree using the AVL algorithm.

    Implementation based on
    http://code.activestate.com/recipes/576817-red-black-tree/.
    """
    def __init__(self, new_node=AVLNode):
        self.new_node = new_node
        self.nil = new_node(None)
        self.root = self.nil

    def __repr__(self):
        return str(list(self.as_tree()))

    def as_tree(self, x=None):
        if x is None:
            x = self.root
        if x is not self.nil:
            yield x
            for l, r in izip_longest(self.as_tree(x.left), self.as_tree(x.right)):
                yield (l, r)

    def descending(self, x=None):
        """Yield nodes in descending order."""
        if x is None:
            x = self.root

        if x is not self.nil:
            if x.right is not self.nil:
                for y in self.descending(x.right):
                    yield y
            yield x
            if x.left is not self.nil:
                for y in self.descending(x.left):
                    yield y

    def ascending(self, x=None):
        """Yield nodes in ascending order."""
        if x is None:
            x = self.root
        l, r = x.left, x.right

        if x is not self.nil:
            if x.left is not self.nil:
                for y in self.ascending(x.left):
                    yield y
            yield x
            if x.right is not self.nil:
                for y in self.ascending(x.right):
                    yield y

    def left_descending(self, x=None):
        """Yield nodes less than the given node."""
        if x is None:
            x = self.root
        if x.left is not self.nil:
            for y in self.descending(x.left):
                yield y

        if x.parent.right is x:
            yield x.parent
            for y in self.left_descending(x.parent):
                yield y

    def right_ascending(self, x=None):
        """Yield nodes greater than the given node."""
        if x is None:
            x = self.root
        if x.right is not self.nil:
            for y in self.ascending(x.right):
                yield y

        if x.parent.left is x:
            yield x.parent
            for y in self.right_ascending(x.parent):
                yield y

    def rotate_left(self, x=None):
        """Left-rotate the tree under node x."""
        if x is None:
            x = self.root
        assert x.right is not self.nil, "Cannot rotate any further left"

        # Right node replaces x as the top node
        y = x.right

        # Move new top node's child under old top node.
        x.right = y.left
        if x.right is not self.nil:
            x.right.parent = x

        # Set new node's parent and fix child relationships.
        y.parent = x.parent
        if y.parent is self.nil:
            self.root = y
        elif x is y.parent.left:
            y.parent.left = y
        else:
            y.parent.right = y

        # Old node moves left of new node.
        y.left = x
        x.parent = y

        # Update the balance.
        x.balance += 1 - min(y.balance, 0)
        y.balance += 1 + max(x.balance, 0)

    def rotate_right(self, x=None):
        """Right-rotate the tree under node x."""
        if x is None:
            x = self.root
        assert x.left is not self.nil, "Cannot rotate any further right"

        # Left node replaces x as the top node
        y = x.left

        # Move new top node's child under old top node.
        x.left = y.right
        if x.left is not self.nil:
            x.left.parent = x

        # Set new node's parent and fix child relationships.
        y.parent = x.parent
        if y.parent is self.nil:
            self.root = y
        elif x is y.parent.left:
            y.parent.left = y
        else:
            y.parent.right = y

        # Old node moves right of new node.
        y.right = x
        x.parent = y

        # Update the balance.
        x.balance -= 1 + max(y.balance, 0)
        y.balance -= 1 - min(x.balance, 0)

    def search(self, key):
        """Find a key in the tree."""
        x = self.root

        while x is not self.nil:
            if key == x.key:
                break

            if key < x.key:
                x = x.left
            else:
                x = x.right
        return x

    def insert_key(self, key):
        self.insert(self.new_node(key))

    def insert(self, node):
        x = self.root
        y = x
        while y is not self.nil:
            x = y
            if node.key < y.key:
                y = y.left
            else:
                y = y.right

        node.parent = x
        node.left = self.nil
        node.right = self.nil

        if x is self.nil:
            self.root = node
        elif node.key < x.key:
            x.left = node
        else:
            x.right = node

        self.update(node, 1)

    def update(self, x, factor=0):
        """Recursively update balance factors going up the tree.
        For a single insertion, factor = 1.
        For a single deletion, factor = -1.
        """
        if x is self.nil:
            return

        if x.balance > 1 or x.balance < -1:
            self.rebalance(x)
            return
        if x is self.root:
            return

        if x is x.parent.left:
            x.parent.balance += factor
        elif x is x.parent.right:
            x.parent.balance -= factor

        if x.parent.balance != 0:
            self.update(x.parent, factor)

    def delete_key(self, key):
        self.delete(self.search(key))

    def delete(self, x):
        if x is self.nil:
            return
        left = x.left is not self.nil
        right = x.right is not self.nil

        if left and right:
            self._swap_right(x)
            self.delete(x)
        elif left:
            self._replace(x, x.left)
        elif right:
            self._replace(x, x.right)
        else:
            self._delete_leaf(x)

    def _delete_leaf(x):
        if x is self.root:
            self.root = self.nil
            return
        if x is x.parent.left:
            x.parent.left = self.nil
            x.parent.balance -= 1
        else:
            x.parent.right = self.nil
            x.parent.balance += 1
        if x.parent.balance == 0:
            self.update(x.parent, -1)

    def _replace(self, x, y):
        """Delete a node and replace it with another."""
        y.parent = x.parent
        if x is self.root:
            self.root = y
            return
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        self.update(y, -1)

    def _swap_right(self, x):
        """Swap node with the smallest node in the right subtree."""
        y = self.minimum(x.right)

        if x is y.parent:
            x.parent, y.parent = y, x.parent
            x.right, y.right = y.right, x
        else:
            x.parent, y.parent = y.parent, x.parent
            x.right, y.right = y.right, x.right
            x.parent.left = x
            y.right.parent = y

        if y.parent is self.nil:
            self.root = y
        elif x is y.parent.left:
            y.parent.left = y
        else:
            y.parent.right = y

        x.left, y.left = y.left, x.left

        x.left.parent = x
        x.right.parent = x
        y.left.parent = y

        x.balance, y.balance = y.balance, x.balance

    def rebalance(self, x=None):
        if x is None:
            x = self.root
        if x is self.nil:
            return

        while x.balance > 1:
            if x.left.balance < 0:
                self.rotate_left(x.left)
            self.rotate_right(x)
        while x.balance < -1:
            if x.right.balance > 0:
                self.rotate_right(x.right)
            self.rotate_left(x)

    def update_all(self):
        if x.left is not self.nil:
            self.update(x.left, True)
        if x.right is not self.nil:
            self.update(x.right, True)
        x.height = 1 + max(x.left.height, x.right.height)
        x.balance = x.left.height - x.right.height

    def maximum(self, x=None):
        if x is None:
            x = self.root
        while x.right is not self.nil:
            x = x.right
        return x

    def minimum(self, x=None):
        if x is None:
            x = self.root
        while x.left is not self.nil:
            x = x.left
        return x

    def add_chunk(self, chunk):
        x, equal = self.find_pivot(chunk.key)
        if equal:
            x.time + chunk.time
