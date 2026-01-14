"""Tests for the Rust parser."""

import pytest

# Skip all tests if tree-sitter-rust is not installed
pytest.importorskip("tree_sitter_rust")

from codemap.parsers.rust_parser import RustParser


class TestRustParser:
    """Tests for RustParser class."""

    @pytest.fixture
    def parser(self):
        return RustParser()

    def test_parse_simple_function(self, parser):
        source = '''
/// Greets a user by name.
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "greet"
        assert symbols[0].type == "function"

    def test_parse_async_function(self, parser):
        source = '''
/// Fetches data asynchronously.
async fn fetch_data(url: &str) -> Result<Vec<u8>, Error> {
    Ok(vec![])
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "fetch_data"
        # Note: async detection may vary by tree-sitter grammar version
        assert symbols[0].type in ("function", "async_function")

    def test_parse_struct(self, parser):
        source = '''
/// Represents a user.
pub struct User {
    pub id: u32,
    pub name: String,
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "User"
        assert symbols[0].type == "struct"

    def test_parse_enum(self, parser):
        source = '''
/// User status.
pub enum Status {
    Active,
    Inactive,
    Pending,
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "Status"
        assert symbols[0].type == "enum"

    def test_parse_trait(self, parser):
        source = '''
/// Service trait for user operations.
pub trait UserService {
    fn get_user(&self, id: u32) -> Option<&User>;
    fn create_user(&mut self, name: String) -> &User;
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "UserService"
        assert symbols[0].type == "trait"

    def test_parse_impl(self, parser):
        source = '''
impl User {
    pub fn new(id: u32, name: String) -> Self {
        User { id, name }
    }

    pub fn display(&self) -> String {
        format!("{}: {}", self.id, self.name)
    }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].type == "impl"

    def test_parse_module(self, parser):
        source = '''
pub mod utils {
    pub fn format_number(n: u32) -> String {
        n.to_string()
    }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "utils"
        assert symbols[0].type == "module"

    def test_parse_multiple_functions(self, parser):
        source = '''
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn subtract(a: i32, b: i32) -> i32 {
    a - b
}

fn multiply(a: i32, b: i32) -> i32 {
    a * b
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 3
        names = [s.name for s in symbols]
        assert "add" in names
        assert "subtract" in names
        assert "multiply" in names

    def test_parse_fixture_file(self, parser):
        """Test parsing the Rust fixture file."""
        import os
        fixture_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "sample_module.rs"
        )
        with open(fixture_path, "r") as f:
            source = f.read()

        symbols = parser.parse(source, fixture_path)

        # Should find multiple symbols
        assert len(symbols) >= 3

        names = [s.name for s in symbols]
        types = [s.type for s in symbols]

        assert "User" in names
        assert "UserService" in names
        assert "greet" in names
        assert "struct" in types
        assert "trait" in types
        assert "function" in types
