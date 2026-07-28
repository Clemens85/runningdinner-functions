# Skill: Update Client Dependencies

## Description

Orchestrates a safe, incremental upgrade of all NodeJS dependencies across the `runningdinner-functions` PNPM monorepo (root `package.json`, and NodeJS Lambda sub-packages). A **main orchestrator agent** supervises a **worker agent** that performs the actual upgrades. Each dependency is upgraded, verified, and logged to a changelog before committing. If a upgrade is deemed impossible without human input, the process stops and the user is informed.

## Trigger

Use this skill when the user says something like:

- "Update/upgrade PNPM dependencies"
- "Check for new NodeJS package versions"
- "Run dependency updates"
- Invokes this skill by name

---

## Prerequisites & Permissions (Ask ONCE before starting)

Before doing any work, ask the user the following questions in a single message. Do not start until you have answers for all required items:

1. **Commit permission** (required): "May I create git commits for each successfully verified upgrade batch?"
2. **E2E tests** (required): "Should I run tests as a final sanity check?
3. **Scope** (optional, default = all): "Are there any packages you want to skip or pin? 

Store the answers in session memory under `/memories/session/dep-upgrade-permissions.md` and read them at the start of every sub-task.

---

## Monorepo Structure Reference

```
runningdinner-functions/
  package.json          ← root: shared devDependencies (TypeScript, Vite, ESLint, Vitest, React, etc.)
  pnpm-workspace.yaml
  packages/
    ...

### Key Commands

```bash
# From runningdinner-client/
pnpm install                    # install after version changes
pnpm typecheck                  # run tsc across all packages (MUST pass)
pnpm test                       # run Vitest unit tests across all packages
```

---

## Changelog File

Maintain a file at `runningdinner-client/DEPENDENCY_CHANGELOG.md`.

- Create it if it does not exist.
- Prepend a new dated section on each run using the format below.
- Do not overwrite previous entries.

```markdown
## YYYY-MM-DD – Dependency Update Run

### Updated

| Package | Location | Old Version | New Version | Notes                           |
| ------- | -------- | ----------- | ----------- | ------------------------------- |
| axios   | root     | 1.16.0      | 1.17.0      | Patch bump, no breaking changes |

### Skipped / Blocked

| Package | Reason              |
| ------- | ------------------- |
| yup     | User requested skip |

### Failed / Needs Human Review

