# CodeMap: LLM Token-Efficient File Navigation System

## Project Overview

CodeMap is a CLI tool that generates and maintains a structural index of codebases, enabling LLMs to navigate directly to specific code sections instead of reading entire files. This reduces token consumption by 60-80% in typical coding sessions.

## Problem Statement

When LLMs work with code:
1. They read entire files even when they only need a specific function
2. After context compaction, they must re-read files from scratch
3. Large files consume thousands of tokens per read
4. No persistent memory of file structure between reads

## Solution

A lightweight JSON map that provides:
- File hashes (detect changes without re-reading)
- Symbol locations (class/function/method line ranges)
- Hierarchical structure (nested classes, methods)
- Quick navigation metadata

---

## Core Features (MVP)

### 1. Index Generation
```bash
codemap init                    # Index current directory
codemap init ./src              # Index specific directory
codemap init --lang python,typescript  # Filter by language
```

### 2. Single File Reindex
```bash
codemap update path/to/file.py  # Reindex single file
codemap update --all            # Full reindex
```

### 3. Query Interface
```bash
codemap find "PaymentProcessor"           # Find symbol
codemap find "process_payment" --type method
codemap show path/to/file.py              # Show file structure
codemap lines path/to/file.py:45-89       # Validate line range still valid
```

### 4. Validation
```bash
codemap validate                # Check all hashes, report stale entries
codemap validate path/to/file.py
```

### 5. Git Integration
```bash
codemap install-hooks           # Install pre-commit hook
```

---

## Architecture

```
codemap/
├── cli.py                 # Click-based CLI entry point
├── core/
│   ├── __init__.py
│   ├── indexer.py         # Main indexing orchestrator
│   ├── hasher.py          # File hashing utilities
│   └── map_store.py       # JSON map read/write operations
├── parsers/
│   ├── __init__.py
│   ├── base.py            # Abstract parser interface
│   ├── python_parser.py   # Python AST-based parser
│   ├── typescript_parser.py  # TypeScript parser (tree-sitter)
│   └── javascript_parser.py  # JavaScript parser (tree-sitter)
├── hooks/
│   ├── pre-commit         # Git pre-commit hook script
│   └── installer.py       # Hook installation logic
├── utils/
│   ├── __init__.py
│   ├── file_utils.py      # File discovery, filtering
│   └── config.py          # Configuration management
└── tests/
    ├── test_indexer.py
    ├── test_parsers.py
    └── fixtures/          # Sample code files for testing
```

---

## Data Model

### .codemap.json Structure

```json
{
  "version": "1.0",
  "generated_at": "2025-01-11T10:30:00Z",
  "root": "/absolute/path/to/project",
  "config": {
    "languages": ["python", "typescript", "javascript"],
    "exclude_patterns": ["**/node_modules/**", "**/__pycache__/**", "**/dist/**"],
    "include_patterns": ["src/**", "lib/**"]
  },
  "files": {
    "src/payments/processor.py": {
      "hash": "a3f2b8c1d4e5",
      "indexed_at": "2025-01-11T10:30:00Z",
      "language": "python",
      "lines": 542,
      "symbols": [
        {
          "name": "PaymentProcessor",
          "type": "class",
          "lines": [15, 189],
          "docstring": "Handles payment processing for all payment methods",
          "children": [
            {
              "name": "__init__",
              "type": "method",
              "lines": [20, 35],
              "signature": "(self, gateway: Gateway, config: Config)"
            },
            {
              "name": "process_payment",
              "type": "method",
              "lines": [37, 98],
              "signature": "(self, amount: Decimal, card: Card) -> TransactionResult",
              "docstring": "Process a payment transaction"
            },
            {
              "name": "validate_card",
              "type": "method",
              "lines": [100, 145],
              "signature": "(self, card: Card) -> ValidationResult"
            }
          ]
        },
        {
          "name": "RefundHandler",
          "type": "class",
          "lines": [191, 320],
          "children": [...]
        },
        {
          "name": "calculate_fee",
          "type": "function",
          "lines": [322, 340],
          "signature": "(amount: Decimal, fee_type: str) -> Decimal"
        }
      ]
    }
  },
  "stats": {
    "total_files": 47,
    "total_symbols": 382,
    "last_full_index": "2025-01-11T10:30:00Z"
  }
}
```

---

## Implementation Details

### Python Parser (AST-based)

