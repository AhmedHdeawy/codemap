"""Tests for the Go parser."""

import pytest

# Skip all tests if tree-sitter-go is not installed
pytest.importorskip("tree_sitter_go")

from codemap.parsers.go_parser import GoParser


class TestGoParser:
    """Tests for GoParser class."""

    @pytest.fixture
    def parser(self):
        return GoParser()

    def test_parse_simple_function(self, parser):
        source = '''package main

// Greet says hello to someone.
func Greet(name string) string {
    return "Hello, " + name
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "Greet"
        assert symbols[0].type == "function"

    def test_parse_method(self, parser):
        source = '''package main

type Service struct{}

// Process handles data.
func (s *Service) Process(data []byte) error {
    return nil
}
'''
        symbols = parser.parse(source)

        # Should find the struct and method
        assert any(s.name == "Process" and s.type == "method" for s in symbols)

    def test_parse_struct(self, parser):
        source = '''package main

// User represents a user.
type User struct {
    ID   int
    Name string
}
'''
        symbols = parser.parse(source)

        # Should find at least one symbol related to User
        assert len(symbols) >= 1

    def test_parse_interface(self, parser):
        source = '''package main

// Service defines service operations.
type Service interface {
    Process(data []byte) error
    GetStatus() string
}
'''
        symbols = parser.parse(source)

        assert len(symbols) >= 1

    def test_parse_multiple_functions(self, parser):
        source = '''package main

func Add(a, b int) int {
    return a + b
}

func Subtract(a, b int) int {
    return a - b
}

func Multiply(a, b int) int {
    return a * b
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 3
        names = [s.name for s in symbols]
        assert "Add" in names
        assert "Subtract" in names
        assert "Multiply" in names

    def test_parse_fixture_file(self, parser):
        """Test parsing the Go fixture file."""
        import os
        fixture_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "sample_module.go"
        )
        with open(fixture_path, "r") as f:
            source = f.read()

        symbols = parser.parse(source, fixture_path)

        # Should find multiple symbols
        assert len(symbols) > 0

        # Check for expected function
        names = [s.name for s in symbols]
        assert "Greet" in names or any("Greet" in str(s) for s in symbols)
