---
description: Create a pull request with proper branch and commit workflow
---

# How to create a pull request with Git

Please create a new branch, commit changes, and submit a pull request for: $ARGUMENTS.

Follow this systematic approach:

## Behavior

- Creates a new branch based on current changes
- Formats modified files
- Analyzes changes and automatically splits into logical commits when appropriate
- Each commit focuses on a single logical change or feature
- Creates descriptive commit messages for each logical unit
- Pushes branch to remote
- Creates pull request with proper summary

## Guidelines for Automatic Commit Splitting

- Split commits by feature, component, or concern
- Keep related file changes together in the same commit
- Separate refactoring from feature additions
- Ensure each commit can be understood independently
- Multiple unrelated changes should be split into separate commits
