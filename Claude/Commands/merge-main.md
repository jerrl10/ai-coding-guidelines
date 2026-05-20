# Intelligent Merge from Main

## Current Context

**Current branch:** !`git branch --show-current`

**Branch status:** !`git status --short`

**Commits behind main:** !`git rev-list --count HEAD..main`

## Pre-Merge Checks

Before merging, verify:

1. **Working directory is clean:**
   - Run: `git status`
   - If there are uncommitted changes, ask the user if they want to:
     - Stash them: `git stash`
     - Commit them first
     - Abort the merge

2. **Fetch latest main:**
   - Run: `git fetch origin main`

3. **Show what will be merged:**
   - Run: `git log HEAD..main --oneline --graph`
   - Summarize the changes that will come from main

## Merge Process

1. **Attempt merge:**
```bash
   git merge main
```

2. **Check for conflicts:**
```bash
   git status | grep "Unmerged paths"
```

## If Conflicts Occur

### Step 1: List All Conflicted Files
Show all files with conflicts:
```bash
git diff --name-only --diff-filter=U
```

### Step 2: Analyze Each Conflict

For EACH conflicted file:

1. **Show the conflict:**
```bash
   git diff <file>
```

2. **Understand the context:**
   - Read the file to understand what both sides are trying to do
   - Identify the conflicting sections

3. **Resolution strategy - IMPORTANT:**
   
   **PRESERVE BOTH LOGICS** whenever possible:
   
   - If both sides add different features → Keep both
   - If both sides modify same function differently → Keep both approaches (refactor if needed)
   - If changes are complementary → Merge them intelligently
   - If truly conflicting (same variable different values) → Ask user which to keep

4. **Resolve the conflict:**
   - Edit the file to include the best combination of both changes
   - Remove conflict markers
   - Ensure code is syntactically correct
   - Maintain code style consistency
   - Add comments if the merge logic is complex

5. **Mark as resolved:**
```bash
   git add <file>
```

### Step 3: Handle Special Cases

**For package.json / package-lock.json:**
- Prefer main's versions for dependencies
- Keep any new dependencies from your branch
- Run `npm install` to regenerate lock files

**For configuration files:**
- Merge all unique keys from both sides
- If same key with different values, keep both as comments and ask user

**For migration files:**
- Keep both migrations if they don't conflict
- Ask user to manually review if they modify same table/column
- NEVER automatically choose one over the other

### Step 4: Verify Resolution

After resolving all conflicts:

1. **Check no conflicts remain:**
```bash
   git diff --check
```

2. **Verify code compiles/runs:**
   - Run linter: `npm run lint` or equivalent
   - Run type checker if applicable
   - Try to run the app briefly to verify no syntax errors

3. **Show summary of changes:**
```bash
   git diff --cached --stat
```

## Final Summary

Provide a comprehensive summary:

### Conflicts Resolved:
- List each file that had conflicts
- Briefly describe how each was resolved
- Note any files that need manual review

### Resolution Strategy Used:
- Describe the approach taken (preserved both logics, merged features, etc.)

### Files Modified:
```bash
git status
```

### Next Steps:
1. **Review the changes carefully:**
```bash
   git diff --cached
```

2. **Test the application:**
   - Run tests: `npm test` or `pytest` or equivalent
   - Start the app and verify functionality
   - Check that both feature sets work correctly

3. **When ready, commit manually:**
```bash
   git commit -m "merge: integrate main branch changes into <current-branch>
   
   Conflicts resolved in:
   - <file1>: <brief description>
   - <file2>: <brief description>
   
   Both feature sets preserved and tested."
```

## ⚠️ CRITICAL RULES

**NEVER:**
- ❌ Auto-commit the merge (WAIT FOR USER)
- ❌ Choose one side blindly without understanding
- ❌ Delete functionality from either branch
- ❌ Resolve conflicts without showing the user what was done

**ALWAYS:**
- ✅ Preserve both logics whenever possible
- ✅ Show user what conflicts existed
- ✅ Explain resolution strategy
- ✅ Wait for user to manually commit
- ✅ Ask for clarification if truly conflicting logic
- ✅ Verify code still works after resolution

## Abort Option

If at any point the user wants to abort:
```bash
git merge --abort
```

---

**Remember: The user will commit manually. Your job is to resolve conflicts intelligently, preserve functionality, and explain what was done.**
EOF