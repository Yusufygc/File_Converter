from ui.file_discovery import collect_files


def test_collects_matching_files_recursively(tmp_path):
    (tmp_path / "a.pdf").write_text("x")
    sub = tmp_path / "alt"
    sub.mkdir()
    (sub / "b.pdf").write_text("x")
    (sub / "c.txt").write_text("x")  # eşleşmemeli

    result = collect_files(tmp_path, [".pdf"])

    assert result == sorted([tmp_path / "a.pdf", sub / "b.pdf"])


def test_case_insensitive_extension_match(tmp_path):
    (tmp_path / "upper.PDF").write_text("x")

    result = collect_files(tmp_path, [".pdf"])

    assert result == [tmp_path / "upper.PDF"]


def test_empty_directory_returns_empty_list(tmp_path):
    assert collect_files(tmp_path, [".pdf"]) == []


def test_no_matching_files_returns_empty_list(tmp_path):
    (tmp_path / "a.txt").write_text("x")

    assert collect_files(tmp_path, [".pdf"]) == []


def test_multiple_accepted_extensions(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    (tmp_path / "b.jpeg").write_text("x")
    (tmp_path / "c.png").write_text("x")

    result = collect_files(tmp_path, [".jpg", ".jpeg"])

    assert result == sorted([tmp_path / "a.jpg", tmp_path / "b.jpeg"])
