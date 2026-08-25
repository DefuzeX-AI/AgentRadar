#!/usr/bin/env python3
"""Discover and lightly scan public Python projects that use LangGraph."""

from __future__ import annotations

import argparse
import ast
import base64
import configparser
import csv
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import time
import tomllib
from typing import Any, Iterable
import warnings
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"
ANALYZER_VERSION = 1
DEFAULT_QUERY = (
    'langgraph agent in:name,description,readme language:Python '
    "archived:false fork:false"
)
MAX_ARCHIVE_BYTES = 50 * 1024 * 1024
MAX_SOURCE_FILE_BYTES = 1 * 1024 * 1024
MAX_SELECTED_SOURCE_BYTES = 25 * 1024 * 1024
MANIFEST_NAMES = {
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
}
TEXT_NAMES = {
    "readme",
    "readme.md",
    "readme.rst",
    ".env",
    ".env.example",
    ".env.sample",
}
IGNORED_PATH_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "site-packages",
    "vendor",
}
TUTORIAL_PATH_PARTS = {
    "cookbook",
    "docs",
    "example",
    "examples",
    "notebook",
    "notebooks",
    "tutorial",
    "tutorials",
}
IGNORED_SECRET_NAMES = {
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "LANGCHAIN_API_KEY",
    "LANGSMITH_API_KEY",
}
KNOWN_FRAMEWORK_REPOSITORIES = {
    "langchain-ai/langchain",
    "langchain-ai/langgraph",
}
API_SECRET_PATTERN = re.compile(
    r"\b[A-Z][A-Z0-9_]*(?:API_KEY|ACCESS_TOKEN|SECRET_KEY)\b"
)
REQUIREMENT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*")


class ScanError(RuntimeError):
    """A recoverable repository scan failure."""


def normalize_package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def leaf_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def is_requirement_name(value: str) -> str | None:
    value = value.strip()
    if not value or value.startswith(("#", "-", "git+", "http://", "https://")):
        return None
    match = REQUIREMENT_NAME_PATTERN.match(value)
    if not match:
        return None
    return normalize_package_name(match.group(0))


def token_from_environment() -> str | None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token.strip()
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


class GitHubClient:
    def __init__(self, token: str | None) -> None:
        self.token = token

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "AgentRadar/0.1",
            "X-GitHub-Api-Version": API_VERSION,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, url: str, *, max_bytes: int | None = None) -> bytes:
        for attempt in range(3):
            request = Request(url, headers=self._headers())
            try:
                with urlopen(request, timeout=45) as response:
                    if max_bytes is None:
                        return response.read()
                    data = response.read(max_bytes + 1)
                    if len(data) > max_bytes:
                        raise ScanError(f"download exceeds {max_bytes} bytes")
                    return data
            except HTTPError as exc:
                if exc.code not in {403, 429} or attempt == 2:
                    raise ScanError(f"GitHub HTTP {exc.code}: {url}") from exc
                retry_after = int(exc.headers.get("Retry-After", "0") or 0)
                reset_at = int(exc.headers.get("X-RateLimit-Reset", "0") or 0)
                delay = retry_after or max(1, reset_at - int(time.time()))
                if delay > 60:
                    raise ScanError("GitHub rate limit requires a wait longer than 60 seconds")
                time.sleep(delay)
            except URLError as exc:
                if attempt == 2:
                    raise ScanError(f"GitHub request failed: {exc.reason}") from exc
                time.sleep(2**attempt)
        raise AssertionError("request retry loop exhausted")

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        query = f"?{urlencode(params)}" if params else ""
        data = self._request(f"{API_ROOT}{path}{query}")
        return json.loads(data)

    def discover(self, query: str, limit: int) -> list[dict[str, Any]]:
        repositories: list[dict[str, Any]] = []
        page = 1
        while len(repositories) < limit:
            per_page = min(100, limit - len(repositories))
            payload = self.get_json(
                "/search/repositories",
                {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": per_page,
                    "page": page,
                },
            )
            items = payload.get("items", [])
            if not items:
                break
            repositories.extend(items)
            page += 1
        return repositories[:limit]

    def head_sha(self, full_name: str, default_branch: str) -> str:
        branch = quote(default_branch, safe="")
        payload = self.get_json(f"/repos/{full_name}/commits/{branch}")
        return str(payload["sha"])

    def archive(self, full_name: str, sha: str) -> bytes:
        return self._request(
            f"{API_ROOT}/repos/{full_name}/tarball/{sha}",
            max_bytes=MAX_ARCHIVE_BYTES,
        )

    def readme(self, full_name: str, sha: str) -> str:
        payload = self.get_json(f"/repos/{full_name}/readme", {"ref": sha})
        if payload.get("encoding") != "base64" or not payload.get("content"):
            raise ScanError("README content is unavailable")
        try:
            content = base64.b64decode(payload["content"])
        except (ValueError, TypeError) as exc:
            raise ScanError("README content is invalid") from exc
        return content.decode("utf-8", errors="replace")


