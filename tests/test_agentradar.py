from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import agentradar


PROVIDERS = {
    "openai": {
        "id": "openai",
        "packages": ["openai", "langchain-openai"],
        "imports": ["openai", "langchain_openai"],
        "environment_variables": ["OPENAI_API_KEY"],
        "access_model": "commercial",
    }
}


def repository(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "name": "sample-agent",
        "description": "A sample agent",
    }
    value.update(overrides)
    return value


class AnalyzeRepositoryTests(unittest.TestCase):
    def test_confirms_import_and_counts_static_graph_parts(self) -> None:
        files = {
            "pyproject.toml": """
[project]
dependencies = ["langgraph>=0.2", "langchain-openai"]
""",
            "src/agent.py": """
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

class State(TypedDict):
    messages: list
    query: str

researcher = create_react_agent(model=ChatOpenAI(), tools=[])
graph = StateGraph(State)
graph.add_node("researcher", researcher)
graph.add_node("finish", lambda state: state)
graph.add_conditional_edges("researcher", lambda state: "finish")
""",
        }

        result = agentradar.analyze_repository(repository(), files, PROVIDERS)

        self.assertEqual(result["langgraph_status"], "confirmed")
        self.assertEqual(result["nodes_confirmed"], 2)
        self.assertEqual(result["subagents_confirmed"], 1)
        self.assertTrue(result["subagents_unknown"])
        self.assertEqual(result["state_fields_confirmed"], 2)
        self.assertEqual(result["conditional_edges_confirmed"], 1)
        self.assertEqual(
            result["external_apis_confirmed"][0]["provider"], "openai"
        )

    def test_dependency_without_import_is_probable(self) -> None:
        files = {
            "requirements.txt": "langgraph==0.3.1\nrequests>=2\n",
            "app.py": "print('no graph here')\n",
        }

        result = agentradar.analyze_repository(repository(), files, PROVIDERS)

        self.assertEqual(result["langgraph_status"], "probable")
        self.assertEqual(result["direct_dependency_count"], 2)

    def test_loop_registration_is_dynamic_not_one_confirmed_node(self) -> None:
        files = {
            "agent.py": """
from langgraph.graph import StateGraph

graph = StateGraph(dict)
for name, handler in configured_nodes:
    graph.add_node(name, handler)
"""
        }

        result = agentradar.analyze_repository(repository(), files, PROVIDERS)

        self.assertEqual(result["nodes_confirmed"], 0)
        self.assertTrue(result["nodes_dynamic_unknown"])

    def test_unknown_api_key_becomes_candidate(self) -> None:
        files = {
            "agent.py": """
import os
from langgraph.graph import StateGraph

key = os.getenv("NEW_SEARCH_API_KEY")
graph = StateGraph(dict)
"""
        }

        result = agentradar.analyze_repository(repository(), files, PROVIDERS)

        self.assertEqual(result["external_apis_unknown"], ["NEW_SEARCH_API_KEY"])

    def test_unrelated_string_does_not_become_api_candidate(self) -> None:
        files = {
            "agent.py": """
from langgraph.graph import StateGraph

documentation = "Set FAKE_API_KEY before running"
graph = StateGraph(dict)
"""
        }

        result = agentradar.analyze_repository(repository(), files, PROVIDERS)

        self.assertEqual(result["external_apis_unknown"], [])

    def test_env_example_becomes_api_candidate(self) -> None:
        files = {
            "agent.py": "from langgraph.graph import StateGraph\n",
            ".env.example": "NEW_SEARCH_API_KEY=\n",
        }

        result = agentradar.analyze_repository(repository(), files, PROVIDERS)

        self.assertEqual(result["external_apis_unknown"], ["NEW_SEARCH_API_KEY"])

    def test_known_api_key_is_not_unknown(self) -> None:
        files = {
            "agent.py": """
import os
from langgraph.graph import StateGraph

key = os.environ["OPENAI_API_KEY"]
graph = StateGraph(dict)
"""
        }

        result = agentradar.analyze_repository(repository(), files, PROVIDERS)

        self.assertEqual(result["external_apis_unknown"], [])
        self.assertEqual(
            result["external_apis_confirmed"][0]["provider"], "openai"
        )

    def test_tutorial_requires_path_and_repository_identity(self) -> None:
        files = {
            "tutorials/lesson.py": """
from langgraph.graph import StateGraph
graph = StateGraph(dict)
"""
        }

        result = agentradar.analyze_repository(
            repository(name="langgraph-tutorial"), files, PROVIDERS
        )

        self.assertTrue(result["tutorial_only"])

    def test_product_source_is_not_excluded_as_tutorial(self) -> None:
        files = {
            "src/agent.py": """
from langgraph.graph import StateGraph
graph = StateGraph(dict)
"""
        }

        result = agentradar.analyze_repository(
            repository(name="agent-with-tutorial-docs"), files, PROVIDERS
        )

        self.assertFalse(result["tutorial_only"])

    def test_explicit_course_repository_is_excluded(self) -> None:
        files = {
            "app/agent.py": """
from langgraph.graph import StateGraph
graph = StateGraph(dict)
"""
        }

        result = agentradar.analyze_repository(
            repository(name="production-agent-course"), files, PROVIDERS
        )

        self.assertTrue(result["tutorial_only"])

    def test_obvious_collection_is_classified_separately(self) -> None:
        value = repository(
            full_name="owner/awesome-agents",
            name="awesome-agents",
            description="A collection of agents",
        )

        self.assertEqual(agentradar.classify_project_kind(value), "collection")

    def test_agent_framework_is_still_an_agent_project(self) -> None:
        value = repository(
            full_name="owner/trading-agents",
            name="TradingAgents",
            description="A multi-agent financial trading framework",
        )

        self.assertEqual(agentradar.classify_project_kind(value), "agent_project")

    def test_seen_repository_preserves_first_seen(self) -> None:
        value = repository(
            full_name="owner/agent",
            html_url="https://github.com/owner/agent",
            stargazers_count=10,
        )
        seen: dict[str, dict[str, object]] = {}

        agentradar.record_seen_repository(
            seen, value, "probable", observed_at="2026-08-24T10:00:00+00:00"
        )
        value["stargazers_count"] = 12
        agentradar.record_seen_repository(
            seen,
            value,
            "cataloged_confirmed",
            observed_at="2026-08-25T10:00:00+00:00",
        )

        self.assertEqual(seen["owner/agent"]["github_stars"], 12)
        self.assertEqual(
            seen["owner/agent"]["first_seen"], "2026-08-24T10:00:00+00:00"
        )
        self.assertEqual(
            seen["owner/agent"]["last_seen"], "2026-08-25T10:00:00+00:00"
        )

    def test_review_queue_skips_same_reviewed_sha(self) -> None:
        catalog = [
            {"repo": "owner/one", "head_sha": "sha-1"},
            {"repo": "owner/two", "head_sha": "sha-2"},
        ]
        reviews = [{"repo": "owner/one", "reviewed_sha": "sha-1"}]

        selected = agentradar.select_review_candidates(catalog, reviews, limit=10)

        self.assertEqual(selected, [{"repo": "owner/two", "head_sha": "sha-2"}])

    def test_review_queue_rechecks_changed_sha(self) -> None:
        catalog = [{"repo": "owner/one", "head_sha": "new-sha"}]
        reviews = [{"repo": "owner/one", "reviewed_sha": "old-sha"}]

        selected = agentradar.select_review_candidates(catalog, reviews, limit=10)

        self.assertEqual(selected, catalog)

    def test_agent_review_attaches_only_to_matching_sha(self) -> None:
        catalog = [
            {"repo": "owner/one", "head_sha": "sha-1"},
            {"repo": "owner/two", "head_sha": "sha-2"},
        ]
        reviews = [
            {
                "repo": "owner/one",
                "reviewed_sha": "sha-1",
                "agent_project": "yes",
            },
            {
                "repo": "owner/two",
                "reviewed_sha": "old-sha",
                "agent_project": "no",
            },
        ]

        agentradar.attach_agent_reviews(catalog, reviews)

        self.assertEqual(catalog[0]["host_review"]["agent_project"], "yes")
        self.assertNotIn("host_review", catalog[1])

    def test_seen_repository_writer_outputs_sorted_list(self) -> None:
        seen = {
            "owner/low": {"repo": "owner/low", "github_stars": 1},
            "owner/high": {"repo": "owner/high", "github_stars": 10},
        }
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)

            agentradar.write_seen_repositories(output_dir, seen)

            payload = json.loads(
                (output_dir / "repositories_seen.json").read_text(encoding="utf-8")
            )
        self.assertEqual([item["repo"] for item in payload], ["owner/high", "owner/low"])

    def test_checkpoint_writes_cache_and_seen_repositories(self) -> None:
        cache = {"owner/agent": {"head_sha": "sha-1"}}
        seen = {
            "owner/agent": {
                "repo": "owner/agent",
                "url": "https://github.com/owner/agent",
                "github_stars": 10,
                "first_seen": "2026-08-24T10:00:00+00:00",
                "last_seen": "2026-08-24T10:00:00+00:00",
                "scan_status": "cataloged_confirmed",
                "detail": None,
            }
        }

        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            agentradar.checkpoint_scan_state(output_dir, cache, seen)
            written_cache = json.loads(
                (output_dir / "scan_cache.json").read_text(encoding="utf-8")
            )
            written_seen = json.loads(
                (output_dir / "repositories_seen.json").read_text(encoding="utf-8")
            )

        self.assertEqual(written_cache, cache)
        self.assertEqual(written_seen[0]["repo"], "owner/agent")


if __name__ == "__main__":
    unittest.main()
