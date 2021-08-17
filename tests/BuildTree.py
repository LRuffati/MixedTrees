import unittest
from src.MixedTrees import *


class TreeNode(MixedTree):
    """
    Not having provided any child to the class means this will be a leaf
    """
    def __init__(self, val):
        self.id = id(self)
        self.val = val

    def __repr__(self):
        return str(self.val)

    def __eq__(self, other):
        if type(other) is int:
            return self.val == other
        else:
            return id(other) == id(self)


class A(TreeNode, full=["head", "tail"], right=["tail"]):
    """
    This node has two variables holding children.
    "head" holds only one children, "tail" is a list of children

    I can choose to navigate "full" for both or just "left" for the head
    """
    def __init__(self, val, var1, *vars):
        self.id = id(self)
        self.val = val
        self.head = var1
        self.tail = list(vars)


class B(A, right=["preview"]):
    """
    This is inherited from A, so it will already include
    the children for full and left, but will add variable
    "preview" to the children explored in left (but not in full)
    """
    def __init__(self, val, var1, var2, *vars):
        super().__init__(val, var1, *vars)
        self.preview = var2


class BuildTree(unittest.TestCase):
    def setUp(self) -> None:
        self.b1 = B(3,
                        TreeNode(5),
                        TreeNode(7)) # I can leave vars empty
        self.b2 = B(11,
                        TreeNode(13),
                        TreeNode(17),
                        TreeNode(19), TreeNode(23)) # or add multiple elements
        self.tree = A(2,
                      self.b1,
                      self.b2,
                      TreeNode(29))

    def test_children_a(self):
        self.assertListEqual(self.tree.list_mixed_children('full'),
                         [3,11,29])

        self.assertListEqual(self.tree.list_mixed_children('right'),
                         [11,29])

    def test_chidren_b(self):
        self.assertListEqual(self.b1.list_mixed_children('full'),
                         [5])
        self.assertListEqual(self.b2.list_mixed_children('full'),
                             [13,19,23])
        self.assertListEqual(self.b2.list_mixed_children('right'),
                         [19,23,17])

    def test_navigate_full(self):
        """
        It will include the values of every child of A
        but only of head and tail of B
        """
        l = []
        self.tree.navigate(lambda x:l.append(x.val), path='full')
        self.assertListEqual(l,
                             [5,3,13,19,23,11,29,2])
        # explores first the children then the parent

    def test_navigate_right(self):
        l = []
        self.tree.navigate(lambda x:l.append(x.val), path="right")
        self.assertListEqual(l,
                             [19,23,17]+ # first tail, then preview
                             [11]+ # then the value of the node
                             [29]+
                             [2])


if __name__ == '__main__':
    unittest.main()
