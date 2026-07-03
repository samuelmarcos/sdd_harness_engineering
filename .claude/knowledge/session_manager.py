"""Gestão de memória curta (session-context) e longa (knowledge/checkpoints)."""

from __future__ import annotations

import datetime as dt
import json
import re
import uuid
from pathlib import Path
from typing import Any


DEFAULT_SESSION_MEMORY = {
    "enabled": True,
    "tokenThreshold": 8000,
    "approxCharsPerToken": 4,
    "persistence": "json",
    "longTermDir": ".claude/knowledge/checkpoints",
    "summaryMaxLines": 40,
}


def utc_now_iso() -> str:
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def utc_today() -> str:
    return utc_now_iso()[:10]


class SessionManager:
    """Curto prazo: .claude/session-context/ | Longo prazo: knowledge/checkpoints."""

    def __init__(self, root: Path, config: dict[str, Any] | None = None):
        self.root = root.resolve()
        merged = dict(DEFAULT_SESSION_MEMORY)
        if config:
            session_cfg = config.get("sessionMemory")
            if isinstance(session_cfg, dict):
                merged.update(session_cfg)
        self.config = merged
        self.session_dir = self.root / ".claude" / "session-context"
        self.templates_dir = self.session_dir / "_templates"
        long_term = self.config.get("longTermDir", DEFAULT_SESSION_MEMORY["longTermDir"])
        self.long_term_dir = (self.root / long_term).resolve()

    @property
    def enabled(self) -> bool:
        return bool(self.config.get("enabled", True))

    def metadata_path(self) -> Path:
        return self.session_dir / "metadata.json"

    def global_working_path(self) -> Path:
        return self.session_dir / "global" / "working.md"

    def feature_context_path(self, feature_id: str) -> Path:
        return self.session_dir / "features" / feature_id / "context.md"

    def active_feature_path(self) -> Path:
        return self.session_dir / "active-feature"

    def read_json(self, path: Path) -> dict[str, Any]:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def write_json(self, path: Path, value: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def read_text(self, path: Path, default: str = "") -> str:
        if not path.is_file():
            return default
        return path.read_text(encoding="utf-8")

    def write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def estimate_tokens(self, text: str) -> int:
        ratio = int(self.config.get("approxCharsPerToken", 4) or 4)
        if ratio < 1:
            ratio = 4
        return max(0, (len(text) + ratio - 1) // ratio)

    def read_metadata(self) -> dict[str, Any]:
        path = self.metadata_path()
        if not path.is_file():
            return {}
        return self.read_json(path)

    def new_session_id(self) -> str:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
        return "sess-{}-{}".format(stamp, uuid.uuid4().hex[:8])

    def repair_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Corrige placeholders de template e campos ausentes."""
        session_id = str(metadata.get("sessionId", ""))
        if not session_id or "YYYYMMDD" in session_id:
            metadata["sessionId"] = self.new_session_id()
        created = str(metadata.get("createdAt", ""))
        if not created or "YYYY" in created:
            metadata["createdAt"] = utc_now_iso()
        metadata["updatedAt"] = utc_now_iso()
        metadata["tokenThreshold"] = int(
            metadata.get("tokenThreshold")
            or self.config.get("tokenThreshold", DEFAULT_SESSION_MEMORY["tokenThreshold"])
        )
        metadata.setdefault("checkpoints", [])
        metadata.setdefault("resumeStrategy", "summary")
        metadata.setdefault("estimatedTokens", 0)
        metadata.setdefault("activeFeature", None)
        return metadata

    def bootstrap(self) -> dict[str, Any]:
        """Inicializa estrutura de session-context se ausente."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        (self.session_dir / "global").mkdir(exist_ok=True)
        (self.session_dir / "features").mkdir(exist_ok=True)

        metadata = self.read_metadata()
        if not metadata:
            template_path = self.templates_dir / "metadata.template.json"
            if template_path.is_file():
                metadata = self.read_json(template_path)
            else:
                metadata = {
                    "sessionId": self.new_session_id(),
                    "createdAt": utc_now_iso(),
                    "updatedAt": utc_now_iso(),
                    "activeFeature": None,
                    "estimatedTokens": 0,
                    "tokenThreshold": self.config.get("tokenThreshold", 8000),
                    "checkpoints": [],
                    "resumeStrategy": "summary",
                }
        metadata = self.repair_metadata(metadata)
        self.write_json(self.metadata_path(), metadata)

        if not self.global_working_path().is_file():
            template = self.templates_dir / "global-working.template.md"
            content = (
                self.read_text(template)
                if template.is_file()
                else "# Contexto global\n"
            )
            self.write_text(self.global_working_path(), content)

        active = self.get_active_feature()
        if active:
            self.ensure_feature_context(active)
            metadata = self.read_metadata()
            metadata["activeFeature"] = active
            metadata["updatedAt"] = utc_now_iso()
            self.write_json(self.metadata_path(), metadata)

        self.refresh_token_estimate()
        return self.read_metadata()

    def set_active_feature(self, feature_id: str) -> None:
        """Define feature ativa e garante context.md escopado."""
        if not re.match(r"^\d{3,}-[a-z0-9]+(?:-[a-z0-9]+)*$", feature_id):
            raise ValueError("ID da feature inválido: {}".format(feature_id))
        self.write_text(self.active_feature_path(), feature_id + "\n")
        self.ensure_feature_context(feature_id)
        metadata = self.repair_metadata(self.read_metadata() or {})
        metadata["activeFeature"] = feature_id
        self.write_json(self.metadata_path(), metadata)

    def update_next_steps(self, content: str) -> None:
        path = self.session_dir / "next-steps.md"
        self.write_text(path, content.rstrip() + "\n")
        self.refresh_token_estimate()

    def append_task_progress(
        self,
        feature_id: str,
        task_id: str,
        note: str,
        files: list[str] | None = None,
    ) -> None:
        """Registra conclusão parcial de task em features/<id>/context.md."""
        path = self.ensure_feature_context(feature_id)
        text = self.read_text(path)
        stamp = utc_now_iso()
        line = "- **{}** ({}): {}".format(task_id, stamp, note.strip())
        if files:
            line += " — arquivos: `{}`".format("`, `".join(files))
        section = "## Estado de implementação"
        if section in text:
            text = text.rstrip() + "\n" + line + "\n"
        else:
            text = text.rstrip() + "\n\n" + section + "\n\n" + line + "\n"
        self.write_text(path, text)
        feature_meta_path = path.parent / "metadata.json"
        feature_meta = (
            self.read_json(feature_meta_path)
            if feature_meta_path.is_file()
            else {
                "featureId": feature_id,
                "requiresPersistence": True,
                "resumeStrategy": "summary",
            }
        )
        feature_meta["lastTask"] = task_id
        feature_meta["updatedAt"] = stamp
        self.write_json(feature_meta_path, feature_meta)
        self.refresh_token_estimate()

    def get_active_feature(self) -> str | None:
        path = self.active_feature_path()
        if not path.is_file():
            return None
        line = path.read_text(encoding="utf-8").splitlines()
        feature_id = line[0].strip() if line else ""
        if not feature_id:
            return None
        if not re.match(r"^\d{3,}-[a-z0-9]+(?:-[a-z0-9]+)*$", feature_id):
            return None
        return feature_id

    def ensure_feature_context(self, feature_id: str) -> Path:
        path = self.feature_context_path(feature_id)
        if path.is_file():
            return path
        template = self.templates_dir / "feature-context.template.md"
        content = self.read_text(template) if template.is_file() else "# Feature\n"
        content = content.replace("{{feature_id}}", feature_id)
        title = feature_id
        status_path = self.root / "specs" / "features" / feature_id / "status.json"
        if status_path.is_file():
            try:
                status = self.read_json(status_path)
                title = status.get("title") or feature_id
            except (OSError, ValueError):
                pass
        content = content.replace("_(copiar título de status.json)_", title)
        self.write_text(path, content)
        feature_meta = path.parent / "metadata.json"
        if not feature_meta.is_file():
            self.write_json(
                feature_meta,
                {
                    "featureId": feature_id,
                    "requiresPersistence": True,
                    "resumeStrategy": "summary",
                    "updatedAt": utc_now_iso(),
                },
            )
        return path

    def collect_short_term_files(self) -> list[Path]:
        files: list[Path] = []
        for relative in (
            "global/working.md",
            "progress.md",
            "decisions.md",
            "next-steps.md",
        ):
            path = self.session_dir / relative
            if path.is_file():
                files.append(path)
        features_dir = self.session_dir / "features"
        if features_dir.is_dir():
            for path in sorted(features_dir.rglob("*.md")):
                files.append(path)
        return files

    def short_term_text(self) -> str:
        parts = []
        for path in self.collect_short_term_files():
            parts.append("<!-- {} -->\n".format(path.relative_to(self.session_dir)))
            parts.append(self.read_text(path))
            parts.append("\n")
        return "".join(parts)

    def refresh_token_estimate(self) -> int:
        metadata = self.read_metadata()
        if not metadata:
            return 0
        total = self.estimate_tokens(self.short_term_text())
        metadata["estimatedTokens"] = total
        metadata["updatedAt"] = utc_now_iso()
        metadata["tokenThreshold"] = int(
            metadata.get("tokenThreshold") or self.config.get("tokenThreshold", 8000)
        )
        self.write_json(self.metadata_path(), metadata)
        return total

    def should_checkpoint(self) -> bool:
        if not self.enabled:
            return False
        metadata = self.read_metadata()
        if not metadata:
            return False
        threshold = int(
            self.config.get("tokenThreshold")
            or metadata.get("tokenThreshold")
            or DEFAULT_SESSION_MEMORY["tokenThreshold"]
        )
        return self.refresh_token_estimate() >= threshold

    def summarize_text(self, text: str, label: str) -> str:
        lines = [line for line in text.splitlines() if line.strip()]
        max_lines = int(self.config.get("summaryMaxLines", 40) or 40)
        if len(lines) <= max_lines:
            body = text.strip()
        else:
            head = lines[: max_lines // 2]
            tail = lines[-(max_lines // 2) :]
            omitted = len(lines) - len(head) - len(tail)
            body = "\n".join(head + ["", "... [{} linhas omitidas] ...".format(omitted), ""] + tail)
        return (
            "# Checkpoint — {}\n\n"
            "- Arquivado em: {}\n"
            "- Tokens estimados (antes): {}\n\n"
            "{}\n"
        ).format(label, utc_now_iso(), self.estimate_tokens(text), body)

    def checkpoint_all(self, force: bool = False) -> list[str]:
        if not self.enabled:
            return []
        if not force and not self.should_checkpoint():
            return []

        metadata = self.read_metadata()
        if not metadata:
            self.bootstrap()
            metadata = self.read_metadata()

        session_id = metadata.get("sessionId") or self.new_session_id()
        archive_dir = self.long_term_dir / session_id / utc_now_iso().replace(":", "-")
        archive_dir.mkdir(parents=True, exist_ok=True)
        created: list[str] = []

        for path in self.collect_short_term_files():
            text = self.read_text(path)
            if not text.strip():
                continue
            rel = path.relative_to(self.session_dir)
            archive_path = archive_dir / rel
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            archive_path.write_text(text, encoding="utf-8")
            created.append(str(archive_path.relative_to(self.root)))

            summary = self.summarize_text(text, str(rel))
            stub = (
                "# Stub pós-checkpoint — {}\n\n"
                "> Conteúdo completo arquivado em: `{}`\n\n"
                "{}\n"
            ).format(rel, archive_path.relative_to(self.root), summary)
            self.write_text(path, stub)

        checkpoint_record = {
            "at": utc_now_iso(),
            "archiveDir": str(archive_dir.relative_to(self.root)),
            "files": created,
            "tokensBefore": metadata.get("estimatedTokens", 0),
        }
        metadata.setdefault("checkpoints", []).append(checkpoint_record)
        metadata["estimatedTokens"] = self.refresh_token_estimate()
        metadata["updatedAt"] = utc_now_iso()
        self.write_json(self.metadata_path(), metadata)

        index_path = self.long_term_dir / session_id / "index.json"
        index: list[Any] = []
        if index_path.is_file():
            try:
                index = self.read_json(index_path)
            except (OSError, ValueError):
                index = []
        if not isinstance(index, list):
            index = []
        index.append(checkpoint_record)
        self.write_json(index_path, {"sessionId": session_id, "checkpoints": index})

        return created

    def get_global_context(self) -> str:
        parts = [
            self.read_text(self.global_working_path()),
            self.read_text(self.session_dir / "decisions.md"),
            self.read_text(self.session_dir / "next-steps.md"),
        ]
        return "\n\n".join(part for part in parts if part.strip())

    def get_feature_context(self, feature_id: str) -> str:
        self.ensure_feature_context(feature_id)
        return self.read_text(self.feature_context_path(feature_id))

    def get_merged_context(self, feature_id: str | None = None) -> str:
        active = feature_id or self.get_active_feature()
        sections = ["## Contexto global (curto prazo)", self.get_global_context()]
        if active:
            sections.extend(
                [
                    "## Contexto da feature ({})".format(active),
                    self.get_feature_context(active),
                ]
            )
        long_term = self.get_long_term_hints()
        if long_term:
            sections.extend(["## Memória longa (hints)", long_term])
        return "\n\n".join(section for section in sections if section.strip())

    def get_long_term_hints(self) -> str:
        hints: list[str] = []
        lessons = self.root / ".claude" / "knowledge" / "learned-lessons.md"
        if lessons.is_file():
            text = self.read_text(lessons)
            lines = [
                line
                for line in text.splitlines()
                if line.strip().startswith("- [")
            ]
            if lines:
                hints.append("### Lições recentes\n" + "\n".join(lines[-5:]))
        session_id = self.read_metadata().get("sessionId")
        if session_id:
            index_path = self.long_term_dir / session_id / "index.json"
            if index_path.is_file():
                try:
                    index = self.read_json(index_path)
                    checkpoints = index.get("checkpoints", [])
                    if checkpoints:
                        last = checkpoints[-1]
                        hints.append(
                            "### Último checkpoint\n"
                            "- {}\n"
                            "- Arquivo: `{}`".format(
                                last.get("at", ""),
                                last.get("archiveDir", ""),
                            )
                        )
                except (OSError, ValueError):
                    pass
        return "\n\n".join(hints)

    def status_report(self) -> str:
        metadata = self.read_metadata() or self.bootstrap()
        active = self.get_active_feature()
        tokens = self.refresh_token_estimate()
        threshold = int(
            self.config.get("tokenThreshold")
            or metadata.get("tokenThreshold")
            or DEFAULT_SESSION_MEMORY["tokenThreshold"]
        )
        lines = [
            "Session memory: {}".format("enabled" if self.enabled else "disabled"),
            "Session ID: {}".format(metadata.get("sessionId", "(none)")),
            "Active feature: {}".format(active or "(none)"),
            "Estimated tokens: {} / {}".format(tokens, threshold),
            "Checkpoints: {}".format(len(metadata.get("checkpoints", []))),
            "Long-term dir: {}".format(self.long_term_dir.relative_to(self.root)),
        ]
        return "\n".join(lines)
