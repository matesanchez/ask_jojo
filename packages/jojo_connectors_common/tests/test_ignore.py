from jojo_connectors_common.ignore import JojoIgnore


def test_defaults_skip_office_lockfiles():
    ig = JojoIgnore.from_patterns([])
    assert ig.match("~$protocol.docx")
    assert ig.match(".DS_Store")
    assert ig.match("Thumbs.db")


def test_custom_patterns_override():
    ig = JojoIgnore.from_patterns(["drafts/", "*.bak"])
    assert ig.match("drafts", is_dir=True)
    assert ig.match("drafts/x.md")
    assert ig.match("scratch.bak")
    assert not ig.match("report.md")


def test_negation(tmp_path):
    # "!keep/" overrides a broader "drafts/" rule
    ig = JojoIgnore.from_patterns(["*.md", "!README.md"])
    assert ig.match("notes.md")
    assert not ig.match("README.md")


def test_rooted_patterns():
    # Use a name that isn't in defaults so we isolate rooted-vs-nested behavior.
    ig = JojoIgnore.from_patterns(["/release/"])
    assert ig.match("release", is_dir=True)
    assert ig.match("release/out.bin")
    # Rooted rule must NOT match a nested release/ directory.
    assert not ig.match("subdir/release/x.txt")


def test_from_file_reads_jojoignore(tmp_path):
    (tmp_path / ".jojoignore").write_text("# comment\nscratch/\n*.tmp\n")
    ig = JojoIgnore.from_file(tmp_path / ".jojoignore")
    assert ig.match("scratch", is_dir=True)
    assert ig.match("notes.tmp")
    assert not ig.match("notes.md")


# --------------------- with_extra: connector-side layering ----------------
# Connectors like PublicDriveConnector ship baseline ignore patterns the
# operator can't add to the source root's own .jojoignore (e.g. P:\\ where
# they have no write access). `with_extra` is the seam.


def test_with_extra_layers_additional_patterns(tmp_path):
    """`with_extra` returns a new ignore that also matches the extra rules."""
    (tmp_path / ".jojoignore").write_text("scratch/\n", encoding="utf-8")
    base = JojoIgnore.from_file(tmp_path / ".jojoignore")
    layered = base.with_extra(["*.D/"])

    # Original patterns still match.
    assert layered.match("scratch", is_dir=True)
    # New pattern matches an Agilent-style ChemStation directory.
    assert layered.match("Analytical/065-injection.D", is_dir=True)
    # Files of unrelated names still pass through.
    assert not layered.match("notes.md")


def test_with_extra_does_not_mutate_original(tmp_path):
    """The base ignore must be unchanged after with_extra returns."""
    base = JojoIgnore.from_patterns([])
    _ = base.with_extra(["*.D/"])
    # Base must NOT now match the layered pattern.
    assert not base.match("Analytical/065-injection.D", is_dir=True)


def test_with_extra_supports_negation():
    """A `!`-rule in extras can override a builtin pattern from the base.

    This is the safety valve that lets an operator un-ignore a builtin
    when their use case actually wants that subtree (gitignore semantics:
    later rules win).
    """
    base = JojoIgnore.from_patterns(["secrets/"])
    layered = base.with_extra(["!secrets/keep/"])
    assert base.match("secrets/private.txt")
    # Layered: explicit !secrets/keep/ un-ignores the keep/ subtree.
    assert not layered.match("secrets/keep/important.txt")