def wanted_archive_path(path: PurePosixPath) -> bool:
    if any(part.lower() in IGNORED_PATH_PARTS for part in path.parts):
        return False
    name = path.name.lower()
    return (
        path.suffix.lower() == ".py"
        or name in MANIFEST_NAMES
        or name in TEXT_NAMES
        or (name.startswith("requirements") and name.endswith(".txt"))
    )


def parse_python(content: str, path: str) -> ast.Module:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(content, filename=path)


def read_archive_files(archive: bytes) -> dict[str, str]:
    files: dict[str, str] = {}
    selected_bytes = 0
    try:
        tar = tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz")
    except tarfile.TarError as exc:
        raise ScanError("invalid repository tarball") from exc
    with tar:
        for member in tar:
            if not member.isfile() or member.size > MAX_SOURCE_FILE_BYTES:
                continue
            parts = PurePosixPath(member.name).parts
            if len(parts) < 2:
                continue
            relative = PurePosixPath(*parts[1:])
            if not wanted_archive_path(relative):
                continue
            selected_bytes += member.size
            if selected_bytes > MAX_SELECTED_SOURCE_BYTES:
                raise ScanError("selected source exceeds scan size limit")
            extracted = tar.extractfile(member)
            if extracted is None:
                continue
            files[str(relative)] = extracted.read().decode("utf-8", errors="replace")
    return files


def dependencies_from_pyproject(content: str) -> set[str]:
    dependencies: set[str] = set()
    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError:
        return dependencies

    project = data.get("project", {})
    for item in project.get("dependencies", []) or []:
        if isinstance(item, str) and (name := is_requirement_name(item)):
            dependencies.add(name)
    for items in (project.get("optional-dependencies", {}) or {}).values():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, str) and (name := is_requirement_name(item)):
                dependencies.add(name)

    poetry_dependencies = (
        data.get("tool", {}).get("poetry", {}).get("dependencies", {}) or {}
    )
    for name in poetry_dependencies:
        normalized = normalize_package_name(name)
        if normalized != "python":
            dependencies.add(normalized)
    return dependencies


def dependencies_from_setup_py(content: str) -> set[str]:
    dependencies: set[str] = set()
    try:
        tree = parse_python(content, "setup.py")
    except SyntaxError:
        return dependencies
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or leaf_name(node.func) != "setup":
            continue
        for keyword in node.keywords:
            if keyword.arg not in {"install_requires", "extras_require"}:
                continue
            for child in ast.walk(keyword.value):
                if (value := literal_string(child)) and (name := is_requirement_name(value)):
                    dependencies.add(name)
    return dependencies


def dependencies_from_setup_cfg(content: str) -> set[str]:
    dependencies: set[str] = set()
    parser = configparser.ConfigParser()
    try:
        parser.read_string(content)
    except configparser.Error:
        return dependencies
    for section in parser.sections():
        if not section.startswith("options"):
            continue
        for key, value in parser.items(section):
            if key not in {"install_requires", "extras_require"}:
                continue
            for line in value.splitlines():
                if name := is_requirement_name(line):
                    dependencies.add(name)
    return dependencies


