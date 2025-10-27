from git import Repo
from pathlib import Path
import tempfile
import shutil
from pprint import pprint
import fnmatch

def get_repo(url: str, branch: str | None = None, max_commits: int = 5):
    temp_dir = tempfile.mkdtemp(prefix="temp_repo_")
    repo = Repo.clone_from(url, temp_dir, depth=50, single_branch=True)
    if branch:
        repo.git.checkout(branch)

    root = Path(temp_dir)

    exclude_dirs = {
        "node_modules", "dist", "build", ".next", "out", "coverage",
        "test", "tests", "__tests__", "__snapshots__", "examples", "example", "demo", "demos", ".git"
    }
    lockfiles = {
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
        "Cargo.lock", "Pipfile.lock", "poetry.lock"
    }
    test_globs = [
        "*.test.*", "*.spec.*", "*test*/*", "*tests*/*", "*__tests__*/*"
    ]

    # Allowed source extensions for diffs (keep it focused on code/config, not assets/docs)
    allowed_source_ext = {
        ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
        ".go", ".rs", ".java", ".kt", ".c", ".h", ".cpp", ".hpp",
        ".cs", ".rb", ".php", ".swift", ".scala", ".m", ".mm",
        ".sh", ".bash", ".zsh", ".ps1",
        ".yml", ".yaml", ".toml", ".ini", ".conf", ".properties",
        ".json", ".env", ".dockerfile", ".gradle", ".cfg"
    }

    def is_excluded_path(rel: Path) -> bool:
        parts = set(rel.parts)
        if parts & exclude_dirs:
            return True
        if rel.name in lockfiles:
            return True
        rel_str = rel.as_posix()
        for pat in test_globs:
            if fnmatch.fnmatch(rel_str, pat):
                return True
        p = (root / rel)
        try:
            if p.exists() and p.is_file() and p.stat().st_size > 200_000:
                return True
        except Exception:
            pass
        return False

    commits = []
    for c in repo.iter_commits(max_count=max_commits):
        try:
            name_only = repo.git.show(c.hexsha, "--name-only", "--pretty=").strip().splitlines()
        except Exception:
            name_only = []
        included_paths = []
        for n in name_only:
            if not n:
                continue
            rel = Path(n)
            if is_excluded_path(rel):
                continue
            # Only include source file extensions (skip docs/assets)
            if rel.suffix.lower() in allowed_source_ext:
                included_paths.append(rel.as_posix())

        diff_text = ""
        if included_paths:
            # Use minimal context to reduce size
            diff_text = repo.git.show(
                c.hexsha,
                "--format=",
                "--patch",
                "--no-color",
                "-U2",
                "--",
                *included_paths,
            )
            # Cap diff size to avoid huge payloads
            MAX_DIFF_CHARS = 80_000
            if len(diff_text) > MAX_DIFF_CHARS:
                diff_text = diff_text[:MAX_DIFF_CHARS] + "\n...\n[diff truncated]\n"

        commits.append({
            "hash": c.hexsha,
            "author": str(c.author),
            "email": getattr(c.author, "email", None),
            "date": c.committed_datetime.isoformat(),
            "message": c.message.strip(),
            "diff": diff_text,
            "files": included_paths,
        })

    doc_files = set()
    for pat in ("*.md", "*.rst", "*.adoc"):
        for p in root.rglob(pat):
            rel = p.relative_to(root)
            if is_excluded_path(rel):
                continue
            doc_files.add(p)
    for p in (root / "docs").rglob("*") if (root / "docs").exists() else []:
        if p.is_file():
            doc_files.add(p)
    for pat in ("README*", "CONTRIBUTING*", "LICENSE*"):
        for p in root.glob(pat):
            if p.is_file():
                doc_files.add(p)

    documentation = []
    for p in list(sorted(doc_files))[:20]:
        try:
            if p.stat().st_size > 120_000:
                continue
            content = p.read_text(encoding="utf-8", errors="ignore")
            documentation.append({
                "path": str(p.relative_to(root)),
                "content": content,
            })
        except Exception:
            continue

    return {
        "repo_path": temp_dir,
        "commits": commits,
        "documentation": documentation,
    }

def cleanup_repo(repo_path: str) -> bool:
    try:
        p = Path(repo_path)
        if p.exists() and p.is_dir() and p.name.startswith("temp_repo_"):
            shutil.rmtree(p)
            return True
    except Exception:
        return False
    return False

if __name__ == "__main__":
    repo = get_repo("https://github.com/michniks2001/s-lang")
    pprint(repo)
    cleanup_repo(repo["repo_path"])