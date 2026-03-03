---
description: Deep dive into directory structure, architecture, and implementation patterns
---

# How to analyze directory structure and purpose

Please analyze the directory structure and purpose of: $ARGUMENTS.

Follow these steps:

## 1. Initial Directory Analysis

1. **List directory contents:**
   ```bash
   ls -la $DIRECTORY
   find $DIRECTORY -type f -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" | head -20
   ```

2. **Understand project structure:**
   ```bash
   # Check for configuration files
   ls -la | grep -E "(package\.json|tsconfig|webpack|vite|next\.config)"
   
   # Look for key directories
   find . -type d -name "src" -o -name "components" -o -name "utils" -o -name "hooks" | head -10
   ```

3. **Identify key files:**
   - Entry points (index files, main files)
   - Configuration files
   - Test files and test structure
   - Documentation files

## 2. Architecture Investigation

1. **Analyze implementation patterns:**
   - Design patterns being used (MVC, Repository, Factory, etc.)
   - State management approach
   - Component structure and hierarchy
   - Service/API layer organization

2. **Examine dependencies:**
   ```bash
   # Check package.json for dependencies
   cat package.json | jq '.dependencies, .devDependencies'
   ```

3. **Code organization analysis:**
   - File naming conventions
   - Directory structure patterns
   - Module boundaries and interfaces
   - Shared utilities and helpers

## 3. Deep Code Analysis

1. **Search for key patterns:**
   ```bash
   # Find React components
   grep -r "export.*function.*Component\|export.*const.*=.*React" --include="*.tsx" --include="*.jsx"
   
   # Find API endpoints
   grep -r "app\.(get\|post\|put\|delete)\|router\.(get\|post\|put\|delete)" --include="*.ts" --include="*.js"
   
   # Find test files
   find . -name "*.test.*" -o -name "*.spec.*" | head -10
   ```

2. **Understand data flow:**
   - Props and state management
   - API integration patterns
   - Event handling and side effects
   - Error boundaries and error handling

## 4. Documentation Creation

1. **Create or update CLAUDE.md:**
   ```markdown
   # [Directory Name] Architecture Overview
   
   ## Purpose
   Brief description of what this directory/module is responsible for.
   
   ## Key Components
   - Component/Module 1: Description and responsibility
   - Component/Module 2: Description and responsibility
   
   ## Architecture Decisions
   - Decision 1: Rationale and implications
   - Decision 2: Rationale and implications
   
   ## Implementation Patterns
   - Pattern 1: How and why it's used
   - Pattern 2: How and why it's used
   
   ## Dependencies
   - External libraries and their purposes
   - Internal module dependencies
   
   ## Common Operations
   - How to add new features
   - How to modify existing functionality
   - Testing approach
   
   ## Gotchas and Non-obvious Behaviors
   - Potential pitfalls
   - Non-intuitive implementations
   - Performance considerations
   ```

2. **Place documentation strategically:**
   - Put CLAUDE.md in the analyzed directory
   - Ensure it's loaded when working in that context
   - Update existing documentation if present

## 5. Quality Checks

1. **Verify documentation completeness:**
   - All major components documented
   - Architecture decisions explained
   - Common tasks covered
   - Gotchas identified

2. **Validate understanding:**
   - Cross-reference with existing documentation
   - Check against actual code implementation
   - Ensure accuracy of architectural descriptions

## Best Practices

- **Be thorough but concise** - Document what matters for understanding and maintenance
- **Focus on "why" over "what"** - Explain decisions and trade-offs
- **Include examples** - Show how to work with the code
- **Keep it current** - Update documentation as you discover new information
- **Think about newcomers** - Write for developers unfamiliar with the codebase

## Credit

This command is based on the work of Thomas Landgraf: https://thomaslandgraf.substack.com/p/claude-codes-memory-working-with
