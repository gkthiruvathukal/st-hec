package edu.northwestern.ece.lockserver.util;

/**
    This class extends the BinarySearchTree by adding the rotate
    operations. Rotation will change the balance of a search
    tree while preserving the search tree property.
    Used as a common base class for self-balancing trees.
    @author Koffman and Wolfgang
 */

public class BinarySearchTreeWithRotate
    extends BinarySearchTree {
  // Methods
  /** Method to perform a right rotation.
      pre:  root is the root of a binary search tree.
      post: root.right is the root of a binary search tree,
            root.right.right is raised one level,
            root.right.left does not change levels,
            root.left is lowered one level,
            the new root is returned.
      @param root The root of the binary tree to be rotated
      @return The new root of the rotated tree
   */
  protected Node rotateRight(Node root) {
    Node temp = root.left;
    root.left = temp.right;
    temp.right = root;
    return temp;
  }

  /** rotateLeft
      pre:  localRoot is the root of a binary search tree
      post: localRoot.right is the root of a binary search tree
            localRoot.right.right is raised one level
            localRoot.right.left does not change levels
            localRoot.left is lowered one level
            the new localRoot is returned.
     @param localRoot The root of the binary tree to be rotated
     @return the new root of the rotated tree
   */
  protected Node rotateLeft(Node localRoot) {
    /**** BEGIN EXERCISE ****/
    Node temp = localRoot.right;
    localRoot.right = temp.left;
    temp.left = localRoot;
    return temp;
    /**** END EXERCISE ****/
  }

}
