# Weird trees
A python library for implementing navigable trees where the nodes don't have
an uniform structure

The basic use case is starting from a hierarchy of nodes of different classes
where each class has its children in a mix of attributes/lists and I need a way 
of performing a walk down the tree

All nodes of the tree must derive from the base class provided by the library
but they don't have to be of the same type