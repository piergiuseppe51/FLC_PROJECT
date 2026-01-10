import graphviz
from dataclasses import is_dataclass, fields
import os

"""
AST Visualizer Module.
Responsible for rendering the Abstract Syntax Tree using Graphviz.
"""

class ASTVisualizer:
    """
    Wrapper class to generate AST images.
    It uses Python's dataclasses reflection to automatically traverse the tree
    without manual rule updates.
    """

    def __init__(self):
        pass

    def generate(self, root_node, output_file='ast_graph'):
        """
        Generates the AST graph from the root node.
        """
        # Initialize a new graph for every run
        dot = graphviz.Digraph(comment='Abstract Syntax Tree')
        dot.attr(rankdir='TB') # Top-Bottom layout
        dot.attr('node', shape='box', style='filled', fontname='Arial')

        # Create a fake root node for better visualization
        dot.node("ROOT", "PROGRAM", shape='doubleoctagon', fillcolor='orange', style='filled')

        # Start recursion
        if isinstance(root_node, list):
            for stmt in root_node:
                self._visit(dot, stmt, "ROOT")
        else:
            self._visit(dot, root_node, "ROOT")

        # Render
        try:
            output_path = dot.render(output_file, format='png', cleanup=True)
            return output_path
        except Exception as e:
            print(f"Graphviz Render Error: {e}")
            return None

    def _visit(self, dot, node, parent_id=None, label_edge=""):
        """
        Recursive core function.
        Uses dataclasses.fields to inspect nodes dynamically.
        """
        if node is None:
            return

        # Create unique ID
        node_id = str(id(node))

        # Determine style and label based on node type
        if is_dataclass(node):
            node_label = type(node).__name__
            color = 'lightblue' # Structural Nodes
        elif isinstance(node, list):
            node_label = "Block []"
            color = 'lightgrey'
        else:
            # Primitives (int, str, bool)
            node_label = str(node)
            color = 'white'

        # Add node to graph
        dot.node(node_id, node_label, fillcolor=color)

        # Connect to parent
        if parent_id:
            dot.edge(parent_id, node_id, label=label_edge, fontsize='10', fontcolor='gray')

        # ---RECURSION---

        # Dataclasses
        if is_dataclass(node):
            for field in fields(node):
                field_value = getattr(node, field.name)
                
                # Handling lists (es: body, params)
                if isinstance(field_value, list):
                    if field_value: # Only if list is not empty
                        list_id = node_id + "_" + field.name
                        dot.node(list_id, f"{field.name} []", shape='ellipse', fillcolor='lightgrey', style='filled')
                        dot.edge(node_id, list_id)
                        
                        for item in field_value:
                            self._visit(dot, item, list_id)
                
                # Handling single children (es: left, right, expr)
                else:
                    self._visit(dot, field_value, node_id, label_edge=field.name)

        # Lists
        elif isinstance(node, list):
            for item in node:
                self._visit(dot, item, node_id)