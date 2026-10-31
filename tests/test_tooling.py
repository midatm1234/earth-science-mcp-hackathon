"""Tests for the repository tooling in scripts/. No network, no Claude."""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import client_config  # noqa: E402
import install_skills  # noqa: E402
import new_contribution  # noqa: E402
import package  # noqa: E402
import validate_repo as vr  # noqa: E402

import catalog  # noqa: E402


def _repo_copy(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    ignore = shutil.ignore_patterns("__pycache__", ".pytest_cache", ".ruff_cache", "dist", "verification", ".claude",
                                    ".venv", ".git")
    shutil.copytree(REPO, root, ignore=ignore)
    return root


def test_real_repository_passes_validation():
    rep = vr.run(REPO)
    assert rep.errors == []


def test_skill_validator_catches_spec_violations(tmp_path):
    skill = tmp_path / "Bad_Skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: Bad_Skill\ndescription: Helps.\nmetadata:\n  version: 1\n---\n# x\n")
    errs = " ".join(vr.validate_skill(skill))
    assert "lowercase" in errs
    assert "Use when" in errs
    assert "metadata must map" in errs
    assert "missing section '## Procedure'" in errs


def test_real_skills_are_valid():
    for name in ("obs-model-comparison", "earth-data-discovery"):
        assert vr.validate_skill(REPO / "skills" / name) == []


def test_dependency_pins_must_be_exact_and_match_lock(tmp_path):
    (tmp_path / "servers" / "x").mkdir(parents=True)
    (tmp_path / "uv.lock").write_text('version = 1\n[[package]]\nname = "mcp"\nversion = "2.3.0"\n')
    (tmp_path / "servers" / "x" / "requirements.txt").write_text("mcp==2.2.0\nhttpx>=0.27\n-e .\n")
    rep = vr.Report()
    vr.check_deps(tmp_path, rep)
    text = " ".join(rep.errors)
    assert "differs from uv.lock" in text
    assert "pin an exact version" in text
    assert "editable" in text


def test_secret_scan_and_env_files(tmp_path):
    (tmp_path / "server.py").write_text('API_KEY = "sk-ant-abcdefghijklmnopqrstuvwxyz123456"\n')  # secret-scan: ignore
    (tmp_path / ".env").write_text("TOKEN=abc\n")
    (tmp_path / "ok.py").write_text('api_key = os.environ["MY_API_KEY"]\n')
    rep = vr.Report()
    vr.check_secrets(tmp_path, rep)
    text = " ".join(rep.errors)
    assert "server.py:1" in text
    assert ".env: environment files" in text
    assert "ok.py" not in text


def test_link_checker_finds_broken_files_and_anchors(tmp_path):
    (tmp_path / "a.md").write_text("# Title\n\n## Real section\n\n[ok](b.md#other) [bad](missing.md) [anchor](#nope) "
                                   "[fine](#real-section) `[code](ignored.md)`\n")
    (tmp_path / "b.md").write_text("# Other\n")
    rep = vr.Report()
    vr.check_links(tmp_path, rep)
    text = " ".join(rep.errors)
    assert "missing.md" in text
    assert "#nope" in text
    assert "#other" not in text and "real-section" not in text and "ignored.md" not in text


def test_catalog_status_rules(tmp_path):
    root = _repo_copy(tmp_path)
    entry = root / "catalog" / "entries" / "obs-model-starter.yaml"
    text = entry.read_text()
    entry.write_text(text.replace("status: not-hosted\n    endpoint: TBD", "status: hosted\n    endpoint: TBD")
                         .replace("peer_testing: []", "peer_testing:\n    - {report: catalog/peer-tests/none.md, result: great}"))
    rep = vr.Report()
    vr.check_catalog(root, rep)
    text = " ".join(rep.errors)
    assert "requires a real endpoint" in text
    assert "peer_testing result must be one of" in text
    assert "none.md' not found" in text


def test_skill_requiring_unknown_tool_is_rejected(tmp_path):
    root = _repo_copy(tmp_path)
    entry = root / "catalog" / "entries" / "obs-model-comparison.yaml"
    entry.write_text(entry.read_text().replace("obs-model-starter/list_datasets",
                                               "obs-model-starter/does_not_exist"))
    rep = vr.Report()
    vr.check_catalog(root, rep)
    assert any("does not list tool 'does_not_exist'" in e for e in rep.errors)


