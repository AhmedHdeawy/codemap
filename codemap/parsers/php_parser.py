"""PHP parser using tree-sitter with configuration-driven extraction."""

from __future__ import annotations

from .treesitter_base import TreeSitterParser, LanguageConfig, NodeMapping


PHP_CONFIG = LanguageConfig(
    name="php",
    extensions=[".php", ".phtml"],
    grammar_module="php",
    node_mappings={
        # Classes
        "class_declaration": NodeMapping(
            symbol_type="class",
            name_child="name",
            body_child="declaration_list",
        ),
        # Interfaces
        "interface_declaration": NodeMapping(
            symbol_type="interface",
            name_child="name",
            body_child="declaration_list",
        ),
        # Traits
        "trait_declaration": NodeMapping(
            symbol_type="trait",
            name_child="name",
            body_child="declaration_list",
        ),
        # Enums (PHP 8.1+)
        "enum_declaration": NodeMapping(
            symbol_type="enum",
            name_child="name",
            body_child="enum_declaration_list",
        ),
        # Functions
        "function_definition": NodeMapping(
            symbol_type="function",
            name_child="name",
            signature_child="formal_parameters",
        ),
        # Methods
        "method_declaration": NodeMapping(
            symbol_type="method",
            name_child="name",
            signature_child="formal_parameters",
        ),
        # Enum cases (PHP 8.1+)
        "enum_case": NodeMapping(
            symbol_type="constant",
            name_child="name",
        ),
    },
    comment_types=["comment"],
    doc_comment_prefix="/**",  # PHPDoc style
)


class PHPParser(TreeSitterParser):
    """Parser for PHP files using tree-sitter.

    Supports PHP 8+ features including:
    - Classes, interfaces, and traits
    - Enums (PHP 8.1+)
    - Attributes (PHP 8.0+)
    - Arrow functions
    - PHPDoc comments
    """

    config = PHP_CONFIG
    extensions = [".php", ".phtml"]
    language = "php"

    def __init__(self):
        """Initialize the PHP parser with the php_only grammar."""
        from .base import Parser

        try:
            from tree_sitter import Language, Parser as TSParser
        except ImportError:
            raise ImportError(
                "tree-sitter and tree-sitter-php are required. "
                "Install with: pip install tree-sitter tree-sitter-php"
            )

        try:
            # Use php_only grammar for pure PHP files (no HTML interpolation)
            from tree_sitter_php import language_php
            self._parser = TSParser(Language(language_php()))
        except ImportError:
            raise ImportError(
                "tree-sitter-php is required. "
                "Install with: pip install tree-sitter-php"
            )
