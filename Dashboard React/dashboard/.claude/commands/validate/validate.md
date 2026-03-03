---
description: Validate the repository is in a working state
---

# Repository Health Check & CI Validation

## Overview

Verify the repository is in a working state by running comprehensive CI checks and fixing any issues. All commands are run from the repository root.

## Execution Steps

Run the following checks sequentially. **Do not proceed to the next step until the current command succeeds.**

### 1. Dependencies
```bash
pnpm i
```
Ensure all dependencies are installed and up to date.

### 2. Code Quality
```bash
pnpm lint
```
Verify code formatting and linting rules pass.

### 3. Type Safety & Build
```bash
pnpm nx run-many --targets=build:types,build:dist,build:app,generate:docs,dev:run,typecheck
```
Validate TypeScript types and successful builds.

### 4. Testing
```bash
# Source .env file first if it exists
pnpm nx run-many --target=test:coverage
```
Run tests with coverage. Execute one package at a time for easier debugging.

### 5. Package Management
```bash
pnpm run sort-package-json
pnpm nx run-many --targets=lint:package,lint:deps
```
Ensure package.json files are properly sorted and dependencies are valid.

### 6. Validation
If any fixes were made in previous steps, re-run all affected checks to ensure no regressions.

### 7. Staging
```bash
git status
git add [files]
```
Add files to staging. **Exclude git submodules in `lib/*` folders.**

## Completion
Print a checklist with ✅ next to each completed step.

---

## Error Resolution Protocol

When any check fails, follow this systematic approach:

### 1. Diagnose
- Analyze logs and source code to understand the root cause
- Look for supporting evidence in the codebase
- Add console logs if needed for debugging
- Ask for help if insufficient context exists

### 2. Fix
- Propose a solution with clear reasoning
- Explain why the fix should work
- If the fix fails, return to step 1

### 3. Verify Scope
- Check if the same issue exists elsewhere in the codebase
- Apply fixes broadly if needed

### 4. Clean Up
- Remove any debugging console logs
- Run formatting: `pnpm run lint`

---

## Important Guidelines

### Dependencies Installation
If `pnpm i` fails, abort unless it's a simple syntax error (missing comma, etc.).

### TypeScript Issues
- Look for type definitions in the codebase or `node_modules`
- Fix obvious type errors immediately
- Consult documentation after multiple failures

### Testing
- **Always use `test:coverage` target** (never run plain `test` as it may timeout)
- Run packages individually for easier debugging
- For snapshot test failures, explain why changes are expected before updating
- Add console logs to verify assumptions when debugging

### Code Changes
- Make fixes confidently - TypeScript and tests will catch regressions
- Don't skip fixes due to perceived risk

### After Making Fixes
1. Run `pnpm run lint` for formatting
2. Ask user before adding files to staging
3. Suggest commit message but let user commit manually

### Git Operations
- **Only add to staging, never commit automatically**
- Exclude git submodules in staging process
