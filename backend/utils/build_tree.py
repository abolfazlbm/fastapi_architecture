#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Sequence

from backend.common.enums import BuildTreeType
from backend.utils.serializers import RowData, select_list_serialize


def get_tree_nodes(row: Sequence[RowData], is_sort: bool, sort_key: str) -> list[dict[str, Any]]:
    """
    Get all tree structure nodes

    :param row: original data row sequence
    :param is_sort: Whether to enable result sorting
    :param sort_key: Sort the results based on this key
    :return:
    """
    tree_nodes = select_list_serialize(row)
    if is_sort:
        tree_nodes.sort(key=lambda x: x[sort_key])
    return tree_nodes


def traversal_to_tree(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Constructing a tree structure through a traversal algorithm

    :param nodes: tree node list
    :return:
    """
    tree: list[dict[str, Any]] = []
    node_dict = {node['id']: node for node in nodes}

    for node in nodes:
        parent_id = node['parent_id']
        if parent_id is None:
            tree.append(node)
        else:
            parent_node = node_dict.get(parent_id)
            if parent_node is not None:
                if 'children' not in parent_node:
                    parent_node['children'] = []
                if node not in parent_node['children']:
                    parent_node['children'].append(node)
            else:
                if node not in tree:
                    tree.append(node)

    return tree


def recursive_to_tree(nodes: list[dict[str, Any]], *, parent_id: int | None = None) -> list[dict[str, Any]]:
    """
    Constructing a tree structure through recursive algorithm (performance impact is greater)

    :param nodes: tree node list
    :param parent_id: Parent node ID, default to None to represent the root node
    :return:
    """
    tree: list[dict[str, Any]] = []
    for node in nodes:
        if node['parent_id'] == parent_id:
            child_nodes = recursive_to_tree(nodes, parent_id=node['id'])
            if child_nodes:
                node['children'] = child_nodes
            tree.append(node)
    return tree


def get_tree_data(
    row: Sequence[RowData],
    build_type: BuildTreeType = BuildTreeType.traversal,
    *,
    parent_id: int | None = None,
    is_sort: bool = True,
    sort_key: str = 'sort',
) -> list[dict[str, Any]]:
    """
    Getting tree structure data

    :param row: original data row sequence
    :param build_type: The algorithm type for building a tree structure, default to the traversal algorithm
    :param parent_id: parent node ID, only used in recursive algorithms
    :param is_sort: Whether to enable result sorting
    :param sort_key: Sort the results based on this key
    :return:
    """
    nodes = get_tree_nodes(row, is_sort, sort_key)
    match build_type:
        case BuildTreeType.traversal:
            tree = traversal_to_tree(nodes)
        case BuildTreeType.recursive:
            tree = recursive_to_tree(nodes, parent_id=parent_id)
        case _:
            raise ValueError(f'Invalid algorithm type：{build_type}')
    return tree


def get_vben5_tree_data(row: Sequence[RowData], is_sort: bool = True, sort_key: str = 'sort') -> list[dict[str, Any]]:
    """
    Get vben5 menu tree structure data

    :param row: original data row sequence
    :param is_sort: Whether to enable result sorting
    :param sort_key: Sort the results based on this key
    :return:
    """
    meta_keys = {'title', 'icon', 'link', 'cache', 'display', 'status'}

    vben5_nodes = [
        {
            **{k: v for k, v in node.items() if k not in meta_keys},
            'meta': {
                'title': node['title'],
                'icon': node['icon'],
                'iframeSrc': node['link'] if node['type'] == 3 else '',
                'link': node['link'] if node['type'] == 4 else '',
                'keepAlive': node['cache'],
                'hideInMenu': not bool(node['display']),
                'menuVisibleWithForbidden': not bool(node['status']),
            },
        }
        for node in get_tree_nodes(row, is_sort, sort_key)
    ]

    return traversal_to_tree(vben5_nodes)
