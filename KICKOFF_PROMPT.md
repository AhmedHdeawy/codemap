I want to build a CLI tool called **CodeMap** that generates structural indexes of codebases to reduce LLM token consumption when reading files.

### What it does:
- Scans a codebase and creates a `.codemap.json` file
- Maps every class/function/method with their exact line numbers
- Stores file hashes to detect changes
- Enables targeted reads like "show me lines 45-89" instead of full files

### Core commands:
```bash
codemap init [path]           # Index a directory
codemap update <file>         # Reindex single file  
codemap find "SymbolName"     # Find symbol location
codemap show <file>           # Show file structure
codemap validate              # Check for stale entries
codemap install-hooks         # Install git pre-commit hook
```

### Tech stack:
- Python 3.10+
- Click for CLI
- stdlib `ast` for Python parsing
- tree-sitter for TypeScript/JavaScript
- PyYAML for config

### Please read the spec files first:
1. Read `PROJECT_SPEC.md` for full architecture and data models
2. Read `CLAUDE.md` for implementation guidelines

Then start building in this order:
1. Set up project structure with pyproject.toml
2. Implement core/hasher.py
3. Implement parsers/base.py and parsers/python_parser.py
4. Implement core/map_store.py
5. Implement core/indexer.py
6. Implement cli.py with init, update, find, show commands
7. Add tests

Focus on Python parsing first (MVP). We can add TypeScript/JS parsers later.

