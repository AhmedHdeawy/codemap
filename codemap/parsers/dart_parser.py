"""Dart parser using tree-sitter-language-pack for Flutter/Dart projects."""

from __future__ import annotations

from typing import Optional

from .treesitter_base import TreeSitterParser, LanguageConfig, NodeMapping
from .base import Symbol

# Tree-sitter imports - uses language-pack since standalone dart package unavailable
try:
    from tree_sitter import Parser as TSParser
    from tree_sitter_language_pack import get_language
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


DART_CONFIG = LanguageConfig(
    name="dart",
    extensions=[".dart"],
    grammar_module="dart",  # Not used directly - we use language-pack
    node_mappings={
        # Classes
        "class_definition": NodeMapping(
            symbol_type="class",
            name_child="identifier",
            body_child="class_body",
        ),
        # Enums
        "enum_declaration": NodeMapping(
            symbol_type="enum",
            name_child="identifier",
            body_child="enum_body",
        ),
        # Mixins
        "mixin_declaration": NodeMapping(
            symbol_type="mixin",
            name_child="identifier",
            body_child="class_body",
        ),
        # Extensions
        "extension_declaration": NodeMapping(
            symbol_type="extension",
            name_child="identifier",
            body_child="extension_body",
        ),
        # Top-level functions (function_signature node)
        "function_signature": NodeMapping(
            symbol_type="function",
            name_child="identifier",
            signature_child="formal_parameter_list",
        ),
    },
    comment_types=["documentation_comment", "comment"],
    doc_comment_prefix="///",
)


