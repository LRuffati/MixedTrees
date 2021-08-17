class MixedTreeException(Exception):
    pass


class Child:
    def list(self):
        """Returns a list of items"""

    def map(self, parent, func, *args,mxd_tree_apply=True, **kwargs):
        pass

    def apply(self, object):
        pass


class AttributeChild(Child):
    def __init__(self, attr, el, path):
        self.attr = attr
        self.el: MixedTree = el
        self.path = path

    def apply(self, object):
        setattr(object, self.attr, self.el)

    def map(self, parent, func, *args,mxd_tree_apply=True, **kwargs):
        self.el = self.el.map(func, *args,
                              path=self.path,
                              mxd_tree_apply=mxd_tree_apply,
                              **kwargs)
        if mxd_tree_apply:
            self.apply(parent)

    def list(self):
        return [self.el]


class ContainerChild(Child):
    def __init__(self, attr, el, path):
        self.type = type(el)
        self.path = path
        self.lst: list[MixedTree] = list(el)
        self.attr = attr

    def apply(self, object):
        new_att = self.type(self.lst)
        setattr(object, self.attr, new_att)

    def map(self, parent, func, *args,mxd_tree_apply=True, **kwargs):
        self.lst = [i.map(func, *args, path=self.path,
                          mxd_tree_apply=mxd_tree_apply, **kwargs) for i in self.lst]
        if mxd_tree_apply:
            self.apply(parent)

    def list(self):
        return self.lst

class MixedTree:
    _mixed_children = None

    def __init_subclass__(cls, paths_list=None, **kwargs):
        inherited_attrs = cls._mixed_children
        if inherited_attrs is None:
            inherited_attrs = {}
        else:
            inherited_attrs = {k:v[:] for k,v in inherited_attrs.items()}

        if paths_list is None:
            paths_list = list(kwargs.keys())

        for p in paths_list:
            prev = inherited_attrs.get(p, [])
            prev.extend(kwargs.pop(p))
            inherited_attrs[p] = prev
        cls._mixed_children = inherited_attrs
        super().__init_subclass__(**kwargs)

    def list_mixed_children(self, path=None, detailed=False):
        if (path is None) and (len(self._mixed_children)!=1):
            raise MixedTreeException("Specify which path for trees with"
                                     "multiple paths")

        if path is None:
            path = list(self._mixed_children.keys())[0]

        list_c = self._mixed_children.get(path, [])
        res = []
        for attr in list_c:
            el = self.__getattribute__(attr)
            if isinstance(el, MixedTree):
                res.append(AttributeChild(attr, el, path))
            elif isinstance(el, list) or isinstance(el, tuple):
                res.append(ContainerChild(attr, el, path))
            else:
                raise MixedTreeException("Attribute ", attr, " of ", repr(self),
                                         " is not a node nor a list or tuple of nodes")

        if detailed:
            return res
        else:
            return [it for l in [i.list() for i in res] for it in l]

    def map(self, fun, *args, path=None, mxd_tree_apply=True, **kwargs):
        """Replaces each subnode with the result of applying the
        function to the child-node (the node is the first positional
        argument of the function and returns the result of the function
        applied to the node itself"""
        childs = self.list_mixed_children(path, detailed=True)
        i: Child
        for i in childs:
            i.map(self, fun, *args, mxd_tree_apply=mxd_tree_apply, **kwargs)
        return fun(self, *args, **kwargs)

    def navigate(self, fun, *args, path=None, **kwargs):
        self.map(fun, *args, path=path, mxd_tree_apply=False, **kwargs)

    @classmethod
    def has_pat(cls, path):
        return path in cls._mixed_children
