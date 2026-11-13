# Contributing to Yggdrasil

## 1. Scope

- This document applies to every repository in the `yggdrasil-iiot` organization.
- A repository that has its own `CONTRIBUTING.md` follows that file instead of this one.
- This document covers only what is common to all repositories. Build, test, and gate commands are in each repository's README and `docs/`.

## 2. Language

- Commit subjects, commit messages, pull request titles, and pull request bodies are written in English.

## 3. Branches and pull requests

1. Every change lands on the default branch through a pull request from a separate branch.
2. One pull request covers one concern.
3. Keep pull requests small enough to review in one sitting; split a larger change into a sequence of pull requests.
4. The pull request title follows the commit subject rules in section 4.
5. The pull request body follows section 5.

## 4. Commit messages

The format is Conventional Commits 1.0.0 with three added constraints: the scope is optional, the subject line is at most 72 characters, and the subject is in the imperative mood.

### 4.1 Subject

1. Form: `type(scope): subject` or `type: subject`.
2. `type` is one of: `feat`, `fix`, `docs`, `ci`, `test`, `chore`, `refactor`, `build`, `perf`, `revert`, `style`.
3. `scope` names the module or area changed and is optional.
4. The subject is in the imperative mood: "add", "fix", "describe" (not "added", "adds", "adding").
5. The whole subject line is at most 72 characters.
6. The subject has no final period.

Examples:

```
feat(gates): add manifest digest check to provenance verify
fix(heimdall): reject NaN setpoints at the write boundary
docs: describe the registry layout in the README
ci: run the test suite on Windows
```

### 4.2 Breaking changes

1. Put `!` after the type or the scope.
2. Add a `BREAKING CHANGE:` footer that states what breaks.

Example:

```
feat(config)!: rename brokerUrl to brokerUri

The configuration key is renamed to match the URI type it holds.

BREAKING CHANGE: configurations that set brokerUrl must set brokerUri.
```

### 4.3 Body

1. Leave one blank line between the subject and the body.
2. Write declarative sentences that state what changed and why.
3. State verifiable facts only.
4. A trivial change needs no body.

Example:

```
fix(sim): restamp source timestamps on every scan

The simulator kept the timestamp from the first scan, so every value
after it looked stale to a freshness check. Each scan now writes the
current time as the source timestamp.
```

### 4.4 AI-assisted commits

1. A commit written with AI assistance ends with the trailer
   `Co-Authored-By: Claude <model> <noreply@anthropic.com>`, where `<model>` is the model name.
2. A pull request body created with Claude Code ends with the line
   `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
3. These two lines are the only mention of AI tools in commit or pull request text.

## 5. Pull request title and body

### 5.1 Title

- The title follows section 4.1 exactly: `type(scope): subject`, imperative, at most 72 characters, no final period, `!` for a breaking change.

### 5.2 Body

The body has these five sections, in this order. The pull request template provides the headings.

1. **Summary** — what the pull request does and why, in a few sentences.
2. **Changes** — the concrete changes, as a list.
3. **Verification** — see section 6.
4. **Deviations from plan or spec** — where the change departs from the plan or specification it implements, and why; or "None".
5. **Out of scope** — related work this pull request deliberately leaves out; or "None".

Body text follows section 4.3: declarative sentences, what changed and why, verifiable facts only.

## 6. Verification reporting

1. List the commands that were actually run.
2. State the commit they were run at.
3. State the result of each command, including failures and skips.
4. Report numbers that were measured in that run, not copied from another document or an earlier run.

Example:

```
## Verification

Run at commit `1a2b3c4`.

- `mvn clean test` — 242 tests, 0 failures, 0 errors, 7 skipped.
- `./scripts/check-ascii-names.sh` — exit 0.
- `mvn -pl gates verify` — 1 failure: `ManifestGateIT.rejectsStaleHead`,
  fixed in the next commit and rerun at `5d6e7f8`: 0 failures.
```

## 7. References

1. Every reference in a commit message, pull request or document resolves publicly: a file in the repository at that commit, an issue or pull request, or a public URL.
2. Cite a decision by stating the decision and its date.

Example:

```
The subject limit is 72 characters (decided 2026-11-13).
See `docs/INTEGRATION.md` and #19.
```

## 8. License

- Each repository that contains code states its license in its `LICENSE` file; a contribution to a repository is made under that repository's license.

## 9. Security issues

- Report security issues as described in `SECURITY.md`. The organization default is `SECURITY.md` at the root of the `.github` repository; a repository that has its own `SECURITY.md` follows that file.
