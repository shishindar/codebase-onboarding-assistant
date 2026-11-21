
from backend.app.parser.code_parser import parse_python_file


def test_python_ast_parser(tmp_path):

    sample_code = """
import os
from pathlib import Path

class UserService:

    def get_user(self, user_id):
        return user_id

def login(username, password):
    return username
"""

    file_path = tmp_path / "sample.py"
    file_path.write_text(sample_code)

    chunks = parse_python_file(str(file_path))

    assert len(chunks) == 3

    class_chunk = next(
        chunk for chunk in chunks
        if chunk["type"] == "class"
    )

    method_chunk = next(
        chunk for chunk in chunks
        if chunk["type"] == "method"
    )

    function_chunk = next(
        chunk for chunk in chunks
        if chunk["type"] == "function"
    )

    assert class_chunk["name"] == "UserService"
    assert method_chunk["name"] == "get_user"
    assert method_chunk["parent_class"] == "UserService"
    assert function_chunk["name"] == "login"

    assert "import os" in function_chunk["imports"]
    assert class_chunk["start_line"] > 0
    assert class_chunk["end_line"] >= class_chunk["start_line"]
