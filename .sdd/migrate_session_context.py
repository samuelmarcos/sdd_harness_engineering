#!/usr/bin/env python3
"""Migra arquivos planos legados em session-context/ para a estrutura global/features."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


LEGACY_FILES = ("progress.md", "decisions.md", "next-steps.md")


def migrate(root: Path, dry_run: bool = False) -> list[str]:
    session_dir = root / ".claude" / "session-context"
    global_dir = session_dir / "global"
    actions: list[str] = []

    if not session_dir.is_dir():
        actions.append("session-context ausente — nada a migrar")
        return actions

    global_dir.mkdir(parents=True, exist_ok=True)
    working = global_dir / "working.md"

    if not working.is_file():
        legacy_progress = session_dir / "progress.md"
        if legacy_progress.is_file():
            target = working
            actions.append("progress.md → global/working.md")
            if not dry_run:
                shutil.copy2(legacy_progress, target)

    for name in LEGACY_FILES:
        source = session_dir / name
        if source.is_file():
            actions.append("mantém {} na raiz (compatível com hooks)".format(name))

    active = session_dir / "active-feature"
    if active.is_file():
        feature_id = active.read_text(encoding="utf-8").splitlines()[0].strip()
        if feature_id:
            feature_dir = session_dir / "features" / feature_id
            feature_dir.mkdir(parents=True, exist_ok=True)
            context = feature_dir / "context.md"
            if not context.is_file():
                actions.append(
                    "cria features/{}/context.md (vazio)".format(feature_id)
                )
                if not dry_run:
                    context.write_text(
                        "# Contexto da feature — {}\n".format(feature_id),
                        encoding="utf-8",
                    )

    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Migra session-context legado")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve(strict=False)
    actions = migrate(root, dry_run=args.dry_run)
    if not actions:
        print("Nada a migrar.")
        return 0
    for line in actions:
        prefix = "[dry-run] " if args.dry_run else ""
        print(prefix + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
