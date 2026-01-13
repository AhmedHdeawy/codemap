# CodeMap Usage (Embed in AI Assistant Instructions)

Copy the section below into your `CLAUDE.md`, `copilot-instructions.md`, or similar files:

---

## CodeMap - Codebase Index

This project has a `.codemap/` index for efficient code navigation. **Use CodeMap before scanning files.**

### Commands
```bash
codemap find "SymbolName"           # Find class/function/method/type by name
codemap find "name" --type method   # Filter by type (class|function|method|interface|type)
codemap show path/to/file.ts        # Show file structure with line ranges
codemap validate                    # Check if index is fresh
```

### Workflow
1. **Find symbol**: `codemap find "UserService"` → `src/services/user.ts:15-89 [class]`
2. **Read targeted lines**: Read only lines 15-89 instead of the full file
3. **Explore structure**: `codemap show src/services/user.ts` to see all methods/functions with line ranges
4. **Validate before re-read**: After context compaction, run `codemap validate path/to/file.ts` - if fresh, line numbers are still valid

### When to Use
- **USE CodeMap**: Finding symbol definitions, understanding file structure, locating code by name
- **READ full file**: Understanding implementation details, making edits, unindexed files

### Direct JSON Access
Symbol data is in `.codemap/<path>/.codemap.json` files - read directly for programmatic access.

---

## Minimal Version (For Space-Constrained Files)

```markdown
## CodeMap
Use `.codemap/` index before scanning files:
- `codemap find "Name"` - Find symbols by name
- `codemap show file.ts` - Show file structure with line ranges
- `codemap validate` - Check index freshness

Workflow: Find symbol → Read only those lines → Use `codemap show` for nested symbols
```