class DartParser(TreeSitterParser):
    """Parser for Dart files using tree-sitter.

    Supports Dart/Flutter features including:
    - Classes (including abstract classes)
    - Enums
    - Mixins
    - Extensions
    - Top-level functions
    - Methods (including getters, setters, factory constructors)
    - Named constructors
    - Documentation comments (///)
    """

    config = DART_CONFIG
    extensions = [".dart"]
    language = "dart"

    def __init__(self):
        """Initialize the Dart parser using tree-sitter-language-pack."""
        if not TREE_SITTER_AVAILABLE:
            raise ImportError(
                "tree-sitter and tree-sitter-language-pack are required. "
                "Install with: pip install tree-sitter tree-sitter-language-pack"
            )
        self._parser = TSParser(get_language("dart"))

    def _extract_symbols(self, node, source_bytes: bytes) -> list[Symbol]:
        """Extract symbols from AST node."""
        symbols = []
        prev_doc = None

        for child in node.children:
            # Track documentation comments
            if child.type == "documentation_comment":
                prev_doc = self._extract_doc_comment(child, source_bytes)
                continue

            symbol = self._extract_symbol(child, source_bytes, prev_doc)
            if symbol:
                symbols.append(symbol)
            prev_doc = None

        return symbols

    def _extract_symbol(
        self, node, source_bytes: bytes, docstring: Optional[str] = None
    ) -> Optional[Symbol]:
        """Extract a symbol from a node with Dart-specific handling."""
        # Handle class definition (including abstract)
        if node.type == "class_definition":
            return self._extract_class(node, source_bytes, docstring)

        # Handle enum
        if node.type == "enum_declaration":
            return self._extract_enum(node, source_bytes, docstring)

        # Handle mixin
        if node.type == "mixin_declaration":
            return self._extract_mixin(node, source_bytes, docstring)

        # Handle extension
        if node.type == "extension_declaration":
            return self._extract_extension(node, source_bytes, docstring)

        # Handle top-level function
        if node.type == "function_signature":
            return self._extract_top_level_function(node, source_bytes, docstring)

        return None

    def _extract_class(
        self, node, source_bytes: bytes, docstring: Optional[str]
    ) -> Symbol:
        """Extract class definition (including abstract classes)."""
        name = self._get_child_text(node, "identifier", source_bytes)
        is_abstract = any(c.type == "abstract" for c in node.children)

        # Extract children from class body
        children = []
        body_node = self._find_child(node, "class_body")
        if body_node:
            children = self._extract_class_members(body_node, source_bytes)

        return Symbol(
            name=name,
            type="class",
            lines=(node.start_point[0] + 1, node.end_point[0] + 1),
            signature=f"{'abstract ' if is_abstract else ''}class {name}",
            docstring=docstring,
            children=children if children else None,
        )

    def _extract_enum(
        self, node, source_bytes: bytes, docstring: Optional[str]
    ) -> Symbol:
        """Extract enum declaration."""
        name = self._get_child_text(node, "identifier", source_bytes)

        return Symbol(
            name=name,
            type="enum",
            lines=(node.start_point[0] + 1, node.end_point[0] + 1),
            signature=f"enum {name}",
            docstring=docstring,
            children=None,
        )

    def _extract_mixin(
        self, node, source_bytes: bytes, docstring: Optional[str]
    ) -> Symbol:
        """Extract mixin declaration."""
        name = self._get_child_text(node, "identifier", source_bytes)

        # Extract children from class body
        children = []
        body_node = self._find_child(node, "class_body")
        if body_node:
            children = self._extract_class_members(body_node, source_bytes)

        return Symbol(
            name=name,
            type="mixin",
            lines=(node.start_point[0] + 1, node.end_point[0] + 1),
            signature=f"mixin {name}",
            docstring=docstring,
            children=children if children else None,
        )

    def _extract_extension(
        self, node, source_bytes: bytes, docstring: Optional[str]
    ) -> Symbol:
        """Extract extension declaration."""
        name = self._get_child_text(node, "identifier", source_bytes) or "<anonymous>"

        # Get the 'on' type
        on_type = None
        found_on = False
        for child in node.children:
            if child.type == "on":
                found_on = True
            elif found_on and child.type == "type_identifier":
                on_type = self._get_node_text(child, source_bytes)
                break

        # Extract children from extension body
        children = []
        body_node = self._find_child(node, "extension_body")
        if body_node:
            children = self._extract_class_members(body_node, source_bytes)

        signature = f"extension {name}"
        if on_type:
            signature += f" on {on_type}"

        return Symbol(
            name=name,
            type="extension",
            lines=(node.start_point[0] + 1, node.end_point[0] + 1),
            signature=signature,
            docstring=docstring,
            children=children if children else None,
        )

    def _extract_top_level_function(
        self, node, source_bytes: bytes, docstring: Optional[str]
    ) -> Symbol:
        """Extract top-level function."""
        name = self._get_child_text(node, "identifier", source_bytes)
        signature = self._get_node_text(node, source_bytes)

        # Find the function_body sibling to get end line
        end_line = node.end_point[0] + 1
        parent = node.parent
        if parent:
            found_sig = False
            for sibling in parent.children:
                if sibling == node:
                    found_sig = True
                elif found_sig and sibling.type == "function_body":
                    end_line = sibling.end_point[0] + 1
                    break

        return Symbol(
            name=name,
            type="function",
            lines=(node.start_point[0] + 1, end_line),
            signature=self._truncate_signature(signature),
            docstring=docstring,
            children=None,
        )

    def _extract_class_members(self, body_node, source_bytes: bytes) -> list[Symbol]:
        """Extract methods and constructors from class/mixin/extension body."""
        members = []
        prev_doc = None
        prev_method_sig = None

        for child in body_node.children:
            if child.type == "documentation_comment":
                prev_doc = self._extract_doc_comment(child, source_bytes)

            elif child.type == "declaration":
                # Check for constructor
                constructor_sig = self._find_child(child, "constructor_signature")
                if constructor_sig:
                    symbol = self._extract_constructor(
                        child, constructor_sig, source_bytes, prev_doc
                    )
                    if symbol:
                        members.append(symbol)
                prev_doc = None

            elif child.type == "method_signature":
                prev_method_sig = child
                # Don't clear prev_doc yet - will be used with function_body

            elif child.type == "function_body" and prev_method_sig:
                symbol = self._extract_method(
                    prev_method_sig, child, source_bytes, prev_doc
                )
                if symbol:
                    members.append(symbol)
                prev_method_sig = None
                prev_doc = None

        return members

    def _extract_method(
        self,
        sig_node,
        body_node,
        source_bytes: bytes,
        docstring: Optional[str],
    ) -> Optional[Symbol]:
        """Extract method from method_signature + function_body."""
        # method_signature can contain: function_signature, getter_signature,
        # setter_signature, factory_constructor_signature
        inner_sig = None
        for child in sig_node.children:
            if child.type in (
                "function_signature",
                "getter_signature",
                "setter_signature",
                "factory_constructor_signature",
            ):
                inner_sig = child
                break

        if not inner_sig:
            return None

        name = self._get_child_text(inner_sig, "identifier", source_bytes)
        signature = self._get_node_text(sig_node, source_bytes)

        # Determine type based on inner signature
        if inner_sig.type == "getter_signature":
            symbol_type = "getter"
        elif inner_sig.type == "setter_signature":
            symbol_type = "setter"
        elif inner_sig.type == "factory_constructor_signature":
            symbol_type = "constructor"
            # For factory constructors, get the full name (ClassName.factoryName)
            identifiers = [c for c in inner_sig.children if c.type == "identifier"]
            if len(identifiers) >= 2:
                class_name = self._get_node_text(identifiers[0], source_bytes)
                factory_name = self._get_node_text(identifiers[1], source_bytes)
                name = f"{class_name}.{factory_name}"
        else:
            symbol_type = "method"

        return Symbol(
            name=name,
            type=symbol_type,
            lines=(sig_node.start_point[0] + 1, body_node.end_point[0] + 1),
            signature=self._truncate_signature(signature),
            docstring=docstring,
            children=None,
        )

    def _extract_constructor(
        self,
        decl_node,
        sig_node,
        source_bytes: bytes,
        docstring: Optional[str],
    ) -> Optional[Symbol]:
        """Extract constructor from declaration with constructor_signature."""
        identifiers = [c for c in sig_node.children if c.type == "identifier"]
        if not identifiers:
            return None

        # Get constructor name (ClassName or ClassName.namedConstructor)
        if len(identifiers) >= 2:
            class_name = self._get_node_text(identifiers[0], source_bytes)
            constructor_name = self._get_node_text(identifiers[1], source_bytes)
            name = f"{class_name}.{constructor_name}"
        else:
            name = self._get_node_text(identifiers[0], source_bytes)

        signature = self._get_node_text(sig_node, source_bytes)

        return Symbol(
            name=name,
            type="constructor",
            lines=(decl_node.start_point[0] + 1, decl_node.end_point[0] + 1),
            signature=self._truncate_signature(signature),
            docstring=docstring,
            children=None,
        )

    def _extract_doc_comment(self, node, source_bytes: bytes) -> Optional[str]:
        """Extract and clean documentation comment."""
        text = self._get_node_text(node, source_bytes)
        # Remove /// prefixes and clean up
        lines = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("///"):
                line = line[3:].strip()
            lines.append(line)

        doc = " ".join(lines).strip()
        if doc:
            return doc[:150]  # Truncate to 150 chars
        return None

    def _get_child_text(self, node, child_type: str, source_bytes: bytes) -> str:
        """Get text of first child of given type."""
        child = self._find_child(node, child_type)
        if child:
            return self._get_node_text(child, source_bytes)
        return ""

    def _truncate_signature(self, sig: str, max_len: int = 100) -> str:
        """Truncate signature to max length."""
        sig = " ".join(sig.split())  # Normalize whitespace
        if len(sig) <= max_len:
            return sig
        return sig[: max_len - 3] + "..."
