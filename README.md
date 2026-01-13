# CodeMap

LLM-friendly codebase indexer that reduces token consumption by 60-80% by enabling targeted line-range reads instead of full file reads.

## Problem

When LLMs work with code:
- They read entire files even when they only need a specific function
- After context compaction, they must re-read files from scratch
- Large files consume thousands of tokens per read
- No persistent memory of file structure between reads

## Solution

CodeMap creates a lightweight `.codemap/` directory that provides:
- File hashes (detect changes without re-reading)
- Symbol locations (class/function/method line ranges)
- Hierarchical structure (nested classes, methods)
- Quick navigation metadata
- **Distributed per-directory indexes** for scalable large codebases

## Installation

```bash
# Basic installation (Python parsing only)
pip install -e .

# With TypeScript/JavaScript support
pip install -e ".[treesitter]"

# With watch mode
pip install -e ".[watch]"

# Everything
pip install -e ".[all]"
```

## Quick Start

```bash
# Index a directory
codemap init ./src

# Find a symbol
codemap find "ClassName"

# Show file structure
codemap show path/to/file.py

# Validate freshness
codemap validate

# Update single file
codemap update path/to/file.py

# Watch for changes (live updates)
codemap watch

# Show statistics
codemap stats
```

## Commands

### `codemap init [PATH]`

Initialize codemap for a directory. Scans all supported files and creates `.codemap/` folder mirroring your project structure.

```bash
codemap init                     # Index current directory
codemap init ./src               # Index specific directory
codemap init -l python           # Only index Python files
codemap init -e "**/tests/**"    # Exclude test directories
```

### `codemap find QUERY`

Find symbols matching a query (case-insensitive substring match).

```bash
codemap find "UserService"              # Find by name
codemap find "process" --type method    # Filter by type
codemap find "handle" --type function   # Find functions only
```

Output:
```
src/services/user.py:15-89 [class] UserService
src/services/user.py:20-45 [method] process_request
```

### `codemap show FILE`

Display the structure of a file with all symbols, line ranges, and signatures.

```bash
codemap show src/services/user.py
```

Output:
```
File: src/services/user.py (hash: a3f2b8c1d4e5)
Lines: 542
Language: python

Symbols:
- UserService [class] L15-189
  (self, config: Config)
  # Handles user operations
  - __init__ [method] L20-35
  - get_user [method] L37-98
    (self, user_id: int) -> User
  - create_user [async_method] L100-145
    (self, data: dict) -> User
```

### `codemap validate [FILE]`

Check if indexed files have changed since last index.

```bash
codemap validate              # Check all files
codemap validate src/main.py  # Check specific file
```

### `codemap update [FILE] [--all]`

Update the index for changed files.

```bash
codemap update src/main.py    # Update single file
codemap update --all          # Update all stale files
```

### `codemap watch [PATH]`

Watch directory for changes and update index automatically in real-time.

```bash
codemap watch                 # Watch current directory
codemap watch ./src           # Watch specific directory
codemap watch -d 1.0          # Use 1 second debounce
codemap watch -q              # Quiet mode (errors only)
```

Output:
```
Watching /path/to/project for changes...
Debounce: 0.5s
Press Ctrl+C to stop

[14:30:15] Updated main.py (2 symbols changed)
[14:30:22] Updated utils.py
[14:31:05] Updated new_module.py (3 symbols changed)
```

### `codemap stats`

Show statistics about the current codemap.

```bash
codemap stats
```

Output:
```
CodeMap Statistics
========================================
Root: /path/to/project
Version: 1.0
Generated: 2025-01-12T10:30:00Z
Indexed directories: 5

Total files: 47
Total symbols: 382

Files by language:
  python: 35
  typescript: 10
  javascript: 2

Symbols by type:
  method: 245
  function: 67
  class: 42
  interface: 15
  async_method: 8
  async_function: 5

Indexed directories:
  .codemap/ (root files)
  .codemap/src/
  .codemap/src/components/
  .codemap/lib/
  .codemap/tests/
```

### `codemap lines RANGE_SPEC`

