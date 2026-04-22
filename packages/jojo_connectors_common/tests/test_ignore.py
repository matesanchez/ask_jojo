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
