/******************************************************************
**
** AVLTREE.H:
**
**    ADT AVLTree Implementation
**
** This file is part of Apt Abstract Data Types (ADT)
** Copyright (c) 1991 -- Apt Technologies
** All rights reserved
**
******************************************************************/

#ifndef AVLTREE_H
#define AVLTREE_H

/* ---------- Headers */

#include "apt.h"

/* ---------- Types */

typedef enum _AVLTreeBalanceTypes {
  LEFTHIGH, EQUALHIGH, RIGHTHIGH
} AVLTreeBalanceTypes;

typedef struct _AVLTreeItem {
  enum _AVLTreeBalanceTypes balance;
  int type;
  void *element;
  struct _AVLTreeItem *left;
  struct _AVLTreeItem *right;
} _AVLTreeItem, *AVLTreeItem;

typedef struct _AVLTree {
  int size;
  struct _AVLTreeItem *root;
} _AVLTree, *AVLTree;

/* ---------- Macros */

#ifndef MAX
#define MAX(a,b) (a>b?a:b)
#endif

int AVLTreeDelete(AVLTree, void*, ComparisonFunction, DisposeFunction);
void *AVLTreeDeleteLeftMost(AVLTree);
void *AVLTreeDeleteRightMost(AVLTree);
void AVLTreeDispose(AVLTree, DisposeFunction);
void *AVLTreeFind(AVLTree, void*, ComparisonFunction);
void *AVLTreeFindLeftMost(AVLTree);
void *AVLTreeFindRightMost(AVLTree);
int AVLTreeHeight(AVLTree);
void AVLTreeInorderApply(AVLTree, ApplyFunction);
int AVLTreeInsert(AVLTree, void*, int, ComparisonFunction);
AVLTreeBalanceTypes AVLTreeItemBalance(AVLTreeItem);
void *AVLTreeItemElement(AVLTreeItem);
AVLTreeItem AVLTreeItemLeft(AVLTreeItem);
AVLTreeItem AVLTreeItemRight(AVLTreeItem);
int AVLTreeItemType(AVLTreeItem);
int AVLTreeLeftHeight(AVLTree);
AVLTree AVLTreeNew(void);
void AVLTreePostorderApply(AVLTree, ApplyFunction);
void AVLTreePreorderApply(AVLTree, ApplyFunction);
int AVLTreeRightHeight(AVLTree);
AVLTreeItem AVLTreeRoot(AVLTree);
int AVLTreeSize(AVLTree);

/* Added 03/25/2005 pma */
void AVLTreeInorderApply2(AVLTree tree, ApplyFunctionGeneric f, void* args[]);
void AVLTreePostorderApply2(AVLTree tree, ApplyFunctionGeneric f, void* args[]);
void AVLTreePreorderApply2(AVLTree tree, ApplyFunctionGeneric f, void* args[]);

#endif /* AVLTREE_H */
