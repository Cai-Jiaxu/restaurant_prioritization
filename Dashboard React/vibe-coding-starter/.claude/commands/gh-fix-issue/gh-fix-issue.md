---
description: Fix a GitHub issue with comprehensive git workflow
---

# How to fix a GitHub issue

Please analyze and fix the GitHub issue: $ARGUMENTS.

Follow these steps:

## 1. Initial Setup & Issue Analysis

1. **Get issue details:**
   ```bash
   gh issue view $ISSUE_NUMBER
   ```

2. **Check current git status:**
   ```bash
   git status
   git branch
   ```

3. **Ensure you're on the main branch and up to date:**
   ```bash
   git checkout main
   git pull origin main
   ```

## 2. Create Feature Branch

1. **Create and switch to a new branch:**
   ```bash
   git checkout -b fix/issue-$ISSUE_NUMBER
   # or for more descriptive naming:
   git checkout -b fix/issue-$ISSUE_NUMBER-short-description
   ```

2. **Verify branch creation:**
   ```bash
   git branch --show-current
   ```

## 3. Development Workflow

1. **Understand the problem** described in the issue
2. **Search the codebase** for relevant files
3. **Implement the necessary changes** to fix the issue

### During development:

- **Check what files have changed:**
  ```bash
  git status
  git diff
  ```

- **Stage specific files:**
  ```bash
  git add path/to/file.ts
  # or stage all changes:
  git add .
  ```

- **Make incremental commits:**
  ```bash
  git commit -m "fix: address part of issue #$ISSUE_NUMBER - description"
  ```

## 4. Testing & Validation

1. **Write and run tests** to verify the fix
2. **Ensure code passes linting and type checking:**
   ```bash
   npm run lint
   npm run type-check
   npm run test
   ```

3. **Check final diff before committing:**
   ```bash
   git diff --cached  # for staged changes
   git diff HEAD      # for all changes since last commit
   ```

## 5. Final Commit & Push

1. **Stage all final changes:**
   ```bash
   git add .
   ```

2. **Create a descriptive commit message:**
   ```bash
   git commit -m "fix: resolve issue #$ISSUE_NUMBER - detailed description

   - Specific change 1
   - Specific change 2
   - Any breaking changes or notes

   Fixes #$ISSUE_NUMBER"
   ```

3. **Push the branch to remote:**
   ```bash
   git push origin fix/issue-$ISSUE_NUMBER
   ```

## 6. Create Pull Request

1. **Create PR using GitHub CLI:**
   ```bash
   gh pr create --title "Fix: Issue #$ISSUE_NUMBER - Short Description" \
                --body "Fixes #$ISSUE_NUMBER

   ## Changes
   - List of changes made
   - Any relevant details

   ## Testing
   - How the fix was tested
   - Any additional considerations"
   ```

2. **Or create PR with auto-fill:**
   ```bash
   gh pr create --fill
   ```

## 7. Post-PR Workflow

1. **Check PR status:**
   ```bash
   gh pr status
   gh pr view
   ```

2. **If changes are requested, make updates:**
   ```bash
   # Make changes
   git add .
   git commit -m "fix: address PR feedback - description"
   git push origin fix/issue-$ISSUE_NUMBER
   ```

3. **After PR is merged, clean up:**
   ```bash
   git checkout main
   git pull origin main
   git branch -d fix/issue-$ISSUE_NUMBER
   git remote prune origin  # clean up remote tracking branches
   ```

## Useful Git Commands During Development

### Viewing Changes
```bash
git log --oneline -10        # Recent commits
git show HEAD               # Latest commit details
git diff HEAD~1             # Changes since previous commit
git diff main..HEAD         # All changes on current branch
```

### Undoing Changes
```bash
git restore file.ts         # Discard unstaged changes
git restore --staged file.ts # Unstage changes
git reset HEAD~1            # Undo last commit (keep changes)
git reset --hard HEAD~1     # Undo last commit (discard changes)
```

### Branch Management
```bash
git branch -a               # List all branches
git branch -d branch-name   # Delete local branch
git push origin --delete branch-name  # Delete remote branch
```

## Best Practices

- **Use descriptive commit messages** that reference the issue number
- **Make atomic commits** - each commit should represent a single logical change
- **Test thoroughly** before pushing
- **Keep commits focused** on the specific issue being fixed
- **Use conventional commit format** (feat:, fix:, docs:, etc.)
- **Link commits to issues** using "Fixes #123" or "Closes #123"

Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks and follow the project's contribution guidelines.
