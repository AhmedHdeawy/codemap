"""Tests for the TreeSitter base parser classes."""

import pytest

from codemap.parsers.treesitter_base import (
    LanguageConfig,
    NodeMapping,
    TREE_SITTER_AVAILABLE,
)


class TestLanguageConfig:
    """Tests for LanguageConfig dataclass."""

    def test_create_config(self):
        config = LanguageConfig(
            name="test",
            extensions=[".test"],
            grammar_module="test",
            node_mappings={
                "function": NodeMapping(
                    symbol_type="function",
                    name_child="identifier",
                )
            },
        )

        assert config.name == "test"
        assert config.extensions == [".test"]
        assert "function" in config.node_mappings

    def test_config_defaults(self):
        config = LanguageConfig(
            name="test",
            extensions=[".test"],
            grammar_module="test",
        )

        assert config.node_mappings == {}
        assert config.export_wrappers == []
        assert config.comment_types == ["comment"]
        assert config.doc_comment_prefix is None


class TestNodeMapping:
    """Tests for NodeMapping dataclass."""

    def test_create_mapping(self):
        mapping = NodeMapping(
            symbol_type="function",
            name_child="identifier",
            signature_child="parameters",
        )

        assert mapping.symbol_type == "function"
        assert mapping.name_child == "identifier"
        assert mapping.signature_child == "parameters"

    def test_mapping_defaults(self):
        mapping = NodeMapping(
            symbol_type="class",
            name_child="name",
        )

        assert mapping.signature_child is None
        assert mapping.body_child is None
        assert mapping.docstring_extractor == "preceding_comment"
        assert mapping.is_async_check is None

    def test_mapping_with_list_name_child(self):
        mapping = NodeMapping(
            symbol_type="function",
            name_child=["identifier", "property_identifier"],
        )

        assert isinstance(mapping.name_child, list)
        assert len(mapping.name_child) == 2

    def test_mapping_with_async_check(self):
        def check_async(node):
            return True

        mapping = NodeMapping(
            symbol_type="function",
            name_child="identifier",
            is_async_check=check_async,
        )

        assert mapping.is_async_check is not None
        assert mapping.is_async_check(None) is True


@pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="tree-sitter not installed")
class TestTreeSitterAvailability:
    """Tests that require tree-sitter to be installed."""

    def test_tree_sitter_available(self):
        assert TREE_SITTER_AVAILABLE is True

    def test_import_base_classes(self):
        from codemap.parsers.treesitter_base import TreeSitterParser
        assert TreeSitterParser is not None
