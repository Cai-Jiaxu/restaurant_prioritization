---
description: Prime the context of the project by reading key files
---

# How to prime the context of the project

Please prime the context of the project: $ARGUMENTS.

Follow this systematic approach:

## 1. Read Core Documentation

- Read README.md to understand project overview
- Read CLAUDE.md for Claude-specific context

## 2. Analyze Project Structure

- Run `git ls-files | grep -v -f (sed 's|^|^|; s|$|/|' .cursorignore | psub)` to understand the project file structure
- Identify key directories and their purposes
- Understand the project architecture and organization

## 3. Understand Development Context

- Review package.json or equivalent dependency files
- Check configuration files
- Understand build and deployment processes