Validate if a line range is still valid (file hasn't changed).

```bash
codemap lines src/main.py:45-89
```

### `codemap install-hooks`

Install git pre-commit hook that automatically updates the codemap when committing code files.

```bash
codemap install-hooks
```

## Supported Languages

| Language | Parser | Symbol Types |
|----------|--------|--------------|
| Python | stdlib `ast` | class, function, method, async_function, async_method |
| TypeScript | tree-sitter | class, function, method, async_function, async_method, interface, type, enum |
| JavaScript | tree-sitter | class, function, method, async_function, async_method |

## Configuration

Create a `.codemaprc` file in your project root for custom settings:

```yaml
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
  - "**/migrations/**"

include:
  - "src/**"
  - "lib/**"

max_docstring_length: 150
output: .codemap
```

## Output Format

The `.codemap/` directory structure mirrors your project:

```
project/
├── .codemap/
│   ├── .codemap.json           # Root manifest with global metadata
│   ├── _root.codemap.json      # Files in project root
│   ├── src/
│   │   ├── .codemap.json       # Files in src/
│   │   └── components/
│   │       └── .codemap.json   # Files in src/components/
│   └── tests/
│       └── .codemap.json       # Files in tests/
├── src/
│   ├── main.py
│   └── components/
│       └── button.py
└── tests/
    └── test_main.py
```

### Root Manifest (`.codemap/.codemap.json`)

```json
{
  "version": "1.0",
  "generated_at": "2025-01-12T10:30:00Z",
  "root": "/path/to/project",
  "config": {
    "languages": ["python", "typescript"],
    "exclude_patterns": ["**/node_modules/**"]
  },
  "stats": {
    "total_files": 47,
    "total_symbols": 382
  },
  "directories": ["", "src", "src/components", "tests"]
}
```

### Directory Map (e.g., `.codemap/src/.codemap.json`)

```json
{
  "version": "1.0",
  "generated_at": "2025-01-12T10:30:00Z",
  "directory": "src",
  "files": {
    "main.py": {
      "hash": "a3f2b8c1d4e5",
      "indexed_at": "2025-01-12T10:30:00Z",
      "language": "python",
      "lines": 150,
      "symbols": [
        {
          "name": "UserService",
          "type": "class",
          "lines": [10, 150],
          "docstring": "Handles user operations",
          "children": [
            {
              "name": "get_user",
              "type": "method",
              "lines": [25, 50],
              "signature": "(self, user_id: int) -> User"
            }
          ]
        }
      ]
    }
  }
}
```

## Claude Code Integration

CodeMap includes a skill/plugin for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that enables automatic codebase navigation.

### Quick Install

```bash
# Install the skill for a single project
cp -r .claude/skills/codemap /path/to/your/project/.claude/skills/

# Or install the plugin globally
claude plugin install ./plugin
```

### What It Does

Once installed, Claude will automatically use CodeMap when:
- Looking for symbol definitions (classes, functions, methods)
- Exploring file structure
- Navigating large codebases

The skill teaches Claude the optimal workflow:
1. Use `codemap find` to locate symbols
2. Read only the relevant line ranges
3. Use `codemap show` for nested symbols
4. Validate freshness before re-reading

See [plugin/README.md](plugin/README.md) for detailed plugin documentation.

## LLM Usage Example

Instead of reading entire files, LLMs can:

1. **Query the index** to find symbol locations:
   ```
   codemap find "PaymentProcessor"
   → src/payments/processor.py:15-189 [class] PaymentProcessor
   ```

2. **Read only the relevant lines**:
   ```
   Read lines 15-189 from src/payments/processor.py
   ```

3. **Validate before re-reading** after context compaction:
   ```
   codemap validate src/payments/processor.py
   → Up to date (no need to re-read)
   ```

This reduces token consumption by only reading the specific code sections needed.

## Development

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=codemap

# Format code
black codemap
ruff check codemap
```

## Project Structure

```
codemap/
├── cli.py                 # Click CLI commands
├── core/
│   ├── indexer.py         # Main indexing orchestrator
│   ├── hasher.py          # SHA256 file hashing
│   ├── map_store.py       # Distributed JSON map CRUD operations
│   └── watcher.py         # File system watcher
├── parsers/
│   ├── base.py            # Abstract parser interface
│   ├── python_parser.py   # Python AST parser
│   ├── typescript_parser.py  # TypeScript tree-sitter parser
│   └── javascript_parser.py  # JavaScript tree-sitter parser
├── hooks/
│   ├── pre-commit         # Git hook script
│   └── installer.py       # Hook installation
├── utils/
│   ├── config.py          # Configuration management
│   └── file_utils.py      # File discovery utilities
└── tests/                 # Test suite (120+ tests)
```

## License

MIT