def test_scaffold_creates_valid_passing_contribution(tmp_path):
    root = _repo_copy(tmp_path)
    assert new_contribution.main(["--team", "zz-tooling-test", "--server", "zz-scaffold-tools",
                                  "--skill", "zz-scaffold-check", "--root", str(root)]) == 0
    server = root / "servers" / "zz-scaffold-tools"
    assert (server / "server.py").exists() and (root / "submissions" / "zz-tooling-test" / "discovery-record.md").exists()
    assert "__SERVER_NAME__" not in (server / "server.py").read_text()
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--rootdir", str(server),
                             str(server / "tests")], capture_output=True, text=True, cwd=root)
    assert result.returncode == 0, result.stdout + result.stderr
    rep = vr.run(root, ["catalog", "files", "skills", "deps", "tooltests", "links", "clients"])
    assert rep.errors == []
    assert "zz-scaffold-tools" in client_config.load_mcp_json(root)
    assert client_config.load_codex(root)["zz-scaffold-tools"]["args"] == client_config.stdio_args("zz-scaffold-tools")
    with pytest.raises(SystemExit, match="Already exists"):
        new_contribution.main(["--team", "zz-tooling-test", "--server", "zz-scaffold-tools", "--root", str(root)])
    with pytest.raises(SystemExit, match="must be 3-40"):
        new_contribution.main(["--team", "x", "--server", "Bad_Name", "--root", str(root)])


def test_client_configs_must_agree(tmp_path):
    root = _repo_copy(tmp_path)
    assert vr.run(root, ["clients"]).errors == []
    toml = root / ".codex" / "config.toml"
    toml.write_text(toml.read_text().replace("servers/obs-model-starter/server.py", "servers/other/server.py"))
    errors = " ".join(vr.run(root, ["clients"]).errors)
    assert "launched differently" in errors
    (root / "servers" / "unregistered-tools").mkdir()
    assert "not registered" in " ".join(vr.run(root, ["clients"]).errors)


def test_install_skills_targets_each_client(tmp_path, monkeypatch):
    monkeypatch.setattr(install_skills, "REPO", tmp_path)
    assert install_skills.main([]) == 0
    for folder in (".claude", ".agents"):
        assert (tmp_path / folder / "skills" / "obs-model-comparison" / "SKILL.md").exists()
    assert not (tmp_path / ".github" / "skills").exists()
    assert install_skills.main(["--check"]) == 0
    assert install_skills.main(["--check", "--client", "codex"]) == 0
    install_skills.main(["--remove", "--client", "claude"])
    assert install_skills.main(["--check", "--client", "claude"]) == 1
    assert install_skills.main(["--check", "--client", "copilot"]) == 0


def test_install_skills_copy_check_and_remove(tmp_path):
    target = tmp_path / "skills"
    assert install_skills.main(["--target", str(target), "--check"]) == 1
    assert install_skills.main(["--target", str(target)]) == 0
    assert (target / "obs-model-comparison" / "SKILL.md").exists()
    assert install_skills.main(["--target", str(target), "--check"]) == 0
    (target / "obs-model-comparison" / "SKILL.md").write_text("edited copy")
    assert install_skills.main(["--target", str(target), "--check"]) == 1
    assert install_skills.main(["--target", str(target), "--remove", "obs-model-comparison"]) == 0
    assert not (target / "obs-model-comparison").exists()


def test_package_contribution_is_deterministic_and_verifiable(tmp_path, monkeypatch):
    monkeypatch.setattr(package, "DIST", tmp_path)
    target, digest = package.package_contribution("obs-model-starter")
    _, digest2 = package.package_contribution("obs-model-starter")
    assert digest == digest2
    with zipfile.ZipFile(target) as zf:
        names = zf.namelist()
    assert "servers/obs-model-starter/server.py" in names
    assert "obs-model-starter-0.1.0.MANIFEST.json" in names
    assert not any("__pycache__" in n or n.endswith(".env") for n in names)
    assert package.verify(target) == 0


def test_bundle_contains_accepted_artifacts_only(tmp_path, monkeypatch):
    monkeypatch.setattr(package, "DIST", tmp_path)
    target, _ = package.package_bundle()
    with zipfile.ZipFile(target) as zf:
        names = set(zf.namelist())
    assert "servers/obs-model-starter/server.py" in names
    assert "skills/obs-model-comparison/SKILL.md" in names
    assert "BUNDLE_MANIFEST.json" in names
    assert {".mcp.json", ".codex/config.toml", "AGENTS.md", "CLAUDE.md"} <= names
    assert not any(n.startswith((".claude/", ".agents/")) for n in names)
    assert package.verify(target) == 0


def test_catalog_search_and_index():
    ids = {e["id"] for e in catalog.search(REPO, ["bias"])}
    assert "obs-model-starter" in ids
    assert "| [obs-model-starter](entries/obs-model-starter.yaml) |" in catalog.render_index(REPO)
