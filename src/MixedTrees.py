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
        self.el = self.el.mxdt_map(func, *args,
                                   path=self.path,
                                   mxd_tree_apply=mxd_tree_apply,
                                   **kwargs)
        if mxd_tree_apply:
            self.apply(parent)

    def list(self):
        return [self.el]


class NoneChild(Child):
    def __init__(self, attr):
        self.attr = attr
        self.v = None

    def apply(self, object):
        setattr(object, self.attr, self.v)

    def map(self, parent, func, *args,mxd_tree_apply=True, **kwargs):
        try:
            v = func(None, *args, **kwargs)
            if mxd_tree_apply:
                self.apply(parent)
        except Exception:
            pass # If function doesn't apply to none just leave it as none

    def list(self):
        return []


class LeafChild(Child):
    def __init__(self, attr, el):
        self.attr = attr
        self.v = el

    def apply(self, object):
        setattr(object, self.attr, self.v)

    def map(self, parent, func, *args, mxd_tree_apply=True, **kwargs):
        v = func(self.v, *args, **kwargs)
        if mxd_tree_apply:
            self.apply(parent)

    def list(self):
        return [self.v]


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
        lst = []
        for i in self.lst:
            typ = type(i)
            if issubclass(typ, MixedTree) and typ.has_pat(self.path):
                lst.append(i.mxdt_map(func, *args, path=self.path, mxd_tree_apply=mxd_tree_apply, **kwargs))
            elif i is None:
                try:
                    lst.append(func(None, *args, **kwargs))
                except:
                    lst.append(None)
            else:
                lst.append(func(i, *args, **kwargs))

        self.lst = lst
        if mxd_tree_apply:
            self.apply(parent)

    def list(self):
        return self.lst

class MixedTree:
    _mxdt_children = None

    def __init_subclass__(cls, paths_list=None, **kwargs):
        inherited_attrs = cls._mxdt_children
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
        cls._mxdt_children = inherited_attrs
        super().__init_subclass__(**kwargs)

    def mxdt_list_children(self, path=None, detailed=False):
        if (path is None) and (len(self._mxdt_children) != 1):
            raise MixedTreeException("Specify which path for trees with"
                                     "multiple paths")

        if path is None:
            path = list(self._mxdt_children.keys())[0]

        list_c = self._mxdt_children.get(path, [])
        res = []
        for attr in list_c:
            try:
                el = self.__getattribute__(attr)
            except AttributeError:
                raise MixedTreeException("Instance: ",repr(self), " lacks attribute: ",attr)

            if isinstance(el, MixedTree):
                res.append(AttributeChild(attr, el, path))
            elif isinstance(el, list) or isinstance(el, tuple):
                res.append(ContainerChild(attr, el, path))
            elif el is None:
                res.append(NoneChild(attr))
            else:
                res.append(LeafChild(attr, el))

        if detailed:
            return res
        else:
            return [it for l in [i.list() for i in res] for it in l]

    def mxdt_map(self, fun, *args, path=None, mxd_tree_apply=True, **kwargs):
        """Replaces each subnode with the result of applying the
        function to the child-node (the node is the first positional
        argument of the function and returns the result of the function
        applied to the node itself"""
        childs = self.mxdt_list_children(path, detailed=True)
        i: Child
        for i in childs:
            i.map(self, fun, *args, mxd_tree_apply=mxd_tree_apply, **kwargs)
        return fun(self, *args, **kwargs)

    def mxdt_navigate(self, fun, *args, path=None, **kwargs):
        self.mxdt_map(fun, *args, path=path, mxd_tree_apply=False, **kwargs)

    @classmethod
    def has_pat(cls, path):
        return path in cls._mxdt_children
