# Commit Guidelines

## Message format

```text
<type>: <short summary>

<body - optional>
```

- **type**: chore, feat, fix, docs, refactor, test, ci, perf, infra.
- **summary**: up to 72 characters, imperative mood (`add X`, `fix Y`).
- **body** (optional): explain *why* not *what*, each sentence on a new line.

## Rules

1. One logical change per commit.
2. No period at the end of the summary.
3. Run `git status` + tests before committing.
4. Breaking changes must include `BREAKING CHANGE: ...` in the body.
5. Never commit secrets or `.env` files.

## Examples

- `feat: add deals kanban board`
- `fix: handle backend auth errors in bff`
- `infra: add docker-compose files`
- `docs: update sprint plan`

Use this file as a quick reference when preparing commit history.
