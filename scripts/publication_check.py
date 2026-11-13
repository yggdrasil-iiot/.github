#!/usr/bin/env python3
"""Publication check for the repositories of the yggdrasil-iiot organization (CONTRIBUTING.md).

Checks the text a pull request or a push publishes:
  - every non-merge commit in the range: English message, `type(scope): subject` in the imperative mood,
    at most 72 characters, no final period, a blank line before the body, a GitHub no-reply author and
    committer address, no AI tool name outside the Co-Authored-By trailer;
  - the pull request title (same subject rules) and body (the five sections, English, no AI tool name
    outside the Claude Code footer);
  - every line a commit adds: no user-specific absolute path, no personal e-mail address.
Secrets are checked by gitleaks in a separate step of the workflow.

Usage:
  publication_check.py ci          GitHub Actions (reads GITHUB_EVENT_NAME and GITHUB_EVENT_PATH)
  publication_check.py selftest    synthetic violations in a temporary repository

A finding prints its rule, its location and an exception id, never the matched text. An exception id listed
in `.github/publication-exceptions.txt` of the checked repository (one per line, reviewed like any change)
clears exactly that finding.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TYPES = "feat|fix|docs|ci|test|chore|refactor|build|perf|revert|style"
SUBJECT = re.compile(r"^(" + TYPES + r")(\([a-z0-9][a-z0-9 ,./_+&-]*\))?!?: (\S.*)$")
HANGUL = re.compile(r"[\u1100-\u11ff\u3130-\u318f\uac00-\ud7a3]")
NOT_IMPERATIVE_OK = {"embed", "need", "seed", "feed", "speed", "proceed", "exceed", "succeed", "shed", "bring", "string", "ring", "sing"}
THIRD_PERSON = {"adds", "fixes", "updates", "removes", "makes", "uses", "moves", "changes", "describes", "replaces", "drops",
                "renames", "keeps", "bumps", "refactors", "improves", "documents", "allows", "ensures", "introduces", "supports",
                "returns", "runs", "checks", "handles", "creates", "deletes", "sets", "gets", "implements", "extends", "reads",
                "writes", "records", "rejects", "refuses", "aligns", "restores", "reverts", "splits", "merges", "builds"}
PR_SECTIONS = ["Summary", "Changes", "Verification", "Deviations from plan or spec", "Out of scope"]
TRAILER = re.compile(r"^Co-Authored-By: Claude [^<>\n]*<noreply@anthropic\.com>\s*$", re.M | re.I)
FOOTER = re.compile(r"^\s*🤖 Generated with \[Claude Code\]\(https://claude\.com/claude-code\)\s*$", re.M)
AI_NAMES = re.compile(r"(?<![\w-])(codex|fable|gemini|chatgpt|gpt-?\d[\w.-]*|gpt|claude|anthropic|openai|opus|sonnet|haiku|"
                      r"antigravity|agy|copilot)(?![\w-])", re.I)
NOREPLY = re.compile(r"^(?:[0-9]+\+)?[A-Za-z0-9._\[\]-]+@users\.noreply\.github\.com$|^noreply@github\.com$", re.I)
USER_PATHS = [
    re.compile(r"(?i)\b[a-z]:(?:\\\\|\\|/)+users(?:\\\\|\\|/)+([^\\/\s\"'`<>|*?]+)"),
    re.compile(r"(?i)(?<![\w.:/])/[a-z]/users/([^/\s\"'`<>]+)"),
    re.compile(r"(?<![\w.:/])/home/([a-z_][\w.-]*)"),
    re.compile(r"(?<![\w.:/])/Users/([A-Za-z][^/\s\"'`<>]*)/"),
]
PLACEHOLDER_USERS = {"runner", "runneradmin", "<user>", "user", "username", "you", "me", "$user", "%username%", "<name>"}
TLDS = ("com|org|net|io|dev|ai|app|co|kr|jp|cn|de|uk|fr|nl|eu|us|me|info|biz|edu|gov|mil|int|tech|cloud|xyz|site|online|"
        "page|so|sh|gg|tv|ca|au|in|ru|br|es|it|se|no|fi|dk|ch|at|be|pl|cz|tw|hk|sg|nz|il|email|mail")
EMAIL = re.compile(r"(?<![\w.%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(?:" + TLDS + r")(?![\w-])", re.I)
EMAIL_OK = re.compile(r"(?i)(@users\.noreply\.github\.com|^noreply@github\.com|^noreply@anthropic\.com|^git@github\.com|"
                      r"@(?:[\w-]+\.)*example\.(?:com|org|net))$")
ZERO = "0" * 40
DOC = re.compile(r"(?i)\.(md|markdown|txt|rst|adoc)$")


class Report:
    def __init__(self, exceptions: set[str]):
        self.exceptions, self.findings = exceptions, []

    def add(self, rule: str, where: str, key: str):
        eid = rule + ":" + hashlib.sha256(f"{rule}\0{key}".encode("utf-8")).hexdigest()[:20]
        if eid not in self.exceptions:
            self.findings.append((rule, where, eid))


def subject_problems(subject: str) -> list[str]:
    out = []
    if subject.startswith('Revert "'):
        return out
    if len(subject) > 72:
        out.append(f"longer than 72 characters ({len(subject)})")
    if subject.rstrip().endswith("."):
        out.append("ends with a period")
    m = SUBJECT.match(subject)
    if not m:
        out.append("not 'type(scope): subject'")
        return out
    first = re.split(r"[\s,:;(]", m.group(3), maxsplit=1)[0].lower()
    if "-" not in first and first not in NOT_IMPERATIVE_OK and (first.endswith("ed") or first.endswith("ing") or first in THIRD_PERSON):
        out.append(f"not imperative ('{first}')")
    return out


def body_problems(body: str) -> list[str]:
    heads = [m.group(1).strip() for m in re.finditer(r"(?m)^##\s+(.+?)\s*$", body)]
    found = [h for h in heads if h in PR_SECTIONS]
    missing = [s for s in PR_SECTIONS if s not in found]
    out = []
    if missing:
        out.append("missing section(s) " + ", ".join(missing))
    if len(found) != len(set(found)):
        out.append("a section appears twice")
    if not missing and found != PR_SECTIONS:
        out.append("sections out of order")
    return out


def text_rules(r: Report, text: str, where: str, key: str, ai_allowed=(TRAILER, FOOTER)):
    if HANGUL.search(text):
        r.add("LANG", f"{where}: write English", key + ":lang")
    stripped = text
    for rx in ai_allowed:
        stripped = rx.sub("", stripped)
    if AI_NAMES.search(stripped):
        r.add("AI-NAME", f"{where}: AI tool name outside the trailer or footer", key + ":ai")


def line_rules(r: Report, line: str, where: str, key: str, path: str):
    for rx in USER_PATHS:
        for m in rx.finditer(line):
            if m.group(1).lower() not in PLACEHOLDER_USERS:
                r.add("USER-PATH", f"{where}: user-specific absolute path", key + ":" + m.group(0))
    for m in EMAIL.finditer(line):
        if not EMAIL_OK.search(m.group(0)):
            r.add("EMAIL", f"{where}: e-mail address", key + ":" + m.group(0).lower())
    if DOC.search(path) and re.search(r"(?<![\w-])(codex|fable|gemini|agy|antigravity)(?![\w-])", line, re.I):
        r.add("AI-NAME", f"{where}: AI tool name in a document", key + ":doc-ai")


def git(*args: str, cwd: str | None = None) -> str:
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout


def check_commits(r: Report, base: str, head: str, cwd: str | None = None) -> int:
    if base == ZERO:
        rng = [head]
    else:
        git("cat-file", "-e", base + "^{commit}", cwd=cwd)
        rng = [f"{base}..{head}"]
    commits = git("rev-list", "--reverse", *rng, cwd=cwd).split()
    for c in commits:
        short = c[:12]
        parents = git("rev-list", "--parents", "-n", "1", c, cwd=cwd).split()[1:]
        meta = git("show", "-s", "--format=%ae%x00%ce%x00%B", c, cwd=cwd)
        ae, ce, msg = (meta.split("\0") + ["", "", ""])[:3]
        for who, e in (("author", ae), ("committer", ce)):
            if not NOREPLY.match(e.strip()):
                r.add("IDENTITY", f"commit {short} {who}: use a GitHub no-reply address", f"{c}:{who}")
        if len(parents) > 1:
            continue   # merge commits: GitHub writes their message
        lines = msg.strip("\n").split("\n")
        for prob in subject_problems(lines[0]):
            r.add("SUBJECT", f"commit {short} subject: {prob}", f"{c}:subject")
        if len(lines) > 1 and lines[1].strip():
            r.add("SUBJECT", f"commit {short}: no blank line after the subject", f"{c}:blank")
        text_rules(r, msg, f"commit {short} message", c, (TRAILER,))
        args = (["diff", "--no-color", "--no-ext-diff", "--text", "-U0", parents[0], c] if parents
                else ["show", "--no-color", "--no-ext-diff", "--text", "-U0", "--format=", c])
        path, n = None, 0
        for ln in git(*args, cwd=cwd).splitlines():
            if ln.startswith("+++ "):
                path = ln[6:] if ln.startswith("+++ b/") else None
                continue
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", ln)
            if m:
                n = int(m.group(1))
                continue
            if path and ln.startswith("+") and not ln.startswith("+++"):
                line_rules(r, ln[1:], f"commit {short} {path}:{n}", f"{path}:{ln[1:]}", path)
                n += 1
    return len(commits)


def ci() -> int:
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event or not path or not Path(path).is_file():
        print("::error::publication check: no GitHub event to check")
        return 1
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    exc_file = Path(".github/publication-exceptions.txt")
    exceptions = {l.strip() for l in exc_file.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")} \
        if exc_file.is_file() else set()
    r = Report(exceptions)
    if event in ("pull_request", "pull_request_target"):
        pr = payload.get("pull_request") or {}
        title, body = pr.get("title"), pr.get("body") or ""
        base, head = (pr.get("base") or {}).get("sha"), (pr.get("head") or {}).get("sha")
        if not title or not base or not head:
            print("::error::publication check: the pull request payload lacks a title or commits")
            return 1
        for prob in subject_problems(title):
            r.add("SUBJECT", f"pull request title: {prob}", "title:" + title)
        text_rules(r, title, "pull request title", "title")
        for prob in body_problems(body):
            r.add("PR-BODY", f"pull request body: {prob}", "body:" + hashlib.sha256(body.encode()).hexdigest())
        text_rules(r, body, "pull request body", "body:" + hashlib.sha256(body.encode()).hexdigest())
        merge_base = git("merge-base", base, head).strip()
        count = check_commits(r, merge_base, head)
    elif event == "push":
        before, after = payload.get("before"), payload.get("after")
        if not after or after == ZERO:
            print("publication check: a deleted ref, nothing to check")
            return 0
        count = check_commits(r, before or ZERO, after)
    else:
        print(f"::error::publication check: event {event} is not supported")
        return 1
    for rule, where, eid in r.findings:
        print(f"::error::{rule} {where} (exception id {eid})")
    print(f"publication check: {count} commit(s), {len(r.findings)} finding(s)")
    return 1 if r.findings else 0


def selftest() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="pubcheck-"))
    me = "1+dev@users.noreply.github.com"
    env = dict(os.environ, GIT_AUTHOR_NAME="dev", GIT_AUTHOR_EMAIL=me, GIT_COMMITTER_NAME="dev", GIT_COMMITTER_EMAIL=me)
    results = []
    try:
        def run(*a, e=None):
            return subprocess.run(list(a), cwd=tmp, env=e or env, capture_output=True, text=True, encoding="utf-8")
        run("git", "init", "-q", "-b", "main")
        (tmp / "a.txt").write_text("a\n", encoding="utf-8")
        run("git", "add", "-A"); run("git", "commit", "-q", "-m", "docs: start")

        def case(name, files, msg, expect, e=None):
            base = git("rev-parse", "HEAD", cwd=str(tmp)).strip()
            for k, v in files.items():
                (tmp / k).parent.mkdir(parents=True, exist_ok=True)
                (tmp / k).write_text(v, encoding="utf-8")
            run("git", "add", "-A")
            (tmp.parent / "m.txt").write_text(msg, encoding="utf-8")
            run("git", "commit", "-q", "-F", str(tmp.parent / "m.txt"), e=e)
            r = Report(set())
            check_commits(r, base, git("rev-parse", "HEAD", cwd=str(tmp)).strip(), cwd=str(tmp))
            rules = {f[0] for f in r.findings}
            results.append((name, (expect in rules) if expect else not rules, rules))

        tr = "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
        case("clean", {"b.txt": "b\n"}, "feat(core): add a reader\n\nThe reader parses rows." + tr, None)
        case("korean", {"c.txt": "c\n"}, "feat: 읽기 추가" + tr, "LANG")
        case("past", {"d.txt": "d\n"}, "fix: added a check" + tr, "SUBJECT")
        case("long", {"e.txt": "e\n"}, "docs: " + "x" * 70, "SUBJECT")
        case("no-blank", {"f.txt": "f\n"}, "docs: add f\nbody", "SUBJECT")
        case("ai-name", {"g.txt": "g\n"}, "docs: add g as Gemini drafted" + tr, "AI-NAME")
        bs = chr(92)   # the synthetic violations are assembled at run time, so this file holds none of them literally
        case("user-path", {"h.md": "run C:" + bs + "Users" + bs + "alice" + bs + "repo" + bs + "x.ps1\n"}, "docs: add h", "USER-PATH")
        case("ci-path-ok", {"i.md": "path /home/runner/work\n"}, "docs: add i", None)
        at = chr(64)
        case("email", {"j.txt": "mail someone.real" + at + "gmail.com\n"}, "docs: add j", "EMAIL")
        case("email-ok", {"k.txt": "a@example.com 1+x@users.noreply.github.com\n"}, "docs: add k", None)
        case("doc-tool-name", {"l.md": "Answer keys by Codex\n"}, "docs: add l", "AI-NAME")
        case("identity", {"m.txt": "m\n"}, "docs: add m",
             "IDENTITY", e=dict(env, GIT_AUTHOR_EMAIL="real.person" + at + "gmail.com", GIT_COMMITTER_EMAIL="real.person" + at + "gmail.com"))
        five = "".join(f"## {s}\n\nText.\n\n" for s in PR_SECTIONS)
        results.append(("body-ok", not body_problems(five), body_problems(five)))
        results.append(("body-missing", bool(body_problems("## Summary\n\nx\n")), ""))
        results.append(("title-ok", not subject_problems("ci: run the publication check"), ""))
        results.append(("title-bad", bool(subject_problems("Updated the docs.")), ""))
        rr = Report(set()); rr.add("EMAIL", "x", "k"); eid = rr.findings[0][2]
        r2 = Report({eid}); r2.add("EMAIL", "x", "k"); r3 = Report({eid}); r3.add("EMAIL", "x", "other")
        results.append(("exception-exact", not r2.findings and bool(r3.findings), ""))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = [x for x in results if not x[1]]
    for name, ok, note in results:
        print(("PASS " if ok else "FAIL ") + name + ("" if ok else f" :: {note}"))
    print(f"selftest: {len(results) - len(bad)} / {len(results)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "ci":
        try:
            sys.exit(ci())
        except Exception as e:   # a check that cannot run fails
            print(f"::error::publication check could not run ({type(e).__name__}: {e})")
            sys.exit(1)
    if mode == "selftest":
        sys.exit(selftest())
    print(__doc__)
    sys.exit(2)