```python
# parsers/python_parser.py
import ast
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Symbol:
    name: str
    type: str  # class, function, method, async_function, async_method
    lines: tuple[int, int]
    signature: Optional[str] = None
    docstring: Optional[str] = None
    children: List['Symbol'] = None
    
    def to_dict(self):
        result = {
            "name": self.name,
            "type": self.type,
            "lines": list(self.lines)
        }
        if self.signature:
            result["signature"] = self.signature
        if self.docstring:
            result["docstring"] = self.docstring[:150]  # Truncate long docstrings
        if self.children:
            result["children"] = [c.to_dict() for c in self.children]
        return result

class PythonParser:
    def parse(self, source: str) -> List[Symbol]:
        tree = ast.parse(source)
        return self._extract_symbols(tree.body, is_top_level=True)
    
    def _extract_symbols(self, nodes, is_top_level=False) -> List[Symbol]:
        symbols = []
        for node in nodes:
            if isinstance(node, ast.ClassDef):
                symbols.append(self._parse_class(node))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbol_type = "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"
                symbols.append(self._parse_function(node, symbol_type))
        return symbols
    
    def _parse_class(self, node: ast.ClassDef) -> Symbol:
        children = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_type = "async_method" if isinstance(item, ast.AsyncFunctionDef) else "method"
                children.append(self._parse_function(item, method_type))
        
        return Symbol(
            name=node.name,
            type="class",
            lines=(node.lineno, node.end_lineno),
            docstring=ast.get_docstring(node),
            children=children if children else None
        )
    
    def _parse_function(self, node, symbol_type: str) -> Symbol:
        return Symbol(
            name=node.name,
            type=symbol_type,
            lines=(node.lineno, node.end_lineno),
            signature=self._get_signature(node),
            docstring=ast.get_docstring(node)
        )
    
    def _get_signature(self, node) -> str:
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        sig = f"({', '.join(args)})"
        if node.returns:
            sig += f" -> {ast.unparse(node.returns)}"
        return sig
```

### TypeScript/JavaScript Parser (tree-sitter)

```python
# parsers/typescript_parser.py
# Use tree-sitter-javascript and tree-sitter-typescript
# pip install tree-sitter tree-sitter-javascript tree-sitter-typescript

import tree_sitter_javascript as tsjs
import tree_sitter_typescript as tsts
from tree_sitter import Language, Parser

class TypeScriptParser:
    def __init__(self):
        self.parser = Parser(Language(tsts.language_typescript()))
    
    def parse(self, source: str) -> List[Symbol]:
        tree = self.parser.parse(bytes(source, 'utf8'))
        return self._extract_symbols(tree.root_node, source)
    
    def _extract_symbols(self, node, source) -> List[Symbol]:
        symbols = []
        
        # Navigate tree-sitter AST
        # Look for: function_declaration, class_declaration, 
        # method_definition, arrow_function (named)
        
        for child in node.children:
            if child.type == 'class_declaration':
                symbols.append(self._parse_class(child, source))
            elif child.type in ('function_declaration', 'export_statement'):
                # Handle exported functions
                symbols.extend(self._parse_function_or_export(child, source))
        
        return symbols
```

### Hasher Utility

```python
# core/hasher.py
import hashlib

def hash_file(filepath: str) -> str:
    """Generate a short hash of file contents."""
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]

def hash_content(content: bytes) -> str:
    """Hash raw content."""
    return hashlib.sha256(content).hexdigest()[:12]
```

### CLI Interface

```python
# cli.py
import click
from pathlib import Path

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """CodeMap - LLM-friendly codebase indexer"""
    pass

@cli.command()
@click.argument('path', default='.', type=click.Path(exists=True))
@click.option('--lang', '-l', multiple=True, help='Languages to index')
@click.option('--exclude', '-e', multiple=True, help='Patterns to exclude')
def init(path, lang, exclude):
    """Initialize codemap for a directory."""
    from core.indexer import Indexer
    
    indexer = Indexer(
        root=Path(path),
        languages=lang or ['python', 'typescript', 'javascript'],
        exclude_patterns=list(exclude)
    )
    result = indexer.index_all()
    click.echo(f"Indexed {result['total_files']} files, {result['total_symbols']} symbols")
    click.echo(f"Map saved to {path}/.codemap.json")

@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
def update(filepath):
    """Update index for a single file."""
    from core.indexer import Indexer
    indexer = Indexer.load_existing()
    indexer.update_file(filepath)
    click.echo(f"Updated {filepath}")

@cli.command()
@click.argument('query')
@click.option('--type', '-t', 'symbol_type', help='Filter by type (class, function, method)')
def find(query, symbol_type):
    """Find a symbol in the codebase."""
    from core.map_store import MapStore
    
    store = MapStore.load()
    results = store.find_symbol(query, symbol_type=symbol_type)
    
    for result in results:
        click.echo(f"{result['file']}:{result['lines'][0]}-{result['lines'][1]} "
                   f"[{result['type']}] {result['name']}")

@cli.command()
@click.argument('filepath')
def show(filepath):
    """Show structure of a file."""
    from core.map_store import MapStore
    
    store = MapStore.load()
    structure = store.get_file_structure(filepath)
    
    if not structure:
        click.echo(f"File not indexed: {filepath}")
        return
    
    click.echo(f"File: {filepath} (hash: {structure['hash']})")
    click.echo(f"Lines: {structure['lines']}")
    click.echo("Symbols:")
    _print_symbols(structure['symbols'], indent=2)

def _print_symbols(symbols, indent=0):
    for sym in symbols:
        prefix = " " * indent
        click.echo(f"{prefix}- {sym['name']} [{sym['type']}] L{sym['lines'][0]}-{sym['lines'][1]}")
        if sym.get('children'):
            _print_symbols(sym['children'], indent + 2)

@cli.command()
def validate():
    """Validate all file hashes, report stale entries."""
    from core.indexer import Indexer
    
    indexer = Indexer.load_existing()
    stale = indexer.validate_all()
    
    if stale:
        click.echo(f"Stale entries ({len(stale)}):")
        for filepath in stale:
            click.echo(f"  - {filepath}")
        click.echo("\nRun 'codemap update --all' to refresh")
    else:
        click.echo("All entries up to date ✓")

@cli.command('install-hooks')
def install_hooks():
    """Install git pre-commit hook."""
    from hooks.installer import install_pre_commit
    install_pre_commit()
    click.echo("Git hooks installed ✓")

if __name__ == '__main__':
    cli()
```

