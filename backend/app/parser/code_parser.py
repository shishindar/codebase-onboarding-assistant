
import tree_sitter
import tree_sitter_python


PYTHON_LANGUAGE = tree_sitter.Language(
    tree_sitter_python.language()
)


def extract_imports(root_node):
    """Extract import statements from a Python file."""

    imports = []

    def walk(node):
        if node.type in ("import_statement", "import_from_statement"):
            imports.append(
                node.text.decode("utf-8")
            )

        for child in node.children:
            walk(child)

    walk(root_node)
    return imports


def parse_python_file(file_path):
    """Parse Python code and extract classes, functions and methods."""

    parser = tree_sitter.Parser(PYTHON_LANGUAGE)

    with open(file_path, "rb") as file:
        source = file.read()

    tree = parser.parse(source)
    root_node = tree.root_node

    imports = extract_imports(root_node)
    chunks = []

    def extract_nodes(node, parent_class=None):

        for child in node.children:

            if child.type == "class_definition":

                name_node = child.child_by_field_name("name")
                class_name = name_node.text.decode("utf-8")

                chunks.append({
                    "name": class_name,
                    "type": "class",
                    "parent_class": None,
                    "start_line": child.start_point.row + 1,
                    "end_line": child.end_point.row + 1,
                    "code": child.text.decode("utf-8"),
                    "imports": imports
                })

                extract_nodes(child, class_name)

            elif child.type == "function_definition":

                name_node = child.child_by_field_name("name")
                function_name = name_node.text.decode("utf-8")

                chunks.append({
                    "name": function_name,
                    "type": "method" if parent_class else "function",
                    "parent_class": parent_class,
                    "start_line": child.start_point.row + 1,
                    "end_line": child.end_point.row + 1,
                    "code": child.text.decode("utf-8"),
                    "imports": imports
                })

                extract_nodes(child, parent_class)

            else:
                extract_nodes(child, parent_class)

    extract_nodes(root_node)

    return chunks
