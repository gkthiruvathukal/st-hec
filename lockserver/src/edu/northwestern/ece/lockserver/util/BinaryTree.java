package edu.northwestern.ece.lockserver.util;

import java.io.Serializable;
import java.io.IOException;
import java.io.BufferedReader;

/** Class for a binary tree that stores Object objects.
 *  @author Koffman and Wolfgang
 * */

public class BinaryTree
    implements Serializable {

  /** Class to encapsulate a tree node. */
  protected static class Node
      implements Serializable {
    // Data Fields
    /** The information stored in this node. */
    protected Object data;
    /** Reference to the left child. */
    protected Node left;
    /** Reference to the right child. */
    protected Node right;

    // Constructors
    /** Construct a node with given data and no children.
        @param data The data to store in this node
     */
    public Node(Object data) {
      this.data = data;
      left = null;
      right = null;
    }

    // Methods
    /** Return a string representation of the node.
        @return A string representation of the data fields
     */
    public String toString() {
      return data.toString();
    }
  }

  // Data Field
  /** The root of the binary tree */
  protected Node root;

  public BinaryTree() {
    root = null;
  }

  protected BinaryTree(Node root) {
    this.root = root;
  }

  /** Constructs a new binary tree with data in its root,
      leftTree as its left subtree and rightTree as its
      right subtree.
   */
  public BinaryTree(Object data, BinaryTree leftTree,
                    BinaryTree rightTree) {
    root = new Node(data);
    if (leftTree != null) {
      root.left = leftTree.root;
    }
    else {
      root.left = null;
    }
    if (rightTree != null) {
      root.right = rightTree.root;
    }
    else {
      root.right = null;
    }
  }

  /** Return the left subtree.
      @return The left subtree or
              null if either the root or the
              left subtree is null
   */
  public BinaryTree getLeftSubtree() {
    if (root != null && root.left != null) {
      return new BinaryTree(root.left);
    }
    else {
      return null;
    }
  }

  /** Return the right sub-tree
        @return the right sub-tree or
        null if either the root or the
        right subtree is null.
   */
  public BinaryTree getRightSubtree() {
    if (root != null && root.right != null) {
      return new BinaryTree(root.right);
    }
    else {
      return null;
    }
  }

  /** Determine whether this tree is a leaf.
      @return true if the root has no children
   */
  boolean isLeaf() {
    return (root.left == null && root.right == null);
  }

  public String toString() {
    StringBuffer sb = new StringBuffer();
    preOrderTraverse(root, 1, sb);
    return sb.toString();
  }

  /** Perform a preorder traversal.
      @param node The local root
      @param depth The depth
      @param sb The string buffer to save the output
   */
  private void preOrderTraverse(Node node, int depth,
                                StringBuffer sb) {
    for (int i = 1; i < depth; i++) {
      sb.append("  ");
    }
    if (node == null) {
      sb.append("null\n");
    }
    else {
      sb.append(node.toString());
      sb.append("\n");
      preOrderTraverse(node.left, depth + 1, sb);
      preOrderTraverse(node.right, depth + 1, sb);
    }
  }

  /** Method to read a binary tree.
      pre: The input consists of a preorder traversal
           of the binary tree. The line "null" indicates a null tree.
      @param bR The input file
      @return The binary tree
      @throws IOException If there is an input error
   */
  public static BinaryTree readBinaryTree(BufferedReader bR) throws IOException {
    // Read a line and trim leading and trailing spaces.
    String data = bR.readLine().trim();
    if (data.equals("null")) {
      return null;
    }
    else {
      BinaryTree left = readBinaryTree(bR);
      BinaryTree right = readBinaryTree(bR);
      return new BinaryTree(data, left, right);
    }
  }

  /** Return the data field of the root
        @return the data field of the root
        or null if the root is null
   */
  public Object getData() {
    if (root != null) {
      return root.data;
    }
    else {
      return null;
    }
  }
}