def collect_dependencies(files: dict[str, str]) -> set[str]:
    dependencies: set[str] = set()
    for path, content in files.items():
        name = PurePosixPath(path).name.lower()
        if name == "pyproject.toml":
            dependencies.update(dependencies_from_pyproject(content))
        elif name == "setup.py":
            dependencies.update(dependencies_from_setup_py(content))
        elif name == "setup.cfg":
            dependencies.update(dependencies_from_setup_cfg(content))
        elif name.startswith("requirements") and name.endswith(".txt"):
            for line in content.splitlines():
                if dependency := is_requirement_name(line):
                    dependencies.add(dependency)
    return dependencies


class PythonFactsVisitor(ast.NodeVisitor):
    def __init__(self, path: str, agent_vars: set[str], compiled_vars: set[str]) -> None:
        self.path = path
        self.agent_vars = agent_vars
        self.compiled_vars = compiled_vars
        self.dynamic_depth = 0
        self.imports: set[str] = set()
        self.langgraph_import_lines: list[int] = []
        self.nodes: list[dict[str, Any]] = []
        self.nodes_dynamic_unknown = False
        self.conditional_edges = 0
        self.agent_factory_count = 0
        self.subagents: set[str] = set()
        self.subagents_unknown = False
        self.subgraphs: set[str] = set()
        self.environment_secrets: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            self.imports.add(root)
            self.imports.add(alias.name)
            if alias.name == "langgraph" or alias.name.startswith("langgraph."):
                self.langgraph_import_lines.append(node.lineno)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        if node.module:
            self.imports.add(node.module.split(".", 1)[0])
            self.imports.add(node.module)
            if node.module == "langgraph" or node.module.startswith("langgraph."):
                self.langgraph_import_lines.append(node.lineno)

    def _visit_dynamic_block(self, node: ast.AST) -> None:
        self.dynamic_depth += 1
        self.generic_visit(node)
        self.dynamic_depth -= 1

    def visit_For(self, node: ast.For) -> None:  # noqa: N802
        self._visit_dynamic_block(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:  # noqa: N802
        self._visit_dynamic_block(node)

    def visit_While(self, node: ast.While) -> None:  # noqa: N802
        self._visit_dynamic_block(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        function_name = leaf_name(node.func)
        if function_name == "add_node":
            self._record_node(node)
        elif function_name == "add_conditional_edges":
            self.conditional_edges += 1
        elif function_name == "create_react_agent":
            self.agent_factory_count += 1
        elif function_name in {"create_supervisor", "create_swarm"}:
            self._record_supervisor_agents(node)
        if function_name in {"getenv", "get"} and node.args:
            self._record_secret(literal_string(node.args[0]))
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:  # noqa: N802
        if isinstance(node.value, ast.Attribute) and node.value.attr == "environ":
            self._record_secret(literal_string(node.slice))
        self.generic_visit(node)

    def _record_secret(self, value: str | None) -> None:
        if value and API_SECRET_PATTERN.fullmatch(value) and value not in IGNORED_SECRET_NAMES:
            self.environment_secrets.add(value)

    def _record_node(self, node: ast.Call) -> None:
        if self.dynamic_depth:
            self.nodes_dynamic_unknown = True
            return
        label_node = node.args[0] if node.args else None
        label = literal_string(label_node) if label_node else None
        if label is None and isinstance(label_node, (ast.Name, ast.Attribute)):
            label = leaf_name(label_node)
        if label is None:
            self.nodes_dynamic_unknown = True
            return
        self.nodes.append({"name": label, "path": self.path, "line": node.lineno})

        handler: ast.AST | None = None
        if len(node.args) >= 2:
            handler = node.args[1]
        elif len(node.args) == 1:
            handler = node.args[0]
        handler_name = leaf_name(handler) if handler else None
        if handler_name in self.agent_vars:
            self.subagents.add(handler_name)
        elif handler_name in self.compiled_vars:
            self.subgraphs.add(handler_name)

    def _record_supervisor_agents(self, node: ast.Call) -> None:
        if not node.args or not isinstance(node.args[0], (ast.List, ast.Tuple, ast.Set)):
            self.subagents_unknown = True
            return
        for element in node.args[0].elts:
            if name := leaf_name(element):
                self.subagents.add(name)
            else:
                self.subagents_unknown = True


def assigned_factories(tree: ast.AST) -> tuple[set[str], set[str]]:
    agent_vars: set[str] = set()
    compiled_vars: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not isinstance(value, ast.Call):
            continue
        targets: Iterable[ast.AST]
        if isinstance(node, ast.Assign):
            targets = node.targets
        else:
            targets = [node.target]
        names = {target.id for target in targets if isinstance(target, ast.Name)}
        function_name = leaf_name(value.func)
        if function_name == "create_react_agent":
            agent_vars.update(names)
        elif function_name == "compile":
            compiled_vars.update(names)
    return agent_vars, compiled_vars


def referenced_state_fields(tree: ast.AST) -> set[str]:
    schemas: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        base_names = {leaf_name(base) for base in node.bases}
        if not base_names.intersection({"TypedDict", "BaseModel"}):
            continue
        fields = {
            child.target.id
            for child in node.body
            if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name)
        }
        schemas[node.name] = fields

    referenced: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or leaf_name(node.func) not in {
            "StateGraph",
            "MessageGraph",
        }:
            continue
        if node.args and isinstance(node.args[0], ast.Name):
            referenced.update(schemas.get(node.args[0].id, set()))
    return referenced


def analyze_python(files: dict[str, str]) -> dict[str, Any]:
    imports: set[str] = set()
    langgraph_evidence: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    state_fields: set[str] = set()
    subagents: set[str] = set()
    subgraphs: set[str] = set()
    environment_secrets: set[str] = set()
    nodes_dynamic_unknown = False
    subagents_unknown = False
    conditional_edges = 0
    agent_factory_count = 0

    for path, content in files.items():
        if not path.endswith(".py"):
            continue
        try:
            tree = parse_python(content, path)
        except (SyntaxError, ValueError):
            continue
        agent_vars, compiled_vars = assigned_factories(tree)
        visitor = PythonFactsVisitor(path, agent_vars, compiled_vars)
        visitor.visit(tree)
        imports.update(visitor.imports)
        nodes.extend(visitor.nodes)
        state_fields.update(referenced_state_fields(tree))
        subagents.update(visitor.subagents)
        subgraphs.update(visitor.subgraphs)
        environment_secrets.update(visitor.environment_secrets)
        nodes_dynamic_unknown |= visitor.nodes_dynamic_unknown
        subagents_unknown |= visitor.subagents_unknown
        conditional_edges += visitor.conditional_edges
        agent_factory_count += visitor.agent_factory_count
        langgraph_evidence.extend(
            {"type": "import", "path": path, "line": line}
            for line in visitor.langgraph_import_lines
        )

    return {
        "imports": imports,
        "langgraph_evidence": langgraph_evidence,
        "nodes": nodes,
        "nodes_dynamic_unknown": nodes_dynamic_unknown,
        "conditional_edges": conditional_edges,
        "agent_factory_count": agent_factory_count,
        "subagents": subagents,
        "subagents_unknown": subagents_unknown,
        "subgraphs": subgraphs,
        "environment_secrets": environment_secrets,
        "state_fields": state_fields,
    }


def environment_secrets_from_files(files: dict[str, str]) -> set[str]:
    secrets: set[str] = set()
    for path, content in files.items():
        if not PurePosixPath(path).name.lower().startswith(".env"):
            continue
        for secret in API_SECRET_PATTERN.findall(content):
            if secret not in IGNORED_SECRET_NAMES:
                secrets.add(secret)
    return secrets


def load_providers(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {provider["id"]: provider for provider in payload["providers"]}


def detect_external_apis(
    dependencies: set[str],
    imports: set[str],
    secrets: set[str],
    providers: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    confirmed: list[dict[str, Any]] = []
    matched_secrets: set[str] = set()
    for provider_id, provider in providers.items():
        provider_dependencies = {
            normalize_package_name(value) for value in provider.get("packages", [])
        }
        provider_imports = set(provider.get("imports", []))
        provider_secrets = set(provider.get("environment_variables", []))
        evidence: list[str] = []
        if dependencies.intersection(provider_dependencies):
            evidence.append("dependency")
        if imports.intersection(provider_imports):
            evidence.append("import")
        secret_matches = secrets.intersection(provider_secrets)
        if secret_matches:
            evidence.append("environment_variable")
            matched_secrets.update(secret_matches)
        if evidence:
            confirmed.append(
                {
                    "provider": provider_id,
                    "access_model": provider.get("access_model", "unknown"),
                    "evidence": evidence,
                }
            )
    unknown = sorted(secrets - matched_secrets)
    return sorted(confirmed, key=lambda item: item["provider"]), unknown


DIRECTION_RULES: dict[str, set[str]] = {
    "browser_automation": {"playwright", "selenium", "browser-use", "browser_use"},
    "coding_agent": {"coding agent", "code agent", "software engineering agent"},
    "data_sql": {"sqlalchemy", "sql agent", "database agent", "psycopg"},
    "finance": {"financial agent", "stock trading", "trading agent"},
    "multi_agent": {"multi-agent", "multi agent", "supervisor", "swarm"},
    "rag_knowledge": {"chromadb", "qdrant", "weaviate", "faiss", "rag"},
    "research_agent": {"research agent", "deep research", "tavily", "exa-py"},
}


def infer_direction(
    repository: dict[str, Any],
    files: dict[str, str],
    dependencies: set[str],
    imports: set[str],
) -> str:
    readme = " ".join(
        content[:50_000]
        for path, content in files.items()
        if PurePosixPath(path).name.lower().startswith("readme")
    )
    text = " ".join(
        [
            repository.get("name") or "",
            repository.get("description") or "",
            readme,
            " ".join(dependencies),
            " ".join(imports),
        ]
    ).lower()
    scores = {
        direction: sum(
            1
            for term in terms
            if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text)
        )
        for direction, terms in DIRECTION_RULES.items()
    }
    best_direction, best_score = max(scores.items(), key=lambda item: item[1])
    return best_direction if best_score else "unknown"


def is_tutorial_only(
    repository: dict[str, Any], langgraph_paths: Iterable[str]
) -> bool:
    paths = list(langgraph_paths)
    if not paths:
        return False
    all_in_tutorial_paths = all(
        any(part.lower() in TUTORIAL_PATH_PARTS for part in PurePosixPath(path).parts)
        for path in paths
    )
    identity = f"{repository.get('name', '')} {repository.get('description', '')}".lower()
    if any(term in identity for term in {"course", "workshop", "cookbook"}):
        return True
    tutorial_identity = any(
        term in identity for term in {"tutorial"}
    )
    return all_in_tutorial_paths and tutorial_identity


def classify_project_kind(repository: dict[str, Any]) -> str:
    full_name = repository.get("full_name", "")
    if full_name in KNOWN_FRAMEWORK_REPOSITORIES:
        return "framework_or_library"
    identity = f"{repository.get('name', '')} {repository.get('description', '')}".lower()
    if any(
        term in identity
        for term in {"awesome", "collection of", "list of", "500-ai-agents-projects"}
    ):
        return "collection"
    if "agent" in identity:
        return "agent_project"
    return "unknown"


def analyze_repository(
    repository: dict[str, Any],
    files: dict[str, str],
    providers: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    dependencies = collect_dependencies(files)
    python = analyze_python(files)
    langgraph_dependency = "langgraph" in dependencies
    if python["langgraph_evidence"]:
        langgraph_status = "confirmed"
    elif langgraph_dependency:
        langgraph_status = "probable"
    elif any("langgraph" in content.lower() for content in files.values()):
        langgraph_status = "unknown"
    else:
        langgraph_status = "not_langgraph"

    confirmed_apis, unknown_apis = detect_external_apis(
        dependencies,
        python["imports"],
        python["environment_secrets"] | environment_secrets_from_files(files),
        providers,
    )
    langgraph_paths = {
        evidence["path"] for evidence in python["langgraph_evidence"]
    }
    return {
        "langgraph_status": langgraph_status,
        "langgraph_evidence": python["langgraph_evidence"],
        "langgraph_dependency": langgraph_dependency,
        "tutorial_only": is_tutorial_only(repository, langgraph_paths),
        "project_kind": classify_project_kind(repository),
        "direction": infer_direction(
            repository, files, dependencies, python["imports"]
        ),
        "direct_dependency_count": len(dependencies),
        "direct_dependencies": sorted(dependencies),
        "external_apis_confirmed": confirmed_apis,
        "external_apis_unknown": unknown_apis,
        "nodes_confirmed": len(python["nodes"]),
        "node_names_confirmed": [node["name"] for node in python["nodes"]],
        "nodes_dynamic_unknown": python["nodes_dynamic_unknown"],
        "conditional_edges_confirmed": python["conditional_edges"],
        "state_fields_confirmed": len(python["state_fields"]),
        "state_field_names_confirmed": sorted(python["state_fields"]),
        "agent_factories_confirmed": python["agent_factory_count"],
        "subagents_confirmed": len(python["subagents"]),
        "subagent_names_confirmed": sorted(python["subagents"]),
        "subagents_unknown": True,
        "subgraphs_confirmed": len(python["subgraphs"]),
        "state_fields_unknown": True,
    }


def repository_metadata(repository: dict[str, Any], sha: str) -> dict[str, Any]:
    license_payload = repository.get("license") or {}
    return {
        "repo": repository["full_name"],
        "url": repository["html_url"],
        "description": repository.get("description"),
        "github_stars": repository.get("stargazers_count", 0),
        "github_forks": repository.get("forks_count", 0),
        "primary_language": repository.get("language"),
        "license": license_payload.get("spdx_id"),
        "last_push": repository.get("pushed_at"),
        "head_sha": sha,
    }


def write_catalog(output_dir: Path, catalog: list[dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "catalog.json"
    json_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    csv_path = output_dir / "catalog.csv"
    fieldnames = (
        list(dict.fromkeys(key for row in catalog for key in row))
        if catalog
        else ["repo", "github_stars"]
    )
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in catalog:
            writer.writerow(
                {
                    key: json.dumps(value, ensure_ascii=False)
                    if isinstance(value, (list, dict))
                    else value
                    for key, value in row.items()
                }
            )


def write_provider_candidates(
    output_dir: Path, catalog: list[dict[str, Any]]
) -> None:
    candidates: dict[str, set[str]] = {}
    for row in catalog:
        for secret in row["external_apis_unknown"]:
            candidates.setdefault(secret, set()).add(row["repo"])
    payload = [
        {"signal": signal, "repositories": sorted(repositories)}
        for signal, repositories in sorted(candidates.items())
    ]
    (output_dir / "provider_candidates.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_scan_cache(output_dir: Path) -> dict[str, dict[str, Any]]:
    path = output_dir / "scan_cache.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def write_scan_cache(
    output_dir: Path, cache: dict[str, dict[str, Any]]
) -> None:
    (output_dir / "scan_cache.json").write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_seen_repositories(output_dir: Path) -> dict[str, dict[str, Any]]:
    path = output_dir / "repositories_seen.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(payload, list):
        return {}
    return {
        item["repo"]: item
        for item in payload
        if isinstance(item, dict) and isinstance(item.get("repo"), str)
    }


def record_seen_repository(
    seen: dict[str, dict[str, Any]],
    repository: dict[str, Any],
    status: str,
    *,
    detail: str | None = None,
    observed_at: str | None = None,
) -> None:
    repo = repository["full_name"]
    now = observed_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    first_seen = seen.get(repo, {}).get("first_seen", now)
    seen[repo] = {
        "repo": repo,
        "url": repository["html_url"],
        "github_stars": repository.get("stargazers_count", 0),
        "first_seen": first_seen,
        "last_seen": now,
        "scan_status": status,
        "detail": detail,
    }


def write_seen_repositories(
    output_dir: Path, seen: dict[str, dict[str, Any]]
) -> None:
    payload = sorted(
        seen.values(), key=lambda item: (-item["github_stars"], item["repo"].lower())
    )
    (output_dir / "repositories_seen.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def checkpoint_scan_state(
    output_dir: Path,
    cache: dict[str, dict[str, Any]],
    seen: dict[str, dict[str, Any]],
) -> None:
    """Persist completed repository scans before moving to the next candidate."""
    write_scan_cache(output_dir, cache)
    write_seen_repositories(output_dir, seen)


def load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def select_review_candidates(
    catalog: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    reviewed = {
        (review.get("repo"), review.get("reviewed_sha")) for review in reviews
    }
    return [
        row
        for row in catalog
        if (row.get("repo"), row.get("head_sha")) not in reviewed
    ][:limit]


def attach_agent_reviews(
    catalog: list[dict[str, Any]], reviews: list[dict[str, Any]]
) -> None:
    by_revision = {
        (review.get("repo"), review.get("reviewed_sha")): review
        for review in reviews
    }
    for row in catalog:
        review = by_revision.get((row.get("repo"), row.get("head_sha")))
        if review:
            row["host_review"] = review


def prepare_review(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    catalog = load_json_list(output_dir / "catalog.json")
    reviews = load_json_list(output_dir / "agent_reviews.json")
    candidates = select_review_candidates(catalog, reviews, args.limit)
    client = GitHubClient(token_from_environment())
    queue: list[dict[str, Any]] = []

    for index, row in enumerate(candidates, start=1):
        print(f"[{index}/{len(candidates)}] reading README {row['repo']}", file=sys.stderr)
        try:
            readme = client.readme(row["repo"], row["head_sha"])
            readme_status = "available"
        except ScanError as exc:
            readme = ""
            readme_status = str(exc)
        queue.append(
            {
                "repo": row["repo"],
                "url": row["url"],
                "github_stars": row["github_stars"],
                "license": row.get("license"),
                "head_sha": row["head_sha"],
                "langgraph_status": row["langgraph_status"],
                "static_direction": row.get("direction", "unknown"),
                "readme_status": readme_status,
                "readme_excerpt": readme[: args.max_readme_chars],
                "readme_truncated": len(readme) > args.max_readme_chars,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "review_queue.json").write_text(
        json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(queue)} README review candidates", file=sys.stderr)
    return 0


def scan(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parent
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cache = load_scan_cache(output_dir)
    seen = load_seen_repositories(output_dir)
    providers = load_providers(root / "providers.json")
    client = GitHubClient(token_from_environment())
    repositories = client.discover(args.query, args.limit)
    catalog: list[dict[str, Any]] = []
    failures: list[str] = []
    counts = {
        "probable": 0,
        "unknown": 0,
        "not_langgraph": 0,
        "tutorial": 0,
        "non_agent": 0,
    }

    for index, repository in enumerate(repositories, start=1):
        full_name = repository["full_name"]
        if repository.get("fork") or repository.get("archived"):
            record_seen_repository(seen, repository, "excluded_fork_or_archived")
            checkpoint_scan_state(output_dir, cache, seen)
            continue
        print(f"[{index}/{len(repositories)}] scanning {full_name}", file=sys.stderr)
        try:
            cached = cache.get(full_name)
            if (
                cached
                and cached.get("analyzer_version") == ANALYZER_VERSION
                and cached.get("pushed_at") == repository.get("pushed_at")
            ):
                if cached.get("scan_error"):
                    raise ScanError(cached["scan_error"])
                sha = cached["head_sha"]
                analysis = cached["analysis"]
            else:
                sha = client.head_sha(full_name, repository["default_branch"])
                files = read_archive_files(client.archive(full_name, sha))
                analysis = analyze_repository(repository, files, providers)
                cache[full_name] = {
                    "analyzer_version": ANALYZER_VERSION,
                    "pushed_at": repository.get("pushed_at"),
                    "head_sha": sha,
                    "analysis": analysis,
                }
            analysis["tutorial_only"] = is_tutorial_only(
                repository,
                {
                    evidence["path"]
                    for evidence in analysis.get("langgraph_evidence", [])
                },
            )
        except ScanError as exc:
            failures.append(f"{full_name}: {exc}")
            cache[full_name] = {
                "analyzer_version": ANALYZER_VERSION,
                "pushed_at": repository.get("pushed_at"),
                "scan_error": str(exc),
            }
            record_seen_repository(seen, repository, "scan_failed", detail=str(exc))
            checkpoint_scan_state(output_dir, cache, seen)
            continue

        if analysis["tutorial_only"]:
            counts["tutorial"] += 1
            record_seen_repository(seen, repository, "excluded_tutorial")
            checkpoint_scan_state(output_dir, cache, seen)
            continue
        if (
            analysis["project_kind"] in {"collection", "framework_or_library"}
            and not args.include_non_agents
        ):
            counts["non_agent"] += 1
            record_seen_repository(
                seen, repository, f"excluded_{analysis['project_kind']}"
            )
            checkpoint_scan_state(output_dir, cache, seen)
            continue
        status = analysis["langgraph_status"]
        if status != "confirmed" and not args.include_probable:
            counts[status] += 1
            record_seen_repository(seen, repository, status)
            checkpoint_scan_state(output_dir, cache, seen)
            continue
        catalog.append(repository_metadata(repository, sha) | analysis)
        record_seen_repository(seen, repository, f"cataloged_{status}")
        checkpoint_scan_state(output_dir, cache, seen)

    catalog.sort(key=lambda row: row["github_stars"], reverse=True)
    attach_agent_reviews(catalog, load_json_list(output_dir / "agent_reviews.json"))
    write_catalog(output_dir, catalog)
    write_provider_candidates(output_dir, catalog)
    write_scan_cache(output_dir, cache)
    write_seen_repositories(output_dir, seen)
    print(
        f"wrote {len(catalog)} projects; skipped "
        f"{counts['probable']} probable, {counts['unknown']} unknown, "
        f"{counts['not_langgraph']} non-LangGraph, {counts['tutorial']} tutorials, "
        f"{counts['non_agent']} obvious non-agent repositories; "
        f"{len(failures)} failures",
        file=sys.stderr,
    )
    for failure in failures:
        print(f"warning: {failure}", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan_parser = subparsers.add_parser("scan", help="discover and scan repositories")
    scan_parser.add_argument("--query", default=DEFAULT_QUERY)
    scan_parser.add_argument("--limit", type=int, default=20)
    scan_parser.add_argument("--output-dir", default="data")
    scan_parser.add_argument(
        "--include-probable",
        action="store_true",
        help="include dependency-only projects in the catalog",
    )
    scan_parser.add_argument(
        "--include-non-agents",
        action="store_true",
        help="include obvious frameworks, libraries, and project collections",
    )
    scan_parser.set_defaults(handler=scan)

    review_parser = subparsers.add_parser(
        "prepare-review", help="prepare a small README queue for host-agent review"
    )
    review_parser.add_argument("--limit", type=int, default=10)
    review_parser.add_argument("--output-dir", default="data")
    review_parser.add_argument("--max-readme-chars", type=int, default=16_000)
    review_parser.set_defaults(handler=prepare_review)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if getattr(args, "limit", 1) < 1:
        parser.error("--limit must be positive")
    if getattr(args, "max_readme_chars", 1) < 1:
        parser.error("--max-readme-chars must be positive")
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