---

## Git Hook

```bash
#!/bin/bash
# hooks/pre-commit

# Get list of staged Python/TS/JS files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|ts|js|tsx|jsx)$')

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

# Check if codemap is initialized
if [ ! -f ".codemap.json" ]; then
    exit 0
fi

# Update index for each staged file
for FILE in $STAGED_FILES; do
    if [ -f "$FILE" ]; then
        codemap update "$FILE"
    fi
done

# Stage the updated map
git add .codemap.json

exit 0
```

---

## Configuration File (.codemaprc)

Optional YAML config for project-specific settings:

```yaml
# .codemaprc
languages:
  - python
  - typescript
  - javascript

exclude:
  - "**/node_modules/**"
  - "**/__pycache__/**"
  - "**/dist/**"
  - "**/build/**"
  - "**/.venv/**"
  - "**/venv/**"
  - "**/*.min.js"
  - "**/migrations/**"

include:
  - "src/**"
  - "lib/**"
  - "app/**"

# Truncate docstrings longer than this
max_docstring_length: 150

# Include these additional file patterns
additional_extensions:
  python: [".pyi"]
  
# Output location (default: .codemap.json)
output: .codemap.json
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_python_parser.py
import pytest
from parsers.python_parser import PythonParser

def test_parse_simple_function():
    source = '''
def hello(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}"
'''
    parser = PythonParser()
    symbols = parser.parse(source)
    
    assert len(symbols) == 1
    assert symbols[0].name == "hello"
    assert symbols[0].type == "function"
    assert symbols[0].lines == (2, 4)
    assert "name: str" in symbols[0].signature

def test_parse_class_with_methods():
    source = '''
class Calculator:
    """A simple calculator."""
    
    def add(self, a: int, b: int) -> int:
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        return a - b
'''
    parser = PythonParser()
    symbols = parser.parse(source)
    
    assert len(symbols) == 1
    assert symbols[0].name == "Calculator"
    assert symbols[0].type == "class"
    assert len(symbols[0].children) == 2
```

### Integration Tests

```python
# tests/test_indexer.py
def test_full_index_workflow(tmp_path):
    # Create sample files
    (tmp_path / "service.py").write_text('''
class UserService:
    def get_user(self, id: int):
        pass
''')
    
    indexer = Indexer(root=tmp_path)
    result = indexer.index_all()
    
    assert result['total_files'] == 1
    assert result['total_symbols'] == 1
    
    # Verify map file created
    map_path = tmp_path / ".codemap.json"
    assert map_path.exists()
```

---

## Dependencies

```toml
# pyproject.toml
[project]
name = "codemap"
version = "1.0.0"
description = "LLM-friendly codebase indexer"
requires-python = ">=3.10"
dependencies = [
    "click>=8.0",
    "tree-sitter>=0.21",
    "tree-sitter-javascript>=0.21",
    "tree-sitter-typescript>=0.21",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "black",
    "ruff",
]

[project.scripts]
codemap = "codemap.cli:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## Success Criteria

1. **Accuracy**: Symbols must have correct line numbers (validated against source)
2. **Performance**: Index 1000 files in <10 seconds
3. **Correctness**: Hash changes detected on any file modification
4. **Usability**: CLI is intuitive, output is LLM-friendly
5. **Reliability**: Graceful handling of parse errors (skip file, log warning)

---

## Future Enhancements (Post-MVP)

1. **Watch mode**: `codemap watch` - continuous file watching
2. **IDE extensions**: VSCode extension for real-time updates
3. **Language Server Protocol**: Integrate with LSP for richer metadata
4. **Semantic search**: Embed symbols for fuzzy matching
5. **Multi-repo support**: Index across multiple repositories
6. **Remote caching**: Share indexes across team members
