package edu.northwestern.ece.lockserver.util;

/** Interface to define a search tree
 *  @author Koffman and Wolfgang
 * */

public interface SearchTree {
  /** Inserts item where it belongs in the tree.
      @param item The item to be inserted
      @pre item must implement the Comparable interface
      @return true If the item is inserted, false if the
      item was already in the tree.
      @throws ClassCastException if item does not implement Comparable
   */
  boolean add(Object item);

  /** Determine if an item is in the tree
      @param target Item being sought in tree
      @return true If the item is in the tree, false otherwise
      @throws ClassCastException if target is not Comparable
   */
  boolean contains(Object target);

  /** Find an object in the tree
      @param target The item being sought
      @return A reference to the object in the tree that compares
      equal as determined by compareTo to the target. If not found
      null is returned.
      @throws ClassCastException if target is not Comparable
   */
  Object find(Object target);

  /** Removes target from tree.
      @param target Item to be removed
      @return A reference to the object in the tree that compares
      equal as determined by compareTo to the target. If not found
      null is returned.
      @post target is not in the tree
      @throws ClassCastException if target is not Comparable
   */
  Object delete(Object target);

  /** Removes target from tree.
      @param target Item to be removed
      @return true if the object was in the tree, false otherwise
      @post target is not in the tree
      @throws ClassCastException if target is not Comparable
   */
  boolean remove(Object target);
}
