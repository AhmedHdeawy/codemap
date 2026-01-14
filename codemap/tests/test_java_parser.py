"""Tests for the Java parser."""

import pytest

# Skip all tests if tree-sitter-java is not installed
pytest.importorskip("tree_sitter_java")

from codemap.parsers.java_parser import JavaParser


class TestJavaParser:
    """Tests for JavaParser class."""

    @pytest.fixture
    def parser(self):
        return JavaParser()

    def test_parse_simple_class(self, parser):
        source = '''
public class User {
    private int id;
    private String name;
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "User"
        assert symbols[0].type == "class"

    def test_parse_class_with_methods(self, parser):
        source = '''
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    public int subtract(int a, int b) {
        return a - b;
    }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        calc = symbols[0]
        assert calc.name == "Calculator"
        assert calc.type == "class"
        assert len(calc.children) == 2
        assert calc.children[0].name == "add"
        assert calc.children[0].type == "method"
        assert calc.children[1].name == "subtract"

    def test_parse_interface(self, parser):
        source = '''
public interface UserService {
    User getUser(int id);
    User createUser(String name);
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "UserService"
        assert symbols[0].type == "interface"

    def test_parse_enum(self, parser):
        source = '''
public enum Status {
    ACTIVE,
    INACTIVE,
    PENDING
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "Status"
        assert symbols[0].type == "enum"

    def test_parse_constructor(self, parser):
        source = '''
public class User {
    private String name;

    public User(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        user = symbols[0]
        assert user.name == "User"
        assert len(user.children) == 2
        # Constructor and method
        method_names = [c.name for c in user.children]
        assert "User" in method_names  # Constructor
        assert "getName" in method_names

    def test_parse_multiple_classes(self, parser):
        source = '''
class First {
    void method1() {}
}

class Second {
    void method2() {}
}

class Third {
    void method3() {}
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 3
        names = [s.name for s in symbols]
        assert "First" in names
        assert "Second" in names
        assert "Third" in names

    def test_parse_fixture_file(self, parser):
        """Test parsing the Java fixture file."""
        import os
        fixture_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "SampleModule.java"
        )
        with open(fixture_path, "r") as f:
            source = f.read()

        symbols = parser.parse(source, fixture_path)

        # Should find multiple symbols (classes, interfaces, enums)
        assert len(symbols) >= 3

        names = [s.name for s in symbols]
        assert "User" in names
        assert "UserService" in names or any("UserService" in n for n in names)
        assert "Status" in names
