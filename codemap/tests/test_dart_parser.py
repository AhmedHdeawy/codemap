"""Tests for the Dart parser."""

import pytest

# Skip all tests if tree-sitter-language-pack is not installed
pytest.importorskip("tree_sitter_language_pack")

from codemap.parsers.dart_parser import DartParser


class TestDartParser:
    """Tests for DartParser class."""

    @pytest.fixture
    def parser(self):
        return DartParser()

    def test_parse_simple_class(self, parser):
        source = '''
class User {
  final int id;
  final String name;
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "User"
        assert symbols[0].type == "class"
        assert symbols[0].signature == "class User"

    def test_parse_abstract_class(self, parser):
        source = '''
abstract class UserService {
  Future<User> getUser(int id);
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "UserService"
        assert symbols[0].type == "class"
        assert "abstract" in symbols[0].signature

    def test_parse_class_with_methods(self, parser):
        source = '''
class Calculator {
  int add(int a, int b) {
    return a + b;
  }

  int subtract(int a, int b) {
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
        assert calc.children[1].type == "method"

    def test_parse_constructor(self, parser):
        source = '''
class Person {
  String name;

  Person(this.name);
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        person = symbols[0]
        assert person.name == "Person"
        assert len(person.children) == 1
        assert person.children[0].name == "Person"
        assert person.children[0].type == "constructor"

    def test_parse_named_constructor(self, parser):
        source = '''
class User {
  int id;
  String name;

  User(this.id, this.name);

  User.fromJson(Map<String, dynamic> json)
      : id = json['id'],
        name = json['name'];
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        user = symbols[0]
        assert len(user.children) == 2

        constructors = [c for c in user.children if c.type == "constructor"]
        assert len(constructors) == 2

        names = [c.name for c in constructors]
        assert "User" in names
        assert "User.fromJson" in names

    def test_parse_factory_constructor(self, parser):
        source = '''
class Singleton {
  static final Singleton _instance = Singleton._internal();

  Singleton._internal();

  factory Singleton() {
    return _instance;
  }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        singleton = symbols[0]

        # Should have named constructor and factory
        constructors = [c for c in singleton.children if c.type == "constructor"]
        assert len(constructors) >= 1

    def test_parse_getter_setter(self, parser):
        source = '''
class Person {
  String _name = '';

  String get name => _name;

  set name(String value) {
    _name = value;
  }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        person = symbols[0]
        assert len(person.children) == 2

        types = {c.type for c in person.children}
        assert "getter" in types
        assert "setter" in types

    def test_parse_enum(self, parser):
        source = '''
enum Status { active, inactive, pending }
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "Status"
        assert symbols[0].type == "enum"
        assert symbols[0].signature == "enum Status"

    def test_parse_mixin(self, parser):
        source = '''
mixin Loggable {
  void log(String message) {
    print(message);
  }
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "Loggable"
        assert symbols[0].type == "mixin"
        assert symbols[0].signature == "mixin Loggable"
        assert len(symbols[0].children) == 1
        assert symbols[0].children[0].name == "log"
        assert symbols[0].children[0].type == "method"

    def test_parse_extension(self, parser):
        source = '''
extension StringUtils on String {
  String toTitleCase() {
    return this[0].toUpperCase() + substring(1);
  }

  bool get isBlank => trim().isEmpty;
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        ext = symbols[0]
        assert ext.name == "StringUtils"
        assert ext.type == "extension"
        assert "on String" in ext.signature
        assert len(ext.children) == 2

    def test_parse_top_level_function(self, parser):
        source = '''
bool validateEmail(String email) {
  return email.contains('@');
}

int add(int a, int b) {
  return a + b;
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 2
        assert symbols[0].name == "validateEmail"
        assert symbols[0].type == "function"
        assert symbols[1].name == "add"
        assert symbols[1].type == "function"

    def test_parse_async_function(self, parser):
        source = '''
Future<String> fetchData() async {
  return 'data';
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].name == "fetchData"
        assert symbols[0].type == "function"

    def test_parse_docstring(self, parser):
        source = '''
/// This is a documented class.
class Documented {
  /// This method does something.
  void doSomething() {}
}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].docstring == "This is a documented class."
        assert len(symbols[0].children) == 1
        assert symbols[0].children[0].docstring == "This method does something."

    def test_parse_multiple_types(self, parser):
        source = '''
class First {}

abstract class Second {}

enum Third { a, b }

mixin Fourth {}

extension Fifth on String {}

void sixth() {}
'''
        symbols = parser.parse(source)

        assert len(symbols) == 6
        names = [s.name for s in symbols]
        assert "First" in names
        assert "Second" in names
        assert "Third" in names
        assert "Fourth" in names
        assert "Fifth" in names
        assert "sixth" in names

    def test_parse_fixture_file(self, parser):
        """Test parsing the Dart fixture file."""
        import os
        fixture_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "sample_module.dart"
        )
        with open(fixture_path, "r") as f:
            source = f.read()

        symbols = parser.parse(source, fixture_path)

        # Should find multiple symbols
        assert len(symbols) >= 6

        names = [s.name for s in symbols]
        assert "User" in names
        assert "UserService" in names
        assert "Status" in names
        assert "Loggable" in names
        assert "StringUtils" in names
        assert "DefaultUserService" in names
        assert "validateEmail" in names

    def test_extensions(self, parser):
        """Test that the parser handles the correct extensions."""
        assert ".dart" in parser.extensions

    def test_language(self, parser):
        """Test that the parser reports the correct language."""
        assert parser.language == "dart"

    def test_line_numbers(self, parser):
        """Test that line numbers are correctly extracted."""
        source = '''class Test {
  void method() {
    print('hello');
  }
}'''
        symbols = parser.parse(source)

        assert len(symbols) == 1
        assert symbols[0].lines[0] == 1  # Start at line 1
        assert symbols[0].lines[1] == 5  # End at line 5 (closing brace)