| Package          | Reason                                                             |
| ---------------- | ------------------------------------------------------------------ |
| react-router-dom | Migration guide step requires manual route refactor – stopped here |
```

---

## Upgrade Order (Worker Agent Must Follow)

Process dependencies in the order below – smaller/lower-risk packages first, larger/higher-risk last. Within each tier, packages can be batched together if they have no interdependencies.

### Tier 1 – Utilities & Tooling (low risk)

- `axios`, `lodash-es`, `uuid`
- `date-fns` ← **check for coupled upgrade** (see Cross-Dependency Rules below)
- `typescript` (check for any new strict rules that break compilation)
- `prettier`, `eslint` and all `eslint-*` plugins
- `@types/*` packages

### Tier 2 – Build & Test Infrastructure (medium risk)

- `vite` and `@vitejs/*` plugins
- `vitest`
- `@testing-library/*`, `jsdom`
- `globals`

### Tier 3 – AWS SDK depdendencies (medium risk)

- `@aws-sdk/client-dynamodb`
- `CDK`
- ...

---

                                      |

## Worker Agent Protocol (Per Dependency or Batch)

For each package (or small batch of related packages in the same tier):

### Step 1 – Check Latest Version & Peer Dependencies

```bash
# In runningdinner-client/
pnpm outdated --recursive 2>/dev/null | grep <package>
# Or check npm registry directly:
npm show <package> version
# Check declared peer dependencies of the new version BEFORE editing package.json:
npm show <package>@<new-version> peerDependencies
```

For every package in a **known coupled group** (see Cross-Dependency Rules), run `npm show ... peerDependencies` on each group member before editing any `package.json`. Determine the full compatible version set first, then apply all bumps together in one batch.

### Step 2 – Consult Migration Guide (Tier 3 and above, or any MAJOR bump)

- Use `mcp_context7_resolve-library-id` + `mcp_context7_query-docs` to fetch:
  - The **changelog** or **migration guide** for the target version.
  - Pay special attention to: breaking API changes, removed exports, peer dependency requirements.
- Document key breaking changes in the changelog entry under "Notes".

### Step 3 – Apply the Version Bump

Edit the relevant `package.json` file(s) directly. Change the version specifier to the new exact version (remove `^` or `~` – use exact versions consistent with the rest of the file).

Then install:

```bash
cd <package> && pnpm install
```

### Step 4 – Apply Required Code Migrations

If the migration guide identified breaking changes, apply the necessary code changes now before running checks. Document what was changed in the changelog "Notes" column.

### Step 5 – Verify

Run in order, stopping immediately if any step fails:

```bash
pnpm typecheck
pnpm test
```

If `typecheck` or `test` fails:

1. Read the full error output carefully.
2. Attempt to fix the error (consult migration docs again if needed).
3. Re-run the failing check.
4. If the error cannot be resolved after **two attempts**, mark the package as **"Needs Human Review"** in the changelog, revert the version bump (`git checkout -- .`), and skip to the next package. Do NOT stop the entire process unless the failure blocks all subsequent upgrades.

### Step 6 – Commit (if user approved)

```bash
cd /home/clemens/Projects/runningdinner-functions
...
git commit -m "chore(deps): upgrade <package> <old> → <new>"
```

Use conventional commit format. Group patch-only bumps from Tier 1 into a single commit if convenient.

---

## Orchestrator Agent Protocol

The main orchestrator agent is responsible for:

1. **Loading permissions** from `/memories/session/dep-upgrade-permissions.md`.
2. **Invoking the worker agent** (via `runSubagent`) for each tier or batch. Pass the full context: tier, packages to upgrade, permissions, changelog path.
3. **Reading the worker's result** and updating the session todo list.
4. **Handling blocked upgrades**: if the worker marks a package as "Needs Human Review", the orchestrator logs it in the changelog and continues with the next package.
5. **Final commit** of the changelog file if not already committed with the last batch.
6. **Reporting** a summary to the user:
   - List of all upgraded packages with old → new versions
   - List of skipped/blocked packages with reasons

### Stopping Conditions

The orchestrator MUST stop the entire process and report to the user if:

- A package upgrade causes compilation failures that cannot be fixed automatically.
- A migration requires architectural decisions that cannot be inferred from code.
- `pnpm install` itself fails due to unresolvable peer dependency conflicts across the monorepo.
- The user's pre-approved skip list cannot be satisfied (e.g., a required peer dep forces an upgrade of a skipped package).

When stopping, the orchestrator must:

1. Revert any uncommitted changes
2. Write the reason to the `DEPENDENCY_CHANGELOG.md` under "Failed / Needs Human Review".
3. Commit the changelog.
4. Report clearly to the user what happened and what decision is needed.

---

## Session Memory Layout

Create and maintain `/memories/session/dep-upgrade-permissions.md`:

```markdown
# Dependency Upgrade Session

## Permissions

- commit: yes/no
- skip: [list of packages to skip]

## Progress

- [ ] Tier 1 – Utilities & Tooling
- [ ] Tier 2 – Build & Test Infrastructure
- [ ] Tier 3 – AWS SDK dependencies

## Blocked Packages

(filled by worker agent results)

## Discovered Coupled Groups (runtime)

(filled when pnpm install warns about new peer dependency conflicts during the run)

```

---

## Important Notes

- **Never use `pnpm update` or `ncu -u` blindly** – always inspect the target version and migration guide before editing `package.json`.
- **Peer dependency warnings from pnpm are acceptable** unless they cause actual build or test failures.
- All version specifiers in the root `package.json` should use exact versions (no `^`) for production deps, consistent with current style.
