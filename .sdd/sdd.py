#!/usr/bin/env python3
"""Controles determinísticos do harness SDD, sem dependências externas."""

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path


STATUS_VALUES = {
    "pending",
    "awaiting_approval",
    "approved",
    "in_progress",
    "in_review",
    "changes_requested",
    "verified",
    "done",
    "blocked",
    "cancelled",
    "superseded",
}
APPROVAL_REQUIRED = {
    "approved",
    "in_progress",
    "in_review",
    "changes_requested",
    "verified",
    "done",
    "blocked",
}
IMPLEMENTATION_ALLOWED = {"approved", "in_progress"}
REVIEW_REQUIRED = {"in_review", "verified", "done"}
SPEC_FILES = ("requirements.md", "design.md", "tasks.md")
PATH_KEYS = {"file_path", "filePath", "path"}


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def feature_dir(root, feature_id):
    return root / "specs" / "features" / feature_id


def feature_prefix(feature_id):
    match = re.match(r"^(\d{3,})-[a-z0-9]+(?:-[a-z0-9]+)*$", feature_id)
    if not match:
        raise ValueError(
            "ID da feature deve usar NNN-kebab-case (ex.: 001-user-auth)"
        )
    return "F" + match.group(1)


def spec_digest(root, feature_id):
    directory = feature_dir(root, feature_id)
    digest = hashlib.sha256()
    for filename in SPEC_FILES:
        path = directory / filename
        if not path.is_file():
            raise FileNotFoundError(str(path))
        content = path.read_bytes()
        if filename == "tasks.md":
            text = content.decode("utf-8")
            text = re.sub(
                r"^(\s*-\s*)\[[xX ]\]",
                r"\1[ ]",
                text,
                flags=re.MULTILINE,
            )
            content = text.encode("utf-8")
        digest.update(filename.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def approval_errors(root, feature_id, status):
    approval = status.get("approval")
    if not isinstance(approval, dict):
        return ["aprovação persistida ausente"]
    errors = []
    if approval.get("status") != "approved":
        errors.append("approval.status deve ser 'approved'")
    if not approval.get("approvedBy"):
        errors.append("approval.approvedBy ausente")
    if not approval.get("approvedAt"):
        errors.append("approval.approvedAt ausente")
    try:
        current_digest = spec_digest(root, feature_id)
    except FileNotFoundError as error:
        return ["arquivo de spec ausente: {}".format(error)]
    if approval.get("specRevision") != current_digest:
        errors.append("aprovação obsoleta: a spec mudou após a aprovação")
    return errors


def extract_paths(value):
    paths = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in PATH_KEYS and isinstance(child, str):
                paths.append(child)
            else:
                paths.extend(extract_paths(child))
    elif isinstance(value, list):
        for child in value:
            paths.extend(extract_paths(child))
    return paths


def canonical_path(root, raw_path):
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve(strict=False)


def is_within(path, directory):
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def protected_directories(root):
    config_path = root / ".sdd" / "config.json"
    protected = ["src"]
    if config_path.is_file():
        config = read_json(config_path)
        configured = config.get("protectedPaths")
        if isinstance(configured, list) and configured:
            protected = configured
    return [canonical_path(root, item) for item in protected]


def guard(payload, root):
    raw_targets = extract_paths(payload)
    if not raw_targets:
        return False, "SDD: payload de escrita sem path reconhecido."
    targets = [canonical_path(root, item) for item in raw_targets]
    try:
        protected = protected_directories(root)
    except (OSError, ValueError) as error:
        return False, "SDD: configuração inválida: {}.".format(error)
    protected_targets = [
        target
        for target in targets
        if any(is_within(target, directory) for directory in protected)
    ]
    if not protected_targets:
        return True, ""

    active_path = root / ".claude" / "session-context" / "active-feature"
    if not active_path.is_file():
        return False, "SDD: nenhuma feature ativa."
    lines = active_path.read_text(encoding="utf-8").splitlines()
    feature_id = lines[0].strip() if lines else ""
    try:
        feature_prefix(feature_id)
    except ValueError:
        return False, "SDD: active-feature contém ID inválido."

    status_path = feature_dir(root, feature_id) / "status.json"
    if not status_path.is_file():
        return False, "SDD: feature ativa sem status.json."
    try:
        status = read_json(status_path)
    except (OSError, ValueError) as error:
        return False, "SDD: status.json inválido: {}.".format(error)

    current_status = status.get("status")
    if current_status not in IMPLEMENTATION_ALLOWED:
        return False, (
            "SDD: feature '{}' está em '{}'. Código só é liberado em "
            "'approved' ou 'in_progress'.".format(feature_id, current_status)
        )
    errors = approval_errors(root, feature_id, status)
    if errors:
        return False, "SDD: aprovação inválida: {}.".format("; ".join(errors))
    return True, ""


def parse_requirements(text, prefix):
    qualified = set(re.findall(r"\*\*({}-R\d+)\*\*".format(prefix), text))
    unqualified = set(re.findall(r"\*\*(R\d+)\*\*", text))
    return qualified, unqualified


def parse_tasks(text, prefix):
    tasks = {}
    unqualified_refs = set()
    pattern = re.compile(
        r"^\s*-\s*\[([ xX])\]\s+({}-T\d+)\s+—\s+(.+)$".format(prefix),
        re.MULTILINE,
    )
    for match in pattern.finditer(text):
        body = match.group(3)
        refs = set(re.findall(r"{}-R\d+".format(prefix), body))
        unqualified_refs.update(re.findall(r"(?<![A-Z0-9-])R\d+", body))
        tasks[match.group(2)] = {
            "checked": match.group(1).lower() == "x",
            "requirements": refs,
        }
    return tasks, unqualified_refs


def coverage_markers(root, prefix):
    covered = set()
    harness_tests = (root / "tests" / "harness").resolve(strict=False)
    for base_name in ("tests", "src"):
        base = root / base_name
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if base_name == "src":
                lower_name = path.name.lower()
                if (
                    ".test." not in lower_name
                    and ".spec." not in lower_name
                    and "_test." not in lower_name
                    and not lower_name.startswith("test_")
                    and "__tests__" not in path.parts
                ):
                    continue
            resolved = path.resolve(strict=False)
            if is_within(resolved, harness_tests):
                continue
            if path.suffix.lower() in {".md", ".json", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            covered.update(
                re.findall(r"@covers\s+({}-R\d+)\b".format(prefix), text)
            )
    return covered


def review_errors(root, feature_id, status):
    reviews = status.get("reviews")
    if not isinstance(reviews, dict):
        return ["status.reviews ausente"]
    errors = []
    expected_dir = (feature_dir(root, feature_id) / "reviews").resolve(
        strict=False
    )
    for kind in ("qa", "traceability"):
        review = reviews.get(kind)
        if not isinstance(review, dict) or review.get("status") != "approved":
            errors.append("review '{}' ainda não foi aprovado".format(kind))
            continue
        report = review.get("report")
        if not report:
            errors.append("review '{}' não possui relatório".format(kind))
            continue
        report_path = canonical_path(root, report)
        if not is_within(report_path, expected_dir):
            errors.append(
                "relatório '{}' deve estar em specs/features/{}/reviews/".format(
                    kind, feature_id
                )
            )
        elif not report_path.is_file():
            errors.append(
                "relatório '{}' não encontrado: {}".format(kind, report)
            )
    return errors


def validate_status(status, feature_id):
    errors = []
    required = {
        "id",
        "title",
        "status",
        "created",
        "updated",
        "approval",
        "reviews",
    }
    absent = required - set(status)
    if absent:
        errors.append(
            "campos obrigatórios ausentes: {}".format(", ".join(sorted(absent)))
        )
    if status.get("id") != feature_id:
        errors.append("status.id deve ser '{}'".format(feature_id))
    if not isinstance(status.get("title"), str) or not status.get("title"):
        errors.append("status.title deve ser texto não vazio")
    if status.get("status") not in STATUS_VALUES:
        errors.append("status desconhecido: '{}'".format(status.get("status")))
    for field in ("created", "updated"):
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(status.get(field, ""))):
            errors.append("status.{} deve usar YYYY-MM-DD".format(field))
    reviews = status.get("reviews")
    if not isinstance(reviews, dict):
        errors.append("status.reviews deve ser objeto")
    else:
        for name in ("qa", "traceability"):
            review = reviews.get(name)
            if not isinstance(review, dict):
                errors.append("status.reviews.{} ausente".format(name))
                continue
            if review.get("status") not in {
                "pending",
                "approved",
                "changes_requested",
            }:
                errors.append("status.reviews.{}.status inválido".format(name))
            if "report" not in review:
                errors.append("status.reviews.{}.report ausente".format(name))
    return errors


def validate_feature(root, feature_id):
    directory = feature_dir(root, feature_id)
    status_path = directory / "status.json"
    if not status_path.is_file():
        return ["status.json ausente para {}".format(feature_id)]
    try:
        status = read_json(status_path)
    except (OSError, ValueError) as error:
        return ["status.json inválido: {}".format(error)]

    errors = validate_status(status, feature_id)
    try:
        prefix = feature_prefix(feature_id)
    except ValueError as error:
        return errors + [str(error)]

    missing = [name for name in SPEC_FILES if not (directory / name).is_file()]
    if missing:
        return errors + [
            "arquivos de spec ausentes: {}".format(", ".join(missing))
        ]

    requirements_text = (directory / "requirements.md").read_text(
        encoding="utf-8"
    )
    tasks_text = (directory / "tasks.md").read_text(encoding="utf-8")
    requirements, unqualified_requirements = parse_requirements(
        requirements_text, prefix
    )
    tasks, unqualified_refs = parse_tasks(tasks_text, prefix)

    if unqualified_requirements:
        errors.append(
            "requisitos sem prefixo: {}".format(
                ", ".join(sorted(unqualified_requirements))
            )
        )
    if unqualified_refs:
        errors.append(
            "referências de task sem prefixo: {}".format(
                ", ".join(sorted(unqualified_refs))
            )
        )
    if not requirements:
        errors.append("nenhum requisito qualificado encontrado")
    if not tasks:
        errors.append("nenhuma task qualificada encontrada")

    referenced = set()
    for task_id, task in tasks.items():
        if not task["requirements"]:
            errors.append("{} não referencia requisito".format(task_id))
        referenced.update(task["requirements"])
        unknown = task["requirements"] - requirements
        if unknown:
            errors.append(
                "{} referencia requisito inexistente: {}".format(
                    task_id, ", ".join(sorted(unknown))
                )
            )
    without_task = requirements - referenced
    if without_task:
        errors.append(
            "requisitos sem task: {}".format(", ".join(sorted(without_task)))
        )

    current_status = status.get("status")
    if current_status in APPROVAL_REQUIRED:
        errors.extend(approval_errors(root, feature_id, status))
    if current_status in REVIEW_REQUIRED:
        unchecked = [
            task_id for task_id, task in tasks.items() if not task["checked"]
        ]
        if unchecked:
            errors.append(
                "tasks não concluídas: {}".format(", ".join(sorted(unchecked)))
            )
        uncovered = requirements - coverage_markers(root, prefix)
        if uncovered:
            errors.append(
                "requisitos sem @covers: {}".format(
                    ", ".join(sorted(uncovered))
                )
            )
    if current_status in {"verified", "done"}:
        errors.extend(review_errors(root, feature_id, status))
    return errors


def approve_feature(root, feature_id, approved_by):
    if not approved_by.strip():
        raise ValueError("identidade do aprovador não pode ser vazia")
    path = feature_dir(root, feature_id) / "status.json"
    status = read_json(path)
    if status.get("status") not in {
        "awaiting_approval",
        "changes_requested",
    }:
        raise ValueError(
            "feature deve estar em awaiting_approval ou changes_requested"
        )
    errors = [
        error
        for error in validate_feature(root, feature_id)
        if "aprovação" not in error and not error.startswith("approval.")
    ]
    if errors:
        raise ValueError("; ".join(errors))
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    status["status"] = "approved"
    status["updated"] = now[:10]
    status["approval"] = {
        "status": "approved",
        "approvedBy": approved_by.strip(),
        "approvedAt": now,
        "specRevision": spec_digest(root, feature_id),
    }
    status["reviews"] = {
        "qa": {"status": "pending", "report": None},
        "traceability": {"status": "pending", "report": None},
    }
    write_json(path, status)


def command_guard(args):
    if str(args.enforce).lower() == "false":
        return 0
    try:
        payload = json.load(sys.stdin)
    except ValueError as error:
        print("SDD: payload JSON inválido: {}.".format(error), file=sys.stderr)
        return 2
    allowed, message = guard(payload, args.root)
    if not allowed:
        print("🚫 " + message, file=sys.stderr)
        return 2
    return 0


def command_validate(args):
    errors = validate_feature(args.root, args.feature)
    if errors:
        print("❌ SDD inválido — {}".format(args.feature))
        for error in errors:
            print("- " + error)
        return 1
    print("✅ SDD válido — {}".format(args.feature))
    return 0


def command_digest(args):
    print(spec_digest(args.root, args.feature))
    return 0


def command_approve(args):
    try:
        approve_feature(args.root, args.feature, args.approved_by)
    except (OSError, ValueError) as error:
        print("❌ Aprovação não registrada: {}".format(error), file=sys.stderr)
        return 1
    print("✅ Spec aprovada e vinculada ao digest atual — {}".format(args.feature))
    return 0


def read_harness_config(root):
    path = root / ".sdd" / "config.json"
    if not path.is_file():
        return {}
    return read_json(path)


def load_session_manager(root):
    module_path = root / ".claude" / "knowledge" / "session_manager.py"
    if not module_path.is_file():
        raise FileNotFoundError(str(module_path))
    spec = importlib.util.spec_from_file_location("session_manager", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SessionManager(root, read_harness_config(root))


def command_session_bootstrap(args):
    try:
        manager = load_session_manager(args.root)
    except OSError as error:
        print("❌ Session bootstrap falhou: {}".format(error), file=sys.stderr)
        return 1
    if not manager.enabled:
        print("Session memory desabilitada (sessionMemory.enabled=false).")
        return 0
    metadata = manager.bootstrap()
    archived = manager.checkpoint_all(force=False)
    if archived:
        print("Checkpoint automatico — {} arquivo(s) arquivados.".format(len(archived)))
    print("OK Session bootstrap — {}".format(metadata.get("sessionId", "(unknown)")))
    return 0


def command_session_status(args):
    try:
        manager = load_session_manager(args.root)
    except OSError as error:
        print("❌ Session status falhou: {}".format(error), file=sys.stderr)
        return 1
    print(manager.status_report())
    return 0


def command_session_checkpoint(args):
    try:
        manager = load_session_manager(args.root)
    except OSError as error:
        print("❌ Session checkpoint falhou: {}".format(error), file=sys.stderr)
        return 1
    if not manager.enabled:
        print("Session memory desabilitada.")
        return 0
    manager.bootstrap()
    archived = manager.checkpoint_all(force=args.force)
    if not archived:
        print("Nenhum checkpoint necessário (limiar não atingido).")
        return 0
    print("Checkpoint — arquivos arquivados:")
    for path in archived:
        print("- " + path)
    return 0


def command_session_context(args):
    try:
        manager = load_session_manager(args.root)
    except OSError as error:
        print("❌ Session context falhou: {}".format(error), file=sys.stderr)
        return 1
    if not manager.enabled:
        return 0
    manager.bootstrap()
    print(manager.get_merged_context(args.feature))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Controles determinísticos SDD")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command", required=True)

    guard_parser = subparsers.add_parser("guard")
    guard_parser.add_argument("--enforce", default="true")
    guard_parser.set_defaults(handler=command_guard)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("feature")
    validate_parser.set_defaults(handler=command_validate)

    digest_parser = subparsers.add_parser("digest")
    digest_parser.add_argument("feature")
    digest_parser.set_defaults(handler=command_digest)

    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("feature")
    approve_parser.add_argument("--by", dest="approved_by", required=True)
    approve_parser.set_defaults(handler=command_approve)

    session_parser = subparsers.add_parser("session")
    session_sub = session_parser.add_subparsers(dest="session_command", required=True)

    bootstrap_parser = session_sub.add_parser("bootstrap")
    bootstrap_parser.set_defaults(handler=command_session_bootstrap)

    status_parser = session_sub.add_parser("status")
    status_parser.set_defaults(handler=command_session_status)

    checkpoint_parser = session_sub.add_parser("checkpoint")
    checkpoint_parser.add_argument(
        "--force", action="store_true", help="arquiva mesmo abaixo do limiar"
    )
    checkpoint_parser.set_defaults(handler=command_session_checkpoint)

    context_parser = session_sub.add_parser("context")
    context_parser.add_argument("--feature", default=None)
    context_parser.set_defaults(handler=command_session_context)
    return parser


def main():
    args = build_parser().parse_args()
    args.root = args.root.resolve(strict=False)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
