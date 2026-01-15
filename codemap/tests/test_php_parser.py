"""Tests for the PHP parser."""

import os

import pytest

# Skip all tests if tree-sitter-php is not installed
pytest.importorskip("tree_sitter_php")

from codemap.parsers.php_parser import PHPParser


class TestPHPParser:
    """Tests for PHPParser class."""

    @pytest.fixture
    def parser(self):
        return PHPParser()

    def test_parse_simple_function(self, parser):
        source = '''<?php
/** Greets a user by name. */
function greet(string $name): string {
    return "Hello, " . $name;
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "greet"
        assert symbols[0].type == "function"

    def test_parse_class_with_methods(self, parser):
        source = '''<?php
/**
 * User class representing a system user.
 */
class User {
    /** Get the user ID. */
    public function getId(): int {
        return $this->id;
    }

    /** Set the user name. */
    public function setName(string $name): void {
        $this->name = $name;
    }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "User"
        assert symbols[0].type == "class"
        assert len(symbols[0].children) == 2
        assert symbols[0].children[0].name == "getId"
        assert symbols[0].children[0].type == "method"
        assert symbols[0].children[1].name == "setName"
        assert symbols[0].children[1].type == "method"

    def test_parse_interface(self, parser):
        source = '''<?php
/** Repository interface for data persistence. */
interface RepositoryInterface {
    /** Find an entity by ID. */
    public function find(int $id): ?object;

    /** Save an entity. */
    public function save(object $entity): void;
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "RepositoryInterface"
        assert symbols[0].type == "interface"
        assert len(symbols[0].children) == 2

    def test_parse_trait(self, parser):
        source = '''<?php
/** Trait providing timestamp functionality. */
trait Timestampable {
    /** Get the creation date. */
    public function getCreatedAt(): ?DateTime {
        return $this->createdAt;
    }

    /** Update the timestamp. */
    public function touch(): void {
        $this->updatedAt = new DateTime();
    }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "Timestampable"
        assert symbols[0].type == "trait"
        assert len(symbols[0].children) == 2

    def test_parse_enum(self, parser):
        source = '''<?php
/** User status enumeration. */
enum UserStatus: string {
    case Active = 'active';
    case Inactive = 'inactive';
    case Pending = 'pending';
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "UserStatus"
        assert symbols[0].type == "enum"

    def test_parse_enum_without_backing_type(self, parser):
        source = '''<?php
/** Color enumeration. */
enum Color {
    case Red;
    case Green;
    case Blue;
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "Color"
        assert symbols[0].type == "enum"

    def test_parse_multiple_functions(self, parser):
        source = '''<?php
function add(int $a, int $b): int {
    return $a + $b;
}

function subtract(int $a, int $b): int {
    return $a - $b;
}

function multiply(int $a, int $b): int {
    return $a * $b;
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 3
        names = [s.name for s in symbols]
        assert "add" in names
        assert "subtract" in names
        assert "multiply" in names

    def test_parse_abstract_class(self, parser):
        source = '''<?php
/** Abstract base class for services. */
abstract class AbstractService {
    /** Initialize the service. */
    abstract public function initialize(): void;

    /** Get the service name. */
    public function getServiceName(): string {
        return static::class;
    }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "AbstractService"
        assert symbols[0].type == "class"
        assert len(symbols[0].children) == 2

    def test_parse_class_with_constructor(self, parser):
        source = '''<?php
class User {
    public function __construct(
        private readonly int $id,
        private string $name,
    ) {}

    public function getId(): int {
        return $this->id;
    }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "User"
        assert len(symbols[0].children) == 2
        assert symbols[0].children[0].name == "__construct"

    def test_parse_class_with_attributes(self, parser):
        source = '''<?php
#[Entity(table: 'users')]
#[Table(name: 'users')]
class User {
    #[Column(type: 'integer')]
    private int $id;

    #[RequiresAuth]
    public function delete(): void {}
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "User"
        assert symbols[0].type == "class"

    def test_parse_static_method(self, parser):
        source = '''<?php
class Factory {
    public static function create(): self {
        return new self();
    }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].children[0].name == "create"
        assert symbols[0].children[0].type == "method"

    def test_parse_fixture_file(self, parser):
        """Test parsing the PHP fixture file."""
        fixture_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "sample_module.php"
        )
        with open(fixture_path, "r") as f:
            source = f.read()
        symbols = parser.parse(source, fixture_path)

        # Should find multiple top-level symbols
        assert len(symbols) >= 5

        # Check for expected symbol types
        names = [s.name for s in symbols]
        types = [s.type for s in symbols]

        assert "UserStatus" in names  # enum
        assert "Color" in names  # enum
        assert "RepositoryInterface" in names  # interface
        assert "Timestampable" in names  # trait
        assert "User" in names  # class
        assert "AbstractService" in names  # abstract class
        assert "UserService" in names  # class
        assert "greet" in names  # function

        assert "enum" in types
        assert "interface" in types
        assert "trait" in types
        assert "class" in types
        assert "function" in types

    def test_docstring_extraction(self, parser):
        source = '''<?php
/**
 * Calculate the sum of all numbers.
 * @param int ...$numbers The numbers to sum.
 * @return int The total sum.
 */
function sum(int ...$numbers): int {
    return array_sum($numbers);
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].docstring is not None
        assert "sum" in symbols[0].docstring.lower() or "Calculate" in symbols[0].docstring

    def test_parser_extensions(self, parser):
        """Test that parser handles correct extensions."""
        assert ".php" in parser.extensions
        assert ".phtml" in parser.extensions

    def test_parser_language(self, parser):
        """Test parser language property."""
        assert parser.language == "php"
