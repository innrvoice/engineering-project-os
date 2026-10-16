"""Proof refresh must be deliberate and older project extensions must stay owned."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_project_os import PROJECT_OS as P


class FindingProofCompatibilityTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name).resolve()
        self.root = self.parent / "project"
        self.root.mkdir()
        self.quiet(P.init_project, self.root, "none", "none", False, False)
        self.registry_path = self.root / ".agents/findings/findings.json"
        self.evidence_path = self.root / ".agents/evidence/reproduction.md"
        self.evidence_path.write_text("Observed before the repair.\n", encoding="utf-8")
        self.input_path = self.parent / "finding-input.json"
        self.definition = {
            "title": "A supported input fails",
            "status": "confirmed",
            "impact": "A controlled reproduction fails before the repair.",
            "evidence": [self.evidence_path.relative_to(self.root).as_posix()],
            "required_check": "Repeat the reproduction after the repair.",
        }
        self.write_input()

    def quiet(self, function, *args, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return function(*args, **kwargs)

    def write_input(self) -> None:
        self.input_path.write_text(json.dumps(self.definition) + "\n", encoding="utf-8")

    def record(self, identifier=None, dry_run=False):
        return self.quiet(P.record_finding, self.root, self.input_path, identifier, dry_run)

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file() and not path.is_symlink()}

    def registry(self):
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def write_registry(self, value) -> None:
        self.registry_path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def check(self, expected=0):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            actual = P.check_project(self.root)
        self.assertEqual(actual, expected, output.getvalue())
        return output.getvalue()

    def make_legacy(self, release="2.2.2", custom_path=False) -> None:
        """Construct the historical public schema, without a local cache dependency."""
        workflow = self.root / ".agents/WORKFLOW.md"
        workflow.write_text("# Historical schema-5 workflow\n\nPreserve repository-owned records.\n", encoding="utf-8")
        system_path = self.root / ".agents/SYSTEM.json"
        system = json.loads(system_path.read_text(encoding="utf-8"))
        system["project_os_version"] = release
        system["managed_guidance"][".agents/WORKFLOW.md"] = "sha256:" + hashlib.sha256(workflow.read_bytes()).hexdigest()
        if custom_path:
            destination = self.root / ".agents/local-incidents.json"
            self.registry_path.rename(destination)
            self.registry_path = destination
            system["paths"]["findings"] = destination.relative_to(self.root).as_posix()
        system_path.write_text(json.dumps(system, indent=2) + "\n", encoding="utf-8")

    def upgrade(self, dry_run=False, review=None):
        kwargs = {} if review is None else {"finding_proof_review": review}
        return self.quiet(P.upgrade_project, self.root, None, None, None, None, dry_run, **kwargs)

    def legacy_223_capture(self, custom_path=False):
        """The published 2.2.3 capture shape, independent of a local installed helper."""
        self.make_legacy("2.2.3", custom_path)
        hashes = {self.definition["evidence"][0]: "sha256:" + hashlib.sha256(self.evidence_path.read_bytes()).hexdigest()}
        entry = dict(self.definition, id="F-001", evidence_sha256=hashes,
                     capture_input_sha256=P.record_hash(self.definition), owner_note="Preserve local history.")
        self.write_registry({"schema_version": 1, "next_id": 2, "findings": [entry]})
        return entry

    def review(self, ownership, snapshot_evidence=None):
        path = self.root / ".agents/evidence/finding-proof-review.json"
        value = {"schema_version": 1,
                 "registry_sha256": "sha256:" + hashlib.sha256(self.registry_path.read_bytes()).hexdigest(),
                 "ownership": ownership}
        if snapshot_evidence is not None:
            value["snapshot_evidence"] = snapshot_evidence
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def managed_capture(self, release="2.2.3", custom_evidence=False):
        self.make_legacy(release, custom_path=True)
        (self.root / "AGENTS.md").write_text(
            "# Repository rules\n\nRead .agents/CONTEXT.md, .agents/STATE.md and .agents/WORKFLOW.md.\n\nPreserve this local instruction.\n"
        )
        if custom_evidence:
            destination = self.root / "audit-evidence"
            (self.root / ".agents/evidence").rename(destination)
            (self.root / ".agents/evidence").mkdir()
            shutil.copyfile(destination / "README.md", self.root / ".agents/evidence/README.md")
            self.evidence_path = destination / "reproduction.md"
            system_path = self.root / ".agents/SYSTEM.json"
            system = json.loads(system_path.read_text())
            system["paths"]["evidence"] = "audit-evidence"
            system_path.write_text(P.canonical_json(system))
        self.definition["evidence"] = ["AGENTS.md", ".agents/SYSTEM.json", ".agents/WORKFLOW.md",
                                       self.evidence_path.relative_to(self.root).as_posix()]
        self.write_input()
        old_bytes = {path: (self.root / path).read_bytes() for path in self.definition["evidence"]}
        hashes = {path: "sha256:" + hashlib.sha256(content).hexdigest() for path, content in old_bytes.items()}
        entry = dict(self.definition, id="F-001", owner_note="Preserve local history.")
        proof = {"schema_version": 1, "owner": P.FINDING_PROOF_OWNER,
                 "capture_input_sha256": P.record_hash(self.definition), "evidence_sha256": hashes}
        if release == "2.2.3":
            entry.update(evidence_sha256=hashes, capture_input_sha256=proof["capture_input_sha256"])
        else:
            entry[P.FINDING_PROOF_KEY] = proof
        owner = {"id": "F-002", "status": "confirmed", "impact": "Local owner finding",
                 "evidence": [self.evidence_path.relative_to(self.root).as_posix()], "required_check": "Owner check",
                 "evidence_sha256": "Owner data", "capture_input_sha256": {"owner": "format"},
                 "owner_extension": ["unchanged"]}
        self.write_registry({"schema_version": 1, "next_id": 3, "findings": [entry, owner]})
        consent = {"F-001": {path: hashes[path] for path in self.definition["evidence"][:3]}}
        return old_bytes, entry, owner, consent

    def managed_review(self, consent, release="2.2.3"):
        ownership = {"F-001": "helper_2_2_3", "F-002": "project_owned"} if release == "2.2.3" else {}
        # A review need not live in the configured evidence directory.
        (self.root / ".agents/evidence").mkdir(exist_ok=True)
        return self.review(ownership, consent)

    def test_managed_223_evidence_is_reviewed_historical_proof_after_atomic_upgrade(self) -> None:
        old_bytes, old, owner, consent = self.managed_capture(custom_evidence=True)
        review = self.managed_review(consent)
        registry_hash = "sha256:" + hashlib.sha256(self.registry_path.read_bytes()).hexdigest()
        review_hash = "sha256:" + hashlib.sha256(review.read_bytes()).hexdigest()
        before = self.snapshot()
        self.assertEqual(self.upgrade(True, review), 0)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.upgrade(review=review), 0)
        saved = self.registry()["findings"][0]
        self.assertEqual(saved["evidence"], old["evidence"])
        self.assertEqual(saved["evidence_sha256"], old["evidence_sha256"])
        self.assertEqual(saved["capture_input_sha256"], old["capture_input_sha256"])
        proof = saved[P.FINDING_PROOF_KEY]
        self.assertEqual(proof["evidence_sha256"], old["evidence_sha256"])
        self.assertEqual(proof["capture_input_sha256"], old["capture_input_sha256"])
        self.assertEqual(set(proof["evidence_snapshots"]), set(consent["F-001"]))
        for path, snapshot in proof["evidence_snapshots"].items():
            self.assertNotEqual((self.root / path).read_bytes(), old_bytes[path])
            self.assertEqual((self.root / snapshot["path"]).read_bytes(), old_bytes[path])
            self.assertTrue(snapshot["path"].startswith("audit-evidence/finding-proof-snapshots/"))
            self.assertEqual(snapshot["source_release"], "2.2.3")
            self.assertEqual(snapshot["registry_sha256"], registry_hash)
            self.assertEqual(snapshot["review_sha256"], review_hash)
        self.assertTrue((self.root / "AGENTS.md").read_bytes().startswith(old_bytes["AGENTS.md"]))
        self.assertEqual(self.registry()["findings"][1], owner)
        self.check()
        upgraded = self.snapshot()
        self.assertEqual(self.upgrade(review=review), 0)
        self.assertEqual(self.upgrade(), 0)
        self.assertEqual(self.snapshot(), upgraded)
        with self.assertRaisesRegex(P.ProjectOSError, "--id"):
            self.record()
        self.assertEqual(self.snapshot(), upgraded)
        self.evidence_path.write_text("Ordinary evidence is still protected.\n")
        self.check(1)
        self.evidence_path.write_bytes(old_bytes[self.evidence_path.relative_to(self.root).as_posix()])
        archive_path = self.root / proof["evidence_snapshots"]["AGENTS.md"]["path"]
        archive_path.write_text("A historical archive edit is detected.\n")
        self.check(1)

    def test_snapshot_consent_requires_exact_changed_paths_and_original_hashes(self) -> None:
        _, _, _, consent = self.managed_capture()
        wrong_hash = json.loads(json.dumps(consent))
        wrong_hash["F-001"]["AGENTS.md"] = "sha256:" + "0" * 64
        invalid = [None, {}, {"F-001": {}}, wrong_hash,
                   {"F-001": {**consent["F-001"], self.evidence_path.relative_to(self.root).as_posix(): "sha256:" + "a" * 64}},
                   {**consent, "F-002": {"AGENTS.md": consent["F-001"]["AGENTS.md"]}}]
        for value in invalid:
            review = self.managed_review(value)
            before = self.snapshot()
            for dry in (True, False):
                with self.subTest(value=value, dry_run=dry):
                    with self.assertRaisesRegex(P.ProjectOSError, "snapshot_evidence"):
                        self.upgrade(dry, review)
                    self.assertEqual(self.snapshot(), before)

    def test_stale_managed_evidence_refuses_without_archiving_or_repinning(self) -> None:
        _, _, _, consent = self.managed_capture()
        review = self.managed_review(consent)
        path = self.root / "AGENTS.md"
        path.write_bytes(path.read_bytes() + b"\nChanged after old capture.\n")
        before = self.snapshot()
        for dry in (True, False):
            with self.assertRaisesRegex(P.ProjectOSError, "invalid proof"):
                self.upgrade(dry, review)
            self.assertEqual(self.snapshot(), before)

    def test_snapshot_destinations_refuse_wrong_bytes_directories_and_symlinks(self) -> None:
        old_bytes, _, _, consent = self.managed_capture()
        review = self.managed_review(consent)
        digest = hashlib.sha256(old_bytes["AGENTS.md"]).hexdigest()
        archive = self.root / ".agents/evidence/finding-proof-snapshots" / (digest + ".bin")
        archive.parent.mkdir()
        outside = self.parent / "outside-archive"
        outside.write_bytes(old_bytes["AGENTS.md"])
        for kind in ("wrong", "directory", "symlink"):
            if kind == "wrong":
                archive.write_text("Preserve conflicting owner data.\n")
            elif kind == "directory":
                archive.mkdir()
            else:
                archive.symlink_to(outside)
            before = self.snapshot()
            for dry in (True, False):
                with self.subTest(kind=kind, dry_run=dry):
                    with self.assertRaises((P.ProjectOSError, OSError)):
                        self.upgrade(dry, review)
                    self.assertEqual(self.snapshot(), before)
                    self.assertEqual(outside.read_bytes(), old_bytes["AGENTS.md"])
            archive.rmdir() if kind == "directory" else archive.unlink()

    def test_shared_snapshot_content_is_deduplicated_and_existing_exact_bytes_reused(self) -> None:
        old_bytes, old, _, consent = self.managed_capture()
        value = self.registry()
        duplicate = dict(old, id="F-003")
        value["findings"].append(duplicate)
        value["next_id"] = 4
        self.write_registry(value)
        consent["F-003"] = dict(consent["F-001"])
        review = self.review({"F-001": "helper_2_2_3", "F-002": "project_owned", "F-003": "helper_2_2_3"}, consent)
        digest = hashlib.sha256(old_bytes["AGENTS.md"]).hexdigest()
        archive = self.root / ".agents/evidence/finding-proof-snapshots" / (digest + ".bin")
        archive.parent.mkdir()
        archive.write_bytes(old_bytes["AGENTS.md"])
        inode = archive.stat().st_ino
        self.assertEqual(self.upgrade(review=review), 0)
        self.assertEqual(archive.stat().st_ino, inode)
        findings = self.registry()["findings"]
        self.assertEqual(findings[0][P.FINDING_PROOF_KEY]["evidence_snapshots"], findings[2][P.FINDING_PROOF_KEY]["evidence_snapshots"])
        self.assertEqual(len(list(archive.parent.glob("*.bin"))), 3)
        self.check()

    def test_snapshot_upgrade_failure_rolls_back_archives_registry_and_managed_files(self) -> None:
        _, _, _, consent = self.managed_capture()
        review = self.managed_review(consent)
        before = self.snapshot()
        with mock.patch.object(P, "require_passing_check", side_effect=P.ProjectOSError("Injected validation failure")):
            with self.assertRaises(P.ProjectOSError):
                self.upgrade(review=review)
        self.assertEqual(self.snapshot(), before)

    def test_concurrent_review_change_rolls_back_created_snapshots_and_preserves_edit(self) -> None:
        _, _, _, consent = self.managed_capture()
        review = self.managed_review(consent)
        before = self.snapshot()
        check = P.require_passing_check
        concurrent = b'{"owner":"A concurrent review edit"}\n'

        def check_then_edit(*args):
            check(*args)
            review.write_bytes(concurrent)

        with mock.patch.object(P, "require_passing_check", side_effect=check_then_edit):
            with self.assertRaises(P.ProjectOSError):
                self.upgrade(review=review)
        after = self.snapshot()
        key = review.relative_to(self.root).as_posix()
        self.assertEqual(after.pop(key), concurrent)
        before.pop(key)
        self.assertEqual(after, before)

    def test_current_owned_proof_can_be_carried_through_later_managed_refresh(self) -> None:
        old_bytes, old, owner, consent = self.managed_capture(release=P.VERSION)
        self.check()
        before = self.snapshot()
        for dry in (True, False):
            with self.assertRaisesRegex(P.ProjectOSError, "snapshot_evidence"):
                self.upgrade(dry)
            self.assertEqual(self.snapshot(), before)
        review = self.managed_review(consent, release=P.VERSION)
        self.assertEqual(self.upgrade(review=review), 0)
        proof = self.registry()["findings"][0][P.FINDING_PROOF_KEY]
        self.assertEqual(proof["evidence_sha256"], old[P.FINDING_PROOF_KEY]["evidence_sha256"])
        self.assertEqual(self.registry()["findings"][1], owner)
        for path, snapshot in proof["evidence_snapshots"].items():
            self.assertEqual((self.root / snapshot["path"]).read_bytes(), old_bytes[path])
        self.check()

    def test_source_edit_after_snapshot_planning_aborts_without_writes(self) -> None:
        _, _, _, consent = self.managed_capture()
        review = self.managed_review(consent)
        before = self.snapshot()
        execute = P.execute_sync_transaction
        concurrent = b"# Concurrent repository instruction\n"

        def edit_then_execute(*args, **kwargs):
            (self.root / "AGENTS.md").write_bytes(concurrent)
            execute(*args, **kwargs)

        with mock.patch.object(P, "execute_sync_transaction", side_effect=edit_then_execute):
            with self.assertRaises(P.ProjectOSError):
                self.upgrade(review=review)
        after = self.snapshot()
        self.assertEqual(after.pop("AGENTS.md"), concurrent)
        before.pop("AGENTS.md")
        self.assertEqual(after, before)

    def test_concurrent_archive_edit_is_preserved_while_other_upgrade_writes_roll_back(self) -> None:
        _, _, _, consent = self.managed_capture()
        review = self.managed_review(consent)
        before = self.snapshot()
        check = P.require_passing_check
        concurrent = b"Concurrent snapshot replacement - do not overwrite.\n"
        changed_path = None

        def check_then_edit(*args):
            nonlocal changed_path
            check(*args)
            entry = self.registry()["findings"][0][P.FINDING_PROOF_KEY]["evidence_snapshots"]["AGENTS.md"]
            changed_path = self.root / entry["path"]
            changed_path.write_bytes(concurrent)

        with mock.patch.object(P, "require_passing_check", side_effect=check_then_edit):
            with self.assertRaises(P.ProjectOSError):
                self.upgrade(review=review)
        self.assertIsNotNone(changed_path)
        after = self.snapshot()
        self.assertEqual(after.pop(changed_path.relative_to(self.root).as_posix()), concurrent)
        self.assertEqual(after, before)

    def test_historical_proof_survives_planned_deletion_of_original_file(self) -> None:
        _, _, _, _ = self.managed_capture(release=P.VERSION)
        value = self.registry()
        value["findings"] = value["findings"][:1]
        self.write_registry(value)
        path = self.evidence_path
        raw_path = path.relative_to(self.root).as_posix()
        expected = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        review = self.managed_review({"F-001": {raw_path: expected}}, release=P.VERSION)
        system = json.loads((self.root / ".agents/SYSTEM.json").read_text())
        preconditions = {}
        creates, replacements = P.plan_finding_proof_migration(self.root, system, preconditions, review, {path})
        self.quiet(P.execute_sync_transaction, self.root, creates, replacements,
                   [(path, expected.removeprefix("sha256:"))],
                   after_write=lambda: self.check(), preconditions=preconditions)
        self.assertFalse(path.exists())
        saved = self.registry()["findings"][0][P.FINDING_PROOF_KEY]
        self.assertEqual(saved["evidence_sha256"][raw_path], expected)
        self.assertEqual(P.file_sha256(self.root / saved["evidence_snapshots"][raw_path]["path"]), expected)
        self.check()

    def test_invalid_or_unsafe_snapshot_metadata_fails_check(self) -> None:
        _, _, _, consent = self.managed_capture()
        review = self.managed_review(consent)
        self.assertEqual(self.upgrade(review=review), 0)
        original = self.registry()
        for field, bad in (("evidence_snapshots", {}), ("evidence_snapshots", "owner text"),
                           ("path", "../outside"), ("review_sha256", "not a digest"),
                           ("registry_sha256", "sha256:" + "0" * 63), ("source_release", None)):
            value = json.loads(json.dumps(original))
            proof = value["findings"][0][P.FINDING_PROOF_KEY]
            if field == "evidence_snapshots":
                proof[field] = bad
            else:
                proof["evidence_snapshots"]["AGENTS.md"][field] = bad
            self.write_registry(value)
            with self.subTest(field=field, value=bad):
                self.check(1)

    def test_unchanged_implicit_repeat_is_a_true_noop(self) -> None:
        self.assertEqual(self.record(), 0)
        self.check()
        before = self.snapshot()
        stat = self.registry_path.stat()
        identity = (stat.st_ino, stat.st_mtime_ns)
        input_bytes = self.input_path.read_bytes()
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                self.assertEqual(self.record(dry_run=dry_run), 0)
                self.assertEqual(self.snapshot(), before)
                current = self.registry_path.stat()
                self.assertEqual((current.st_ino, current.st_mtime_ns), identity)
                self.assertEqual(self.input_path.read_bytes(), input_bytes)
        self.assertEqual(self.registry()["next_id"], 2)

    def test_changed_proof_cannot_be_repinned_by_identical_input(self) -> None:
        self.assertEqual(self.record(), 0)
        original_registry = self.registry_path.read_bytes()
        self.evidence_path.write_text("Changed after capture; this requires a reviewed update.\n", encoding="utf-8")
        self.check(1)
        before = self.snapshot()
        input_bytes = self.input_path.read_bytes()
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                with self.assertRaises(P.ProjectOSError):
                    self.record(dry_run=dry_run)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.registry_path.read_bytes(), original_registry)
                self.assertEqual(self.input_path.read_bytes(), input_bytes)
                self.check(1)

    def assert_single_matching_branch_cannot_refresh(self, branch) -> None:
        self.assertEqual(self.record(), 0)
        value = self.registry()
        entry = value["findings"][0]
        proof = entry["project_os_finding_proof"]
        if branch == "input_hash":
            entry["observation"] = "Retained context omitted from this identical input."
        else:
            proof["capture_input_sha256"] = "sha256:" + "0" * 64
        projected = {key: entry[key] for key in P.FINDING_INPUT_FIELDS if key in entry}
        self.assertEqual(proof["capture_input_sha256"] == P.record_hash(self.definition), branch == "input_hash")
        self.assertEqual(projected == self.definition, branch == "fields")
        self.write_registry(value)
        self.check()
        self.evidence_path.write_text("Different evidence must not be silently approved.\n", encoding="utf-8")
        self.check(1)
        before = self.snapshot()
        source_input = self.input_path.read_bytes()
        for dry_run in (True, False):
            with self.subTest(branch=branch, dry_run=dry_run):
                with self.assertRaisesRegex(P.ProjectOSError, "--id"):
                    self.record(dry_run=dry_run)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.input_path.read_bytes(), source_input)
                self.check(1)

    def test_input_hash_only_match_cannot_implicitly_refresh_changed_proof(self) -> None:
        self.assert_single_matching_branch_cannot_refresh("input_hash")

    def test_field_equivalence_only_match_cannot_implicitly_refresh_changed_proof(self) -> None:
        self.assert_single_matching_branch_cannot_refresh("fields")

    def test_explicit_id_deliberately_refreshes_evidence_for_the_same_finding(self) -> None:
        self.assertEqual(self.record(), 0)
        original_registry = self.registry_path.read_bytes()
        self.evidence_path.write_text("A reviewed later reproduction is now the evidence.\n", encoding="utf-8")
        self.check(1)
        before = self.snapshot()
        self.assertEqual(self.record("F-001", True), 0)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.record("F-001"), 0)
        self.assertNotEqual(self.registry_path.read_bytes(), original_registry)
        self.assertEqual([entry["id"] for entry in self.registry()["findings"]], ["F-001"])
        self.assertEqual(self.registry()["next_id"], 2)
        self.check()
        refreshed = self.snapshot()
        self.assertEqual(self.record(), 0)
        self.assertEqual(self.snapshot(), refreshed)

    def test_legacy_owner_proof_like_fields_survive_upgrade_and_explicit_update(self) -> None:
        raw_path = self.definition["evidence"][0]
        digest = hashlib.sha256(self.evidence_path.read_bytes()).hexdigest()
        corpus = (
            ("owner note", "owner input note"),
            ({"format": "owner-v1", "digest": "opaque"}, {"owner": "local"}),
            ({raw_path: digest}, P.record_hash(self.definition)),
            ({raw_path: "sha256:" + digest}, P.record_hash(self.definition)),
        )
        original_root = self.root
        for index, (owner_proofs, owner_input) in enumerate(corpus):
            with self.subTest(owner_proofs=owner_proofs, owner_input=owner_input):
                self.root = self.parent / f"legacy-{index}"
                shutil.copytree(original_root, self.root)
                self.registry_path = self.root / ".agents/findings/findings.json"
                self.make_legacy(custom_path=index % 2 == 1)
                entry = dict(self.definition, id="OWNER-017", evidence_sha256=owner_proofs,
                             capture_input_sha256=owner_input, owner_extension={"retain": ["all", "values"]})
                self.write_registry({"schema_version": 1, "next_id": 18, "findings": [entry]})
                before = self.snapshot()
                self.assertEqual(self.upgrade(True), 0)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.upgrade(), 0)
                self.assertEqual(self.registry()["findings"][0], entry)
                self.check()
                upgraded = self.snapshot()
                self.assertEqual(self.upgrade(), 0)
                self.assertEqual(self.snapshot(), upgraded)
                self.assertEqual(self.record("OWNER-017", True), 0)
                self.assertEqual(self.snapshot(), upgraded)
                self.assertEqual(self.record("OWNER-017"), 0)
                current = self.registry()["findings"][0]
                self.assertEqual(current["evidence_sha256"], owner_proofs)
                self.assertEqual(current["capture_input_sha256"], owner_input)
                self.assertEqual(current["owner_extension"], entry["owner_extension"])
                self.check()

    def test_failed_legacy_upgrade_preserves_owner_fields_and_custom_registry(self) -> None:
        self.make_legacy(custom_path=True)
        entry = dict(self.definition, id="OWNER-017", evidence_sha256="Owner-defined text.",
                     capture_input_sha256={"owner": "retain"})
        self.write_registry({"schema_version": 1, "next_id": 18, "findings": [entry]})
        before = self.snapshot()
        with mock.patch.object(P, "require_passing_check", side_effect=P.ProjectOSError("Injected validation failure")):
            with self.assertRaises(P.ProjectOSError):
                self.upgrade()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.registry()["findings"][0], entry)

    def test_legacy_match_requires_explicit_capture_and_retains_bare_owner_keys(self) -> None:
        entry = dict(self.definition, id="OWNER-017", evidence_sha256="Owner-defined proof note.",
                     capture_input_sha256=P.record_hash(self.definition))
        self.write_registry({"schema_version": 1, "next_id": 18, "findings": [entry]})
        self.check()
        before = self.snapshot()
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                with self.assertRaisesRegex(P.ProjectOSError, "--id"):
                    self.record(dry_run=dry_run)
                self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.record("OWNER-017"), 0)
        current = self.registry()["findings"][0]
        self.assertEqual(current["evidence_sha256"], entry["evidence_sha256"])
        self.assertEqual(current["capture_input_sha256"], entry["capture_input_sha256"])
        self.check()

    def test_occupied_proof_namespace_is_not_overwritten_by_capture(self) -> None:
        for occupied in ("Owner text.", {"owner_note": "Preserve this collision."},
                         {"owner": "another-tool", "schema_version": 1},
                         {"owner": "engineering-project-os", "schema_version": 999}):
            entry = dict(self.definition, id="OWNER-017", project_os_finding_proof=occupied)
            self.write_registry({"schema_version": 1, "next_id": 18, "findings": [entry]})
            self.check()
            before = self.snapshot()
            for identifier in (None, "OWNER-017"):
                for dry_run in (True, False):
                    with self.subTest(occupied=occupied, identifier=identifier, dry_run=dry_run):
                        with self.assertRaises(P.ProjectOSError):
                            self.record(identifier, dry_run)
                        self.assertEqual(self.snapshot(), before)

    def test_source_223_requires_review_instead_of_guessing_legacy_ownership(self) -> None:
        self.legacy_223_capture()
        before = self.snapshot()
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                with self.assertRaises(P.ProjectOSError):
                    self.upgrade(dry_run)
                self.assertEqual(self.snapshot(), before)

    def test_direct_check_explains_223_ownership_for_current_and_changed_evidence(self) -> None:
        self.legacy_223_capture()
        for content in ("Observed before the repair.\n", "Evidence changed after the old capture.\n"):
            with self.subTest(content=content):
                self.evidence_path.write_text(content, encoding="utf-8")
                before = self.snapshot()
                output = self.check(1)
                self.assertIn("--finding-proof-review", output)
                self.assertEqual(self.snapshot(), before)

    def test_record_cannot_bypass_223_upgrade_and_ownership_review(self) -> None:
        self.legacy_223_capture()
        before = self.snapshot()
        for identifier in (None, "F-001"):
            for dry_run in (True, False):
                with self.subTest(identifier=identifier, dry_run=dry_run):
                    with self.assertRaises(P.ProjectOSError):
                        self.record(identifier, dry_run)
                    self.assertEqual(self.snapshot(), before)

    def test_genuine_223_capture_migrates_original_hashes_and_keeps_tamper_guard(self) -> None:
        old = self.legacy_223_capture(custom_path=True)
        review = self.review({"F-001": "helper_2_2_3"})
        before = self.snapshot()
        self.assertEqual(self.upgrade(True, review), 0)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.upgrade(review=review), 0)
        current = self.registry()["findings"][0]
        self.assertEqual(current["evidence_sha256"], old["evidence_sha256"])
        self.assertEqual(current["capture_input_sha256"], old["capture_input_sha256"])
        self.assertEqual(current["owner_note"], old["owner_note"])
        self.assertEqual(current["project_os_finding_proof"], {
            "schema_version": 1, "owner": "engineering-project-os",
            "capture_input_sha256": old["capture_input_sha256"],
            "evidence_sha256": old["evidence_sha256"],
        })
        self.check()
        migrated = self.snapshot()
        self.assertEqual(self.upgrade(), 0)
        self.assertEqual(self.upgrade(True, review), 0)
        self.assertEqual(self.upgrade(review=review), 0)
        self.assertEqual(self.record(), 0)
        self.assertEqual(self.snapshot(), migrated)
        self.evidence_path.write_text("Changed after migration.\n", encoding="utf-8")
        self.check(1)
        changed = self.snapshot()
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                with self.assertRaises(P.ProjectOSError):
                    self.record(dry_run=dry_run)
                self.assertEqual(self.snapshot(), changed)
                with self.assertRaises(P.ProjectOSError):
                    self.upgrade(dry_run, review)
                self.assertEqual(self.snapshot(), changed)
        self.assertEqual(self.record("F-001"), 0)
        self.assertEqual(self.registry()["findings"][0]["evidence_sha256"], old["evidence_sha256"])
        self.check()

    def test_genuine_223_stale_proof_is_not_repinned_during_migration(self) -> None:
        self.legacy_223_capture()
        self.evidence_path.write_text("The old capture no longer proves these changed bytes.\n", encoding="utf-8")
        review = self.review({"F-001": "helper_2_2_3"})
        before = self.snapshot()
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                with self.assertRaises(P.ProjectOSError):
                    self.upgrade(dry_run, review)
                self.assertEqual(self.snapshot(), before)

    def test_project_owned_review_preserves_ambiguous_223_values_without_claiming_proof(self) -> None:
        old = self.legacy_223_capture()
        review = self.review({"F-001": "project_owned"})
        self.assertEqual(self.upgrade(review=review), 0)
        self.assertEqual(self.registry()["findings"][0], old)
        self.evidence_path.write_text("Owner data does not claim a helper verification of these bytes.\n", encoding="utf-8")
        self.check()
        before = self.snapshot()
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                with self.assertRaises(P.ProjectOSError):
                    self.record(dry_run=dry_run)
                self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.record("F-001"), 0)
        self.assertEqual(self.registry()["findings"][0]["evidence_sha256"], old["evidence_sha256"])
        self.assertEqual(self.registry()["findings"][0]["capture_input_sha256"], old["capture_input_sha256"])
        self.check()

    def test_project_owned_223_review_preserves_nonhelper_field_types(self) -> None:
        old = self.legacy_223_capture()
        old.update(evidence_sha256="The owner's evidence summary.", capture_input_sha256={"owner": "local signature"})
        self.write_registry({"schema_version": 1, "next_id": 2, "findings": [old]})
        review = self.review({"F-001": "project_owned"})
        self.assertEqual(self.upgrade(review=review), 0)
        self.assertEqual(self.registry()["findings"][0], old)
        self.check()
        self.assertEqual(self.record("F-001"), 0)
        current = self.registry()["findings"][0]
        self.assertEqual(current["evidence_sha256"], old["evidence_sha256"])
        self.assertEqual(current["capture_input_sha256"], old["capture_input_sha256"])
        self.check()

    def test_source_223_without_ambiguous_keys_needs_no_ownership_review(self) -> None:
        self.make_legacy("2.2.3")
        entry = dict(self.definition, id="F-001", owner_note="Manually recorded finding.")
        self.write_registry({"schema_version": 1, "next_id": 2, "findings": [entry]})
        original_registry = self.registry_path.read_bytes()
        self.assertEqual(self.upgrade(), 0)
        self.assertEqual(self.registry_path.read_bytes(), original_registry)
        self.check()

    def test_unrelated_opaque_namespace_and_raw_input_hash_do_not_hijack_new_capture(self) -> None:
        old = dict(self.definition, id="OWNER-017", title="A different earlier finding",
                   project_os_finding_proof="Owner-defined opaque metadata.",
                   evidence_sha256={"owner": "preserve"}, capture_input_sha256=P.record_hash(self.definition))
        self.write_registry({"schema_version": 1, "next_id": 18, "findings": [old]})
        self.check()
        before = self.snapshot()
        self.assertEqual(self.record(dry_run=True), 0)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.record(), 0)
        entries = self.registry()["findings"]
        self.assertEqual(entries[0], old)
        self.assertEqual([entry["id"] for entry in entries], ["OWNER-017", "OWNER-018"])
        self.assertIn("project_os_finding_proof", entries[1])
        self.check()

    def test_stale_or_incomplete_ownership_review_cannot_change_project(self) -> None:
        self.legacy_223_capture()
        review = self.review({"F-001": "helper_2_2_3"})
        original = json.loads(review.read_text(encoding="utf-8"))
        variants = (
            dict(original, registry_sha256="sha256:" + "0" * 64),
            dict(original, ownership={}),
            dict(original, ownership={"F-001": "assume_helper"}),
            dict(original, ownership={"F-001": "helper_2_2_3", "F-999": "project_owned"}),
        )
        for value in variants:
            review.write_text(json.dumps(value) + "\n", encoding="utf-8")
            before = self.snapshot()
            for dry_run in (True, False):
                with self.subTest(value=value, dry_run=dry_run):
                    with self.assertRaises(P.ProjectOSError):
                        self.upgrade(dry_run, review)
                    self.assertEqual(self.snapshot(), before)

    def assert_duplicate_review_is_rejected(self, text) -> None:
        review = self.root / ".agents/evidence/duplicate-review.json"
        review.write_text(text + "\n", encoding="utf-8")
        before = self.snapshot()
        original_registry = self.registry_path.read_bytes()
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run, review=text):
                with self.assertRaises(P.ProjectOSError):
                    self.upgrade(dry_run, review)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.registry_path.read_bytes(), original_registry)
                source = json.loads((self.root / ".agents/SYSTEM.json").read_text(encoding="utf-8"))
                self.assertEqual(source["project_os_version"], "2.2.3")

    def test_duplicate_review_schema_does_not_choose_the_last_version(self) -> None:
        self.legacy_223_capture()
        digest = "sha256:" + hashlib.sha256(self.registry_path.read_bytes()).hexdigest()
        self.assert_duplicate_review_is_rejected(
            '{"schema_version":2,"schema_version":1,"registry_sha256":' + json.dumps(digest)
            + ',"ownership":{"F-001":"helper_2_2_3"}}'
        )

    def test_duplicate_review_registry_hash_does_not_choose_the_last_proof(self) -> None:
        self.legacy_223_capture()
        digest = "sha256:" + hashlib.sha256(self.registry_path.read_bytes()).hexdigest()
        self.assert_duplicate_review_is_rejected(
            '{"schema_version":1,"registry_sha256":"sha256:' + "0" * 64
            + '","registry_sha256":' + json.dumps(digest)
            + ',"ownership":{"F-001":"helper_2_2_3"}}'
        )

    def test_duplicate_review_ownership_decisions_are_not_resolved_by_order(self) -> None:
        self.legacy_223_capture()
        digest = "sha256:" + hashlib.sha256(self.registry_path.read_bytes()).hexdigest()
        for first, second in (("helper_2_2_3", "project_owned"), ("project_owned", "helper_2_2_3")):
            self.assert_duplicate_review_is_rejected(
                '{"schema_version":1,"registry_sha256":' + json.dumps(digest)
                + ',"ownership":{"F-001":' + json.dumps(first) + ',"F-001":' + json.dumps(second) + '}}'
            )

    def test_migration_validation_failure_rolls_back_proof_and_guidance_together(self) -> None:
        self.legacy_223_capture(custom_path=True)
        review = self.review({"F-001": "helper_2_2_3"})
        before = self.snapshot()
        with mock.patch.object(P, "require_passing_check", side_effect=P.ProjectOSError("Injected final validation failure")):
            with self.assertRaises(P.ProjectOSError):
                self.upgrade(review=review)
        self.assertEqual(self.snapshot(), before)

    def test_concurrent_ownership_review_edit_rolls_back_owned_writes_and_survives(self) -> None:
        self.legacy_223_capture()
        review = self.review({"F-001": "helper_2_2_3"})
        before = self.snapshot()
        check = P.require_passing_check
        concurrent = b'{"owner": "Concurrent review decision - do not overwrite."}\n'

        def check_then_edit(*args):
            check(*args)
            review.write_bytes(concurrent)

        with mock.patch.object(P, "require_passing_check", side_effect=check_then_edit):
            with self.assertRaises(P.ProjectOSError):
                self.upgrade(review=review)
        after = self.snapshot()
        key = review.relative_to(self.root).as_posix()
        self.assertEqual(after.pop(key), concurrent)
        before.pop(key)
        self.assertEqual(after, before)

    def test_ownership_review_outside_target_or_through_symlink_is_refused(self) -> None:
        self.legacy_223_capture()
        review = self.review({"F-001": "helper_2_2_3"})
        outside = self.parent / "outside-review.json"
        outside.write_bytes(review.read_bytes())
        link = self.root / ".agents/evidence/linked-review.json"
        link.symlink_to(outside)
        before = self.snapshot()
        outside_before = outside.read_bytes()
        for path in (outside, link):
            for dry_run in (True, False):
                with self.subTest(path=path, dry_run=dry_run):
                    with self.assertRaises(P.ProjectOSError):
                        self.upgrade(dry_run, path)
                    self.assertEqual(self.snapshot(), before)
                    self.assertEqual(outside.read_bytes(), outside_before)


if __name__ == "__main__":
    unittest.main()
