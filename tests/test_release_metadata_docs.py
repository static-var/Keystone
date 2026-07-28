import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate-keystone.py"
spec = importlib.util.spec_from_file_location("validate_keystone", VALIDATOR_PATH)
validate_keystone = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate_keystone)
PUBLIC_SKILLS = [
    "context-survey",
    "product-planning",
    "task-creation",
    "implementation",
    "refactoring",
    "root-cause-analysis",
    "change-review",
    "shipping",
    "project-audit",
]
RELEASE_VERSION = "2.0.4"


class ReleaseMetadataDocsTests(unittest.TestCase):
    def skill_description(self, skill):
        text = (ROOT / "skills" / skill / "SKILL.md").read_text()
        match = re.search(r"^description:\s*(?P<body>.+)$", text, re.MULTILINE)
        self.assertIsNotNone(match, f"{skill} must expose a model-visible description")
        assert match is not None
        return match.group("body")

    def test_implementation_description_requires_behavior_changing_project_work(self):
        description = self.skill_description("implementation")
        contracts = {
            "executable-software implementation": (
                r"\bexecutable[- ]software implementation\b"
            ),
            "implementation belongs to an identified project": (
                r"\bexecutable[- ]software implementation\b.*"
                r"\b(?:identified software project|existing project codebase)\b"
            ),
            "eligibility requires requested behavior alteration": (
                r"\bselect only when\b.*\brequested change\b.*\balters?\b.*"
                r"\bruntime\b.*\bAPI\b.*\bdata\b.*\bbuild\b.*\brelease\b.*"
                r"\bbehavior\b"
            ),
            "project-specific verification": r"\bproject-specific verification\b",
            "feature category": r"\bfeatures?\b",
            "diagnosed-fix category": r"\bdiagnosed fixes?\b",
            "migration category": r"\bmigrations?\b",
            "integration category": r"\bintegrations?\b",
            "runtime category": r"\bruntime\b",
            "API category": r"\bAPI\b",
            "data category": r"\bdata\b",
            "build category": r"\bbuild\b",
            "release category": r"\brelease\b",
            "automation category": r"\bautomation\b",
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertRegex(description, re.compile(pattern, re.IGNORECASE))
        mechanical_triggers = {
            "prose": r"\bprose\b",
            "documentation": r"\bdocumentation\b",
            "formatter": r"\bformatter\b",
            "line width": r"\bline[- ]width\b",
            "configuration or config": r"\bconfig(?:uration)?\b",
            "standalone": r"\bstandalone\b",
            "throwaway": r"\bthrowaway\b",
            "script": r"\bscripts?\b",
        }
        for trigger, pattern in mechanical_triggers.items():
            with self.subTest(mechanical_trigger=trigger):
                self.assertIsNone(re.search(pattern, description, re.IGNORECASE))

    def test_implementation_supporting_artifact_boundary_is_consistent(self):
        implementation = (ROOT / "skills" / "implementation" / "SKILL.md").read_text()
        readme = (ROOT / "README.md").read_text()
        how = (ROOT / "HOW_IT_WORKS.md").read_text()

        def section(text, heading):
            match = re.search(
                rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
                text,
                re.MULTILINE | re.DOTALL,
            )
            self.assertIsNotNone(match, f"missing section: {heading}")
            assert match is not None
            return match.group("body")

        boundary_pattern = re.compile(
            r"\bsupporting artifacts only within an already-active "
            r"behavior-changing implementation\b",
            re.IGNORECASE,
        )
        artifact_patterns = {
            "configuration": r"\bconfiguration\b",
            "documentation": r"\bdocumentation\b",
            "content": r"\bcontent\b",
            "scripts": r"\bscripts?\b",
        }

        skill_boundary = (
            f"{section(implementation, '## Load when')}\n"
            f"{section(implementation, '## Entry fit')}"
        )
        with self.subTest(source="implementation", contract="supporting boundary"):
            self.assertRegex(skill_boundary, boundary_pattern)
        for artifact, pattern in artifact_patterns.items():
            with self.subTest(source="implementation", artifact=artifact):
                self.assertRegex(skill_boundary, re.compile(pattern, re.IGNORECASE))

        for source, text in {"README": readme, "HOW_IT_WORKS": how}.items():
            with self.subTest(source=source, contract="explicit override example"):
                self.assertIsNotNone(
                    re.search(
                        r"^/implementation\b.*"
                        r"\b(?:config\w*|doc\w*|content|scripts?)\b",
                        text,
                        re.MULTILINE | re.IGNORECASE,
                    )
                )
            boundary_line = re.search(
                r"^(?P<body>.*supporting artifacts.*)$",
                text,
                re.MULTILINE | re.IGNORECASE,
            )
            with self.subTest(source=source, contract="supporting boundary"):
                self.assertIsNotNone(boundary_line)
            if boundary_line is None:
                continue
            body = boundary_line.group("body")
            with self.subTest(source=source, contract="active implementation"):
                self.assertRegex(body, boundary_pattern)
            for artifact, pattern in artifact_patterns.items():
                with self.subTest(source=source, artifact=artifact):
                    self.assertRegex(body, re.compile(pattern, re.IGNORECASE))

    def test_refactoring_description_requires_code_structure_and_invariant_proof(self):
        description = self.skill_description("refactoring")
        contracts = {
            "program source-code refactoring": (
                r"\bprogram source-code refactoring\b"
            ),
            "explicit structural code improvement": (
                r"\b(?:explicit(?:ly)?|user-requested)\b.*"
                r"\bstructural code improvement\b"
            ),
            "identified executable behavior preservation": (
                r"\bpreserv\w*\b.*\bidentified executable behavior\b"
            ),
            "project-specific invariant proof": r"\bproject-specific invariant proof\b",
            "eligibility requires structural change and proof or handoff": (
                r"\bselect only when\b.*\bstructural code change\b.*"
                r"\b(?:project-specific invariant proof|canonical handoff)\b"
            ),
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertRegex(description, re.compile(pattern, re.IGNORECASE))
        mechanical_triggers = {
            "formatting": r"\bformatting\b",
            "formatter": r"\bformatter\b",
            "settings": r"\bsettings?\b",
            "configuration or config": r"\bconfig(?:uration)?\b",
            "prose": r"\bprose\b",
            "documentation": r"\bdocumentation\b",
        }
        for trigger, pattern in mechanical_triggers.items():
            with self.subTest(mechanical_trigger=trigger):
                self.assertIsNone(re.search(pattern, description, re.IGNORECASE))

    def test_change_review_description_requires_a_new_readiness_verdict(self):
        description = self.skill_description("change-review")
        self.assertRegex(
            description,
            re.compile(
                r"\bneeds?\b.*\bnew evidence-backed readiness verdict\b",
                re.IGNORECASE,
            ),
        )

    def test_shipping_description_requires_authorized_immediate_execution(self):
        description = self.skill_description("shipping")
        contracts = {
            "authorized immediate delivery execution": (
                r"\bauthorized immediate delivery execution\b"
            ),
            "handoff has non-empty exact action set": (
                r"\bhandoff\b.*\bnon-empty exact authorized action set\b"
            ),
            "cleanup has exact named completed target": (
                r"\bdestructive cleanup\b.*"
                r"\bexact named completed-delivery target\b"
            ),
            "Context Survey owns cleanup reconnaissance": (
                r"\bContext Survey\b.*\bcleanup-target reconnaissance\b"
            ),
            "cleanup reconnaissance is before authorization": (
                r"\b(?:pre-authorization|pending-approval)\b"
            ),
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertRegex(description, re.compile(pattern, re.IGNORECASE))

    def test_openai_marketplace_release_notes_match_current_release(self):
        submission = json.loads(
            (ROOT / "marketplace" / "openai" / "submission.json").read_text()
        )
        release_notes = submission["releaseNotes"]
        with self.subTest(contract="current version"):
            self.assertRegex(
                release_notes,
                re.compile(rf"\bKeystone {re.escape(RELEASE_VERSION)}\b"),
            )
        with self.subTest(contract="workflow change is acknowledged"):
            self.assertNotIn(
                "Skills and workflow behavior are unchanged",
                release_notes,
            )

    def test_release_version_is_synchronized(self):
        package = json.loads((ROOT / "package.json").read_text())
        self.assertEqual(RELEASE_VERSION, package["version"])
        lockfile = json.loads((ROOT / "package-lock.json").read_text())
        self.assertEqual(RELEASE_VERSION, lockfile["version"])
        self.assertEqual(RELEASE_VERSION, lockfile["packages"][""]["version"])

        metadata_versions = {
            ".claude-plugin/plugin.json": lambda data: [data["version"]],
            ".claude-plugin/marketplace.json": lambda data: [data["version"], data["plugins"][0]["version"]],
            ".codex-plugin/plugin.json": lambda data: [data["version"]],
        }
        for rel, versions in metadata_versions.items():
            with self.subTest(rel=rel):
                data = json.loads((ROOT / rel).read_text())
                self.assertEqual([RELEASE_VERSION] * len(versions(data)), versions(data))

    def test_docs_describe_migration_to_nine_direct_skills(self):
        readme = (ROOT / "README.md").read_text()
        how = (ROOT / "HOW_IT_WORKS.md").read_text()
        combined = f"{readme}\n{how}"

        self.assertIn("Migrate from `/keystone` to direct skills", combined)
        self.assertIn("Use the matching public skill directly", combined)
        for skill in PUBLIC_SKILLS:
            with self.subTest(skill=skill):
                self.assertIn(f"/{skill}", combined)
        self.assertNotIn("standalone Agent Skills", combined)

    def test_shipping_explicit_only_sections_cover_canonical_actions(self):
        action_patterns = {
            "commit": r"\bcommits?\b",
            "push": r"\bpush(?:es)?\b",
            "PR": r"\bPRs?\b",
            "merge": r"\bmerge\b",
            "tag": r"\btag\b",
            "package": r"\bpackage\b",
            "publish": r"\bpublish\b",
            "release": r"\brelease\b",
            "deploy": r"\bdeploy\b",
            "repository handoff": r"\brepository handoff\b",
            "destructive cleanup": r"\bdestructive cleanup\b",
        }
        shipping = (ROOT / "skills" / "shipping" / "SKILL.md").read_text()
        readme = (ROOT / "README.md").read_text()
        how = (ROOT / "HOW_IT_WORKS.md").read_text()

        def section(text, heading):
            depth = len(heading.split(" ", 1)[0])
            return re.search(
                rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^#{{1,{depth}}} |\Z)",
                text,
                re.MULTILINE | re.DOTALL,
            )

        def line(text, marker):
            return re.search(
                rf"^(?P<body>.*{re.escape(marker)}.*)$",
                text,
                re.MULTILINE,
            )

        sections = {
            "Shipping description": re.search(
                r"^description: (?P<body>.*)$",
                shipping,
                re.MULTILINE,
            ),
            "Shipping Load when": section(shipping, "## Load when"),
            "Shipping Hard rules": section(shipping, "## Hard rules"),
            "Shipping Explicit-only finalization": section(
                shipping, "## Explicit-only finalization"
            ),
            "README Shipping trigger": line(readme, "| `shipping` |"),
            "README /shipping trigger": line(readme, "/shipping explicitly"),
            "README Explicit-only shipping": section(
                readme, "## Explicit-only shipping"
            ),
            "HOW Shipping trigger": line(how, "| `shipping` |"),
            "HOW /shipping trigger": line(how, "| `/keystone ship"),
            "HOW Shipping boundary": section(how, "### Shipping"),
            "HOW maintainer Shipping reminder": line(
                how, "Use `shipping` only when"
            ),
        }

        for source, match in sections.items():
            with self.subTest(source=source, section="present"):
                self.assertIsNotNone(match)
            assert match is not None
            body = match.group("body")
            for action, pattern in action_patterns.items():
                with self.subTest(source=source, action=action):
                    self.assertIsNotNone(re.search(pattern, body, re.IGNORECASE))

    def test_shipping_process_executes_authorized_actions_safely(self):
        shipping = (ROOT / "skills" / "shipping" / "SKILL.md").read_text()
        process = re.search(
            r"^## Process\n(?P<body>.*?)(?=^## |\Z)",
            shipping,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(process)
        assert process is not None

        contracts = {
            "perform authorized action set": (
                r"\bperform\b.*\bauthorized action set\b"
            ),
            "resolve exact targets": r"\bresolve\b.*\bexact targets?\b",
            "record results": r"\brecord\b.*\bresults?\b",
            "stop on failure": r"\bstop\b.*\bfail(?:s|ure|ed)?\b",
            "destructive cleanup recoverability": (
                r"\bdestructive cleanup\b.*\brecoverab"
            ),
            "destructive cleanup target confirmation": (
                r"\bdestructive cleanup\b.*\btarget confirmation\b"
            ),
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertIsNotNone(
                    re.search(pattern, process.group("body"), re.IGNORECASE | re.DOTALL)
                )

    def test_shipping_handoff_authorization_is_canonical(self):
        handoff = (ROOT / "skills" / "_shared" / "handoff-packet.md").read_text()
        rules = re.search(
            r"^## Rules\n(?P<body>.*?)(?=^## |\Z)",
            handoff,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(rules)
        assert rules is not None
        body = rules.group("body")

        contracts = {
            "shipping target condition": r"\btarget skill\b.*\bshipping\b",
            "evidence authorization field": (
                r"\bevidence\b.*\b(?:carries|contains)\b"
            ),
            "verbatim explicit delivery request": (
                r"\bverbatim\b.*\bexplicit delivery request\b"
            ),
            "exact authorized action set": r"\bexact authorized action set\b",
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertIsNotNone(
                    re.search(pattern, body, re.IGNORECASE | re.DOTALL)
                )

    def test_shipping_handoff_authorization_defers_to_current_intent(self):
        handoff = (ROOT / "skills" / "_shared" / "handoff-packet.md").read_text()
        rules = re.search(
            r"^## Rules\n(?P<body>.*?)(?=^## |\Z)",
            handoff,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(rules)
        assert rules is not None
        body = rules.group("body")

        contracts = {
            "handoff authorization is a snapshot": r"\bauthorization snapshot\b",
            "latest explicit instructions are consulted": (
                r"\b(?:latest|current) explicit user instructions\b"
            ),
            "clear restrictions apply immediately": (
                r"\bremove\b.*\b(?:narrow|revoke)\w*\b.*\bimmediately\b"
            ),
            "new actions require explicit expansion": (
                r"\badd\b.*\bbeyond\b.*\bsnapshot\b.*"
                r"\bonly\b.*\bnew explicit (?:user )?request\b.*\bnames?\b"
            ),
            "only ambiguity requires confirmation": (
                r"\bask for confirmation only\b.*\bcannot be mapped unambiguously\b"
            ),
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertIsNotNone(
                    re.search(pattern, body, re.IGNORECASE | re.DOTALL)
                )

    def test_pending_review_allows_only_explicit_pr_scaffolding(self):
        review = (ROOT / "skills" / "_shared" / "gates" / "review.md").read_text()
        shipping = (ROOT / "skills" / "shipping" / "SKILL.md").read_text()
        core = re.search(
            r"^## Core principle\n(?P<body>.*?)(?=^## |\Z)",
            shipping,
            re.MULTILINE | re.DOTALL,
        )
        hard_rules = re.search(
            r"^## Hard rules\n(?P<body>.*?)(?=^## |\Z)",
            shipping,
            re.MULTILINE | re.DOTALL,
        )
        pending = re.search(
            r"^## Pending review pointer\n(?P<body>.*?)(?=^## |\Z)",
            review,
            re.MULTILINE | re.DOTALL,
        )
        process = re.search(
            r"^## Process\n(?P<body>.*?)(?=^## |\Z)",
            shipping,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(core)
        self.assertIsNotNone(hard_rules)
        self.assertIsNotNone(pending)
        self.assertIsNotNone(process)
        assert core is not None
        assert hard_rules is not None
        assert pending is not None
        assert process is not None
        body = pending.group("body")

        contracts = {
            "explicit authorization": r"\bexplicit(?:ly)? authori[sz]",
            "PR review dependency": (
                r"\b(?:review requires? (?:the )?PR|PR is required for (?:the )?review)\b"
            ),
            "sole missing gate": r"\bsole missing gate\b",
            "proof and isolation pass": r"\bproof\b.*\bisolation\b.*\bpass\b",
            "commit scaffolding": r"\bcommit\b",
            "push scaffolding": r"\bpush\b",
            "draft PR scaffolding": r"\bdraft PR\b",
            "review remains pending": r"\breview gate\b.*\bpending\b",
            "final delivery remains blocked": (
                r"\b(?:block|must not|do not)\b.*"
                r"\bpackage\b.*\bmerge\b.*\btag\b.*\bpublish\b.*\brelease\b.*"
                r"\bdeploy\b.*\brepository handoff\b.*\bdestructive cleanup\b"
            ),
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertIsNotNone(
                    re.search(pattern, body, re.IGNORECASE | re.DOTALL)
                )
        exception_branch = re.search(
            r"^10\..*?(?P<body>review-enablement exception.*?)"
            r"(?=^11\. |\Z)",
            process.group("body"),
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(exception_branch)
        assert exception_branch is not None
        self.assertIsNotNone(
            re.search(
                r"\b(?:execute|perform)\b.*\bexception\b.*"
                r"\bterminal\b.*\bdelivery-action branch\b.*"
                r"\bskip\b.*\bstep 11\b.*"
                r"\b(?:continue|route)\b.*\bstep 12\b.*"
                r"\bafter\b.*\bcheckpoint\b.*\bstop\b.*"
                r"\bpending review gate handoff\b",
                exception_branch.group("body"),
                re.IGNORECASE | re.DOTALL,
            )
        )
        self.assertIsNotNone(
            re.search(
                r"\bfollow\b.*\bowning gate\b.*\bfail action\b",
                f"{core.group('body')}\n{hard_rules.group('body')}",
                re.IGNORECASE | re.DOTALL,
            )
        )
        self.assertIsNone(
            re.search(
                r"\b(?:if )?(?:any )?final checks? fail\b.*\babort\b",
                f"{core.group('body')}\n{hard_rules.group('body')}",
                re.IGNORECASE | re.DOTALL,
            )
        )

    def test_shipping_regates_new_artifacts_before_external_delivery(self):
        shipping = (ROOT / "skills" / "shipping" / "SKILL.md").read_text()
        process = re.search(
            r"^## Process\n(?P<body>.*?)(?=^## |\Z)",
            shipping,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(process)
        assert process is not None
        artifact_clause = re.search(
            r"^\s+- When a package action(?P<body>.*?)(?=^\s+- |^\d+\. |\Z)",
            process.group("body"),
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(artifact_clause)
        assert artifact_clause is not None
        body = f"When a package action{artifact_clause.group('body')}"

        contracts = {
            "new artifact trigger": r"\bpackage action\b.*\b(?:creates?|changes?)\b.*\bartifact\b",
            "actual artifact contents": r"\bactual artifact\b.*\bcontents?\b",
            "checksum": r"\bchecksums?\b",
            "signature": r"\bsignature\b",
            "target checks": r"\btarget-specific checks?\b",
            "proof and ship gates rerun": (
                r"\b(?:re-run|re-evaluate)\b.*\bproof\b.*\bship\b.*\bgates?\b"
            ),
            "dependent publication waits": (
                r"\bbefore\b.*\b(?:publish|publication)\b.*\brelease\b"
            ),
            "both gates pass on resulting artifact": (
                r"\bproceed only\b.*\bboth gates pass\b.*\b(?:that|resulting) artifact\b"
            ),
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertIsNotNone(
                    re.search(pattern, body, re.IGNORECASE | re.DOTALL)
                )

    def test_isolation_gate_supports_explicit_cleanup_mode(self):
        isolation = (ROOT / "skills" / "_shared" / "gates" / "isolation.md").read_text()
        shipping = (ROOT / "skills" / "shipping" / "SKILL.md").read_text()
        cleanup = re.search(
            r"^## Requested cleanup mode\n(?P<body>.*?)(?=^## |\Z)",
            isolation,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(cleanup)
        assert cleanup is not None
        body = cleanup.group("body")
        hard_exclusions = re.search(
            r"^4\. (?P<body>Hard exclusions fail unconditionally:.*)$",
            body,
            re.MULTILINE,
        )
        risk_states = re.search(
            r"^5\. (?P<body>Risk-acceptable states.*)$",
            body,
            re.MULTILINE,
        )
        pass_criterion = re.search(
            r"^Cleanup mode passes only (?P<body>.*)$",
            body,
            re.MULTILINE,
        )
        self.assertIsNotNone(hard_exclusions)
        self.assertIsNotNone(risk_states)
        self.assertIsNotNone(pass_criterion)
        assert hard_exclusions is not None
        assert risk_states is not None
        assert pass_criterion is not None

        hard_body = hard_exclusions.group("body")
        for exclusion in (
            "ambiguous",
            "broad",
            "glob-derived",
            "unresolved",
            "current workspace",
            "current worktree",
            "repository root",
            "protected path",
            "irrecoverable",
        ):
            with self.subTest(hard_exclusion=exclusion):
                self.assertIn(exclusion, hard_body)
        self.assertRegex(
            hard_body,
            r"\bapproval\b.*\bcannot\b.*\boverride\b.*\bhard exclusions\b",
        )

        risk_body = risk_states.group("body")
        for risk in (
            "dirty",
            "untracked",
            "unmerged",
            "unpushed",
            "active",
            "depended-upon",
        ):
            with self.subTest(risk_state=risk):
                self.assertIn(risk, risk_body)
        self.assertRegex(risk_body, r"\brecovery remains viable\b")
        self.assertRegex(risk_body, r"\bfresh explicit decision\b.*\bcurrent risk\b")

        pass_body = pass_criterion.group("body")
        self.assertIn("outside the hard exclusions", pass_body)
        for requirement in (
            "exact target",
            "explicit request",
            "state inspection",
            "dependencies",
            "recoverability",
            "restore path",
            "fresh decision",
        ):
            with self.subTest(cleanup_pass_requirement=requirement):
                self.assertIn(requirement, pass_body)
        self.assertIsNotNone(
            re.search(r"\brequested cleanup mode\b", shipping, re.IGNORECASE)
        )

    def test_shipping_packet_reports_action_execution_state(self):
        shipping = (ROOT / "skills" / "shipping" / "SKILL.md").read_text()

        def section(heading):
            return re.search(
                rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
                shipping,
                re.MULTILINE | re.DOTALL,
            )

        sections = {
            "Outcome contract": section("## Outcome contract"),
            "Output format": section("## Output format"),
        }
        contracts = {
            "authorized action set": r"\bauthorized action set\b",
            "attempted action exact target result": (
                r"\battempted actions?\b.*\bexact targets?\b.*\b(?:result|status)\b"
            ),
            "partial completion": r"\bpartial completion\b",
            "remaining or unattempted actions": (
                r"\b(?:remaining|unattempted) actions?\b"
            ),
            "recovery": r"\brecovery\b",
            "next step": r"\bnext step\b",
        }
        for source, match in sections.items():
            with self.subTest(source=source, section="present"):
                self.assertIsNotNone(match)
            assert match is not None
            body = match.group("body")
            for contract, pattern in contracts.items():
                with self.subTest(source=source, contract=contract):
                    self.assertIsNotNone(
                        re.search(pattern, body, re.IGNORECASE | re.DOTALL)
                    )

    def test_context_survey_step_one_supports_pure_reconnaissance(self):
        survey = (ROOT / "skills" / "context-survey" / "SKILL.md").read_text()
        process = re.search(
            r"^## Process\n(?P<body>.*?)(?=^## |\Z)",
            survey,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(process)
        assert process is not None
        step_one = re.search(r"^1\. (?P<body>.*)$", process.group("body"), re.MULTILINE)
        self.assertIsNotNone(step_one)
        assert step_one is not None
        body = step_one.group("body")

        contracts = {
            "requested understanding outcome": (
                r"\b(?:requested understanding outcome|repository reconnaissance)\b"
            ),
            "conditional downstream decision": (
                r"\b(?:downstream )?decision\b.*\b(?:when|if|where) applicable\b"
            ),
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertIsNotNone(re.search(pattern, body, re.IGNORECASE))

    def test_validator_reports_release_metadata_version_mismatches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(json.dumps({
                "name": "@static-var/keystone",
                "version": "1.9.9",
                "files": [],
                "pi": {"skills": ["./skills"]},
            }))
            (root / "packaging.allowlist").write_text("")
            (root / ".pi" / "extensions").mkdir(parents=True)
            (root / ".pi" / "extensions" / "keystone.ts").write_text(
                'readdirSync(skillsDir); skillDescription(skill); registerCommand(skill);'
            )
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin" / "plugin.json").write_text(json.dumps({
                "name": "keystone",
                "version": "1.9.9",
            }))
            (root / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
                "name": "keystone",
                "version": RELEASE_VERSION,
                "plugins": [{"name": "keystone", "version": "1.9.9"}],
            }))
            (root / ".codex-plugin").mkdir()
            (root / ".codex-plugin" / "plugin.json").write_text(json.dumps({
                "name": "keystone",
                "version": "1.9.9",
                "skills": "skills/",
            }))
            (root / ".agents" / "plugins").mkdir(parents=True)
            (root / ".agents" / "plugins" / "marketplace.json").write_text(json.dumps({
                "name": "keystone",
            }))

            errors = validate_keystone.metadata_errors(root)

        self.assertIn(f"package.json version must be {RELEASE_VERSION}", errors)
        self.assertIn(
            f".claude-plugin/plugin.json version must be {RELEASE_VERSION}",
            errors,
        )
        self.assertIn(
            ".claude-plugin/marketplace.json plugins[0].version must be "
            f"{RELEASE_VERSION}",
            errors,
        )
        self.assertIn(
            f".codex-plugin/plugin.json version must be {RELEASE_VERSION}",
            errors,
        )
        self.assertIn('.codex-plugin/plugin.json skills must be "./skills/"', errors)


if __name__ == "__main__":
    unittest.main()
