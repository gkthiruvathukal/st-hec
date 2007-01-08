package edu.northwestern.ece.lockserver.util;

/** Class to represent Red-Black tree.
 *  @author Koffman and Wolfgang
 * */

public class RedBlackTree
    extends BinarySearchTreeWithRotate {

  /** Nested class to represent a Red-Black node. */
  private static class RedBlackNode
      extends Node {
    // Additional data members
    /** Color indicator. True if red, false if black. */
    private boolean isRed;

    // Constructor
    /** Create a RedBlackNode with the default color of red
        and the given data field.
        @param item The data field
     */
    public RedBlackNode(Object item) {
      super(item);
      isRed = true;
    }

    // Methods
    /** Return a string representation of this object.
        The color (red or black) is appended to the
        node’s contents.
        @return String representation of this object
     */
    public String toString() {
      if (isRed) {
        return "Red  : " + super.toString();
      }
      else {
        return "Black: " + super.toString();
      }
    }
  }

  // Data Field
  /** A boolean variable to indicate that the black height
      was reduced by a call to the recursive delete method
      or one of its submethods.
   */
  private boolean fixupRequired;

  //Methods

  /** Insert an item into the tree. This is the starter method
          of a recursive process.
          @param item - The item to be inserted
          @return true if item inserted, false if item already in the tree.
   */
  public boolean add(Object item) {
    if (root == null) {
      root = new RedBlackNode(item);
      ( (RedBlackNode) root).isRed = false; // root is always black
      return true;
    }
    else {
      root = add( (RedBlackNode) root, (Comparable) item);
      ( (RedBlackNode) root).isRed = false; // root is always black
      return addReturn;
    }
  }

  /** Recursive add method.
      @param localRoot - The root of the subtree
      @param item - The item to be inserted
      @return  updated local root of the subtree
      @post insertReturn is set false if item is already in the tree
   */
  private Node add(RedBlackNode localRoot,
                   Comparable item) {
    if (item.compareTo(localRoot.data) == 0) {
      // item already in the tree
      addReturn = false;
      return localRoot;
    }
    else if (item.compareTo(localRoot.data) < 0) {
      // item < localRoot.data
      if (localRoot.left == null) {
        // create new left child
        localRoot.left = new RedBlackNode(item);
        addReturn = true;
        return localRoot;
      }
      else { // need to search
        // check for two red children swap colors
        moveBlackDown(localRoot);
        // recursively insert on the left
        localRoot.left =
            add( (RedBlackNode) localRoot.left, item);
        // see if the left child is now red
        if ( ( (RedBlackNode) localRoot.left).isRed) {
          if (localRoot.left.left != null
              && ( (RedBlackNode) localRoot.left.left).isRed) {
            // left-left grandchild is also red
            // single rotate is necessary
            ( (RedBlackNode) localRoot.left).isRed = false;
            localRoot.isRed = true;
            return rotateRight(localRoot);
          }
          else if (localRoot.left.right != null
                   && ( (RedBlackNode) localRoot.left.right).isRed) {
            // left-right grandchild is also red
            // double rotate is necessary
            localRoot.left = rotateLeft(localRoot.left);
            ( (RedBlackNode) localRoot.left).isRed = false;
            localRoot.isRed = true;
            return rotateRight(localRoot);
          }
        }
        return localRoot;
      }
    }
    else {
      /**** BEGIN EXERCISE ****/
      // item > localRoot.data
      if (localRoot.right == null) {
        // create new right child
        localRoot.right = new RedBlackNode(item);
        addReturn = true;
        return localRoot;
      }
      else { // need to search
        // check for two red children swap colors
        moveBlackDown(localRoot);
        // recursively insert on the right
        localRoot.right =
            add( (RedBlackNode) localRoot.right, item);
        // see if the right child is now red
        if ( ( (RedBlackNode) localRoot.right).isRed) {
          if (localRoot.right.right != null
              && ( (RedBlackNode) localRoot.right.right).isRed) {
            // right-right grandchild is also red
            // single rotate is necessary
            ( (RedBlackNode) localRoot.right).isRed = false;
            localRoot.isRed = true;
            return rotateLeft(localRoot);
          }
          else if (localRoot.right.left != null
                   && ( (RedBlackNode) localRoot.right.left).isRed) {
            // left-right grandchild is also red
            // double rotate is necessary
            localRoot.right = rotateRight(localRoot.right);
            ( (RedBlackNode) localRoot.right).isRed = false;
            localRoot.isRed = true;
            return rotateLeft(localRoot);
          }
        }
        return localRoot;
      }
      /**** END EXERCISE ****/
    }
  }

  /**** BEGIN EXERCISE ****/
  /** Method to make the two children of the a sub-tree
      balck and the localRoot black.
      @param localRoot The root of the sub-tree
   */
  private void moveBlackDown(RedBlackNode localRoot) {
    // see if both children are red
    if (localRoot.left != null && localRoot.right != null
        && ( (RedBlackNode) localRoot.left).isRed
        && ( (RedBlackNode) localRoot.right).isRed) {
      //make them black and myself red
      ( (RedBlackNode) localRoot.left).isRed = false;
      ( (RedBlackNode) localRoot.right).isRed = false;
      localRoot.isRed = true;
    }
  }

  /** Delete starter method. Removes the given object
      from the binary search tree.  Note that the object
      must implement the Comparable interface.
      Post: The object is not in the tree
      @param item - The object to be removed.
      @return The object from the tree that was removed
      or null if the object was not in the tree.
   */
  public Object delete(Object item) {
    fixupRequired = false;
    if (root == null) {
      return null;
    }
    else {
      int compareReturn =
          ( (Comparable) item).compareTo(root.data);
      if (compareReturn == 0) {
        Object oldValue = root.data;
        root = findReplacement(root);
        if (fixupRequired) {
          root = fixupLeft(root);
        }
        return oldValue;
      }
      else if (compareReturn < 0) {
        if (root.left == null) {
          return null;
        }
        else {
          Object oldValue = removeFromLeft(root, (Comparable) item);
          if (fixupRequired) {
            root = fixupLeft(root);
          }
          return oldValue;
        }
      }
      else {
        if (root.right == null) {
          return null;
        }
        else {
          Object oldValue = removeFromRight(root, (Comparable) item);
          if (fixupRequired) {
            root = fixupRight(root);
          }
          return oldValue;
        }
      }
    }
  }

  /** Recursive remove from left sub-tree method.
      Removes the given object from the binary search tree.
      Note that the object must implement the Comparable interface.
      Pre: The values of parent and parent.left are are not null
      The object is less than parent.data
      @post The object is removed from the tree
      @param parent - Parent of the root of the subtree
      @param item - The object to be removed
      @return The object that was removed or null
      if the item is not in the tree
   */
  private Object removeFromLeft(Node parent, Comparable item) {
    if (item.compareTo(parent.left.data) < 0) {
      if (parent.left.left == null) {
        return null;
      }
      else {
        Object oldValue = removeFromLeft(parent.left, item);
        if (fixupRequired) {
          parent.left = fixupLeft(parent.left);
        }
        return oldValue;
      }
    }
    else if (item.compareTo(parent.left.data) > 0) {
      if (parent.left.right == null) {
        return null;
      }
      else {
        Object oldValue = removeFromRight(parent.left, item);
        if (fixupRequired) {
          parent.left = fixupRight(parent.left);
        }
        return oldValue;
      }
    }
    else {
      Object oldValue = parent.left.data;
      parent.left = findReplacement(parent.left);
      if (fixupRequired) {
        parent.left = fixupLeft(parent.left);
      }
      return oldValue;
    }
  }

  /** Recursive remove from right sub-tree method.
      Removes the given object from the binary search tree.
      Note that the object must implement the Comparable interface.
      @pre The values of parent and parent.right are not null
      The object is greater than parent.data
      @post The object is removed from the tree
      @param parent - Parent of the root of the subtree
      @param item - The object to be removed
      @return The object that was removed or null
      if the item is not in the tree
   */
  private Object removeFromRight(Node parent, Comparable item) {
    if (item.compareTo(parent.right.data) < 0) {
      if (parent.right.left == null) {
        return null;
      }
      else {
        Object oldValue = removeFromLeft(parent.right, item);
        if (fixupRequired) {
          parent.right = fixupLeft(parent.right);
        }
        return oldValue;
      }
    }
    else if (item.compareTo(parent.right.data) > 0) {
      if (parent.right.right == null) {
        return null;
      }
      else {
        Object oldValue = removeFromRight(parent.right, item);
        if (fixupRequired) {
          parent.right = fixupRight(parent.right);
        }
        return oldValue;
      }
    }
    else {
      Object oldValue = parent.right.data;
      parent.right = findReplacement(parent.right);
      if (fixupRequired) {
        parent.right = fixupLeft(parent.right);
      }
      return oldValue;
    }
  }

  /** Function to find a replacement for a node that is being
      deleted from a binary search tree.  If the node has a null
      child, then the replacement is the other child.  If neither
      are null, then the replacement is the largest value less
      than the item being removed.
      @pre  node is not null
      @post a node is deleted from the tree
      @param node The node to be deleted or replaced
      @return null if both of node's children are null
      node.left if node.right is null
      node.right if node.left is null
      modified copy of node with its data field changed
   */
  private Node findReplacement(Node node) {
    if (node.left == null) {
      if ( ( (RedBlackNode) node).isRed) {
        // can always remove a red node
        return node.right;
      }
      else if (node.right == null) {
        // We are removing a black leaf
        fixupRequired = true;
        return null;
      }
      else if ( ( (RedBlackNode) node.right).isRed) {
        // replace black node with red child
        ( (RedBlackNode) node.right).isRed = false;
        return node.right;
      }
      else {
        // a black node cannot have only one black child
        throw new RuntimeException("Invalid Red-Black Tree Structure");
      }
    }
    else if (node.right == null) {
      if ( ( (RedBlackNode) node).isRed) {
        // can always remove a red node
        return node.left;
      }
      else if ( ( (RedBlackNode) node.left).isRed) {
        ( (RedBlackNode) node.left).isRed = false;
        return node.left;
      }
      else {
        // a black node cannot have only one black child
        throw new RuntimeException("Invalid Red-Black Tree structure");
      }
    }
    else {
      if (node.left.right == null) {
        node.data = node.left.data;
        if ( ( (RedBlackNode) node.left).isRed) {
          node.left = node.left.left;
        }
        else if (node.left.left == null) {
          fixupRequired = true;
          node.left = null;
        }
        else if ( ( (RedBlackNode) node.left.left).isRed) {
          ( (RedBlackNode) node.left.left).isRed = false;
          node.left = node.left.left;
        }
        else {
          throw new
              RuntimeException("Invalid Red-Black Tree structure");
        }
        return node;
      }
      else {
        node.data = findLargestChild(node.left);
        if (fixupRequired) {
          node.left = fixupRight(node.left);
        }
        return node;
      }
    }
  }

  /** Find the node such that parent.right.right == null
      @post The found node is removed from the tree and replaced
      by its left child (if any)
      @param parent - The possible parent
      @return the value of the found node
   */
  private Object findLargestChild(Node parent) {
    if (parent.right.right == null) {
      Object returnValue = parent.right.data;
      if ( ( (RedBlackNode) parent.right).isRed) {
        parent.right = parent.right.left;
      }
      else if (parent.right.left == null) {
        fixupRequired = true;
        parent.right = null;
      }
      else if ( ( (RedBlackNode) parent.right.left).isRed) {
        ( (RedBlackNode) parent.right.left).isRed = false;
        parent.right = parent.right.left;
      }
      else {
        throw new RuntimeException("Invalid Red-Black Tree structure");
      }
      return returnValue;
    }
    else {
      Object returnValue = findLargestChild(parent.right);
      if (fixupRequired) {
        parent.right = fixupRight(parent.right);
      }
      return returnValue;
    }
  }

  /** Method to restore black balance to a subtree whose right black
      height is currently one less than the left black height.
      @param localRoot - The root of the tree needing fixing
      @return A new local root
   */
  private Node fixupRight(Node localRoot) {
    // If local root is null, problem needs to be fixed at
    // the next level -- just return
    if (localRoot == null)
      return localRoot;
    if ( ( (RedBlackNode) localRoot).isRed) {
      // If the local root is red, then make it black
      ( (RedBlackNode) localRoot).isRed = false;
      // If the local root has red left-right grand child
      if (localRoot.left.right != null
          && ( (RedBlackNode) localRoot.left.right).isRed) {
        // Rotate left child left
        localRoot.left = rotateLeft(localRoot.left);
        // That grandchild is now the child
        // Rotate the localRoot right
        // Fixup is complete after the next step
        fixupRequired = false;
        return rotateRight(localRoot);
      }
      else if (localRoot.left.left != null
               && ( (RedBlackNode) localRoot.left.left).isRed) {
        // There is a left left grandchild
        // Set it black
        ( (RedBlackNode) localRoot.left.left).isRed = false;
        // Set child red
        ( (RedBlackNode) localRoot.left).isRed = true;
        // Fixup is complete after the next step
        fixupRequired = false;
        return rotateRight(localRoot);
      }
      else { // left child is a leaf or has two black children
        // Set it red
        ( (RedBlackNode) localRoot.left).isRed = true;
        // Fixup is complete
        fixupRequired = false;
        return localRoot;
      }
    }
    else { // localRoot is black
      if ( ( (RedBlackNode) localRoot.left).isRed) {
        // left child is red
        // set the local root red, and the
        // left child black
        ( (RedBlackNode) localRoot).isRed = true;
        ( (RedBlackNode) localRoot.left).isRed = false;
        // Rotate the left child left
        localRoot.left = rotateLeft(localRoot.left);
        Node temp = rotateRight(localRoot);
        // After the next step, the black height of
        // this subtree has been reduced
        // Do not reset fixupRequired
        return rotateRight(temp);
      }
      else {
        // left child is black, set it red
        // do not reset fixupRequired
        ( (RedBlackNode) localRoot.left).isRed = true;
        return localRoot;
      }
    }
  }

  /** Method to restore black balance to a subtree whose left black
      height is currently one less than the right black height.
      @param localRoot - The root of the tree needing fixing
      @return A new local root
   */
  private Node fixupLeft(Node localRoot) {
    // If local root is null, problem needs to be fixed at
    // the next level -- just return
    if (localRoot == null)
      return localRoot;
    if ( ( (RedBlackNode) localRoot).isRed) {
      // If the local root is red, then make it black
      ( (RedBlackNode) localRoot).isRed = false;
      // If the local root has a red right-left grand child
      if (localRoot.right.left != null
          && ( (RedBlackNode) localRoot.right.left).isRed) {
        // Rotate right child right
        localRoot.right = rotateRight(localRoot.right);
        // That grandchild is now the child
        // Rotate the localRoot left
        // Fixup is complete after the next step
        fixupRequired = false;
        return rotateLeft(localRoot);
      }
      else if (localRoot.right.right != null
               && ( (RedBlackNode) localRoot.right.right).isRed) {
        // There is a red right right grandchild
        // Set it black
        ( (RedBlackNode) localRoot.right.right).isRed = false;
        // Set child red
        ( (RedBlackNode) localRoot.right).isRed = true;
        // Fixup is complete after the next step
        fixupRequired = false;
        return rotateLeft(localRoot);
      }
      else { // right child is a leaf or has two black children
        // Set it red
        ( (RedBlackNode) localRoot.right).isRed = true;
        // Fixup is complete
        fixupRequired = false;
        return localRoot;
      }
    }
    else { // localRoot is black
      if ( ( (RedBlackNode) localRoot.right).isRed) {
        // right child is red
        // set the local root red, and the
        // right child black
        ( (RedBlackNode) localRoot).isRed = true;
        ( (RedBlackNode) localRoot.right).isRed = false;
        // Rotate the right child right
        localRoot.right = rotateRight(localRoot.right);
        Node temp = rotateLeft(localRoot);
        // After the next step, the black height of
        // this subtree has been reduced
        // Do not reset fixupRequired
        return rotateLeft(temp);
      }
      else {
        // right child is black, set it red
        // and do not reset fixupRequired
        ( (RedBlackNode) localRoot.right).isRed = true;
        return localRoot;
      }
    }
  }
  /**** END EXERCISE ****/
}