# Weird trees
A python library for implementing navigable trees where the nodes don't have
an uniform structure

The basic use case is starting from a hierarchy of nodes of different classes
where each class has its children in a mix of attributes/lists and I need a way 
of performing a walk down the tree

## Implementation idea

1. Create a baseclass which will become an ancestor of all classes, this class will  
need:
   + To receive which attributes contain the children
   + To provide a function listing the children
   + Implement iterators, maps and navigate