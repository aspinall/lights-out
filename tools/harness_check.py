#!/usr/bin/env python3
"""Validate the repository knowledge harness without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REQUIRED_FILES = (
    "AGENTS.md",
    "ARCHITECTURE.md",
    "README.md",
    "harness/project.json",
    "docs/README.md",
    "docs/PRODUCT.md",
    "docs/DESIGN.md",
    "docs/QUALITY.md",
    "docs/RELIABILITY.md",
    "docs/SECURITY.md",
    "docs/GOLDEN_PRINCIPLES.md",
    "docs/product-specs/index.md",
    "docs/design-docs/index.md",
    "docs/exec-plans/README.md",
    "docs/exec-plans/tech-debt.md",
)

REQUIRED_PLAN_HEADINGS = (
    "Outcome",
    "Context",
    "Acceptance criteria",
    "Steps",
    "Progress log",
    "Decision log",
    "Risks and recovery",
    "Verification",
    "Outcome notes",
)

MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
PLACEHOLDER = re.compile(r"replace-with-|YYYY-MM-DD", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    level: str
    path: str
    message: str

    def render(self) -> str:
        return f"{self.level}: {self.path}: {self.message}"


def markdown_files(root: Path) -> list[Path]:
    ignored = {".git", "node_modules", ".venv", "venv"}
    return [
        path
        for path in root.rglob("*.md")
        if not any(part in ignored for part in path.relative_to(root).parts)
    ]


def check_required_files(root: Path) -> list[Finding]:
    return [
        Finding("ERROR", relative, "required harness file is missing")
        for relative in REQUIRED_FILES
        if not (root / relative).is_file()
    ]


def check_project_config(root: Path) -> list[Finding]:
    path = root / "harness/project.json"
    if not path.is_file():
        return []
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [Finding("ERROR", "harness/project.json", f"invalid JSON: {error}")]

    findings: list[Finding] = []
    if config.get("schemaVersion") != 1:
        findings.append(Finding("ERROR", "harness/project.json", "schemaVersion must be 1"))
    for key in ("name", "summary"):
        if not isinstance(config.get(key), str) or not config[key].strip():
            findings.append(Finding("ERROR", "harness/project.json", f"{key} must be a non-empty string"))
    commands = config.get("commands")
    if not isinstance(commands, dict):
        findings.append(Finding("ERROR", "harness/project.json", "commands must be an object"))
    else:
        for command in ("setup", "start", "test", "verify"):
            if not isinstance(commands.get(command), str) or not commands[command].strip():
                findings.append(
                    Finding("ERROR", "harness/project.json", f"commands.{command} must be a non-empty string")
                )
    if PLACEHOLDER.search(path.read_text(encoding="utf-8")):
        findings.append(Finding("WARN", "harness/project.json", "replace template project metadata and commands"))
    return findings


def check_agent_map(root: Path) -> list[Finding]:
    path = root / "AGENTS.md"
    if not path.is_file():
        return []
    line_count = len(path.read_text(encoding="utf-8").splitlines())
    if line_count > 120:
        return [
            Finding(
                "ERROR",
                "AGENTS.md",
                f"contains {line_count} lines; keep the map at or below 120 and move detail into docs/",
            )
        ]
    return []


def check_markdown_links(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in markdown_files(root):
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            target = target.strip("<>")
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                findings.append(
                    Finding("ERROR", str(path.relative_to(root)), f"link escapes repository: {raw_target}")
                )
                continue
            if not resolved.exists():
                findings.append(
                    Finding("ERROR", str(path.relative_to(root)), f"broken local link: {raw_target}")
                )
    return findings


def check_index(root: Path, directory: str, index: str, ignored_names: set[str]) -> list[Finding]:
    base = root / directory
    index_path = root / index
    if not base.is_dir() or not index_path.is_file():
        return []
    index_text = index_path.read_text(encoding="utf-8")
    findings: list[Finding] = []
    for path in base.glob("*.md"):
        if path.name in ignored_names:
            continue
        if path.name not in index_text:
            findings.append(Finding("ERROR", index, f"does not list {path.name}"))
    return findings


def check_active_plans(root: Path) -> list[Finding]:
    active = root / "docs/exec-plans/active"
    if not active.is_dir():
        return []
    findings: list[Finding] = []
    for path in active.glob("*.md"):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        headings = set(HEADING.findall(text))
        for required in REQUIRED_PLAN_HEADINGS:
            if required not in headings:
                findings.append(
                    Finding("ERROR", str(path.relative_to(root)), f"missing required section: ## {required}")
                )
        if "Status: Active" not in text:
            findings.append(Finding("ERROR", str(path.relative_to(root)), "active plan must contain 'Status: Active'"))
    return findings


def run_checks(root: Path) -> list[Finding]:
    checks = (
        check_required_files,
        check_project_config,
        check_agent_map,
        check_markdown_links,
        check_active_plans,
    )
    findings = [finding for check in checks for finding in check(root)]
    findings.extend(
        check_index(
            root,
            "docs/product-specs",
            "docs/product-specs/index.md",
            {"index.md", "SPEC_TEMPLATE.md"},
        )
    )
    findings.extend(
        check_index(
            root,
            "docs/design-docs",
            "docs/design-docs/index.md",
            {"index.md", "DESIGN_TEMPLATE.md"},
        )
    )
    return sorted(findings, key=lambda item: (item.level != "ERROR", item.path, item.message))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd(), help="repository root")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    findings = run_checks(root)
    for finding in findings:
        print(finding.render())
    errors = sum(finding.level == "ERROR" for finding in findings)
    warnings = sum(finding.level == "WARN" for finding in findings)
    print(f"Harness check: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

