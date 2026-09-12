from core.conversion_facade import convert_batch
from core.interfaces.converter_interface import ConversionOptions
from tests._fakes import FakeConverter


def _make_files(tmp_path, n):
    files = []
    for i in range(n):
        p = tmp_path / f"input_{i}.foo"
        p.write_text(f"content-{i}")
        files.append(p)
    return files


def test_convert_batch_runs_all_files_and_reports_progress(tmp_path):
    files = _make_files(tmp_path, 3)
    conv = FakeConverter()
    progress_calls = []
    done_calls = []

    batch = convert_batch(
        files,
        conv,
        ConversionOptions(output_dir=tmp_path),
        on_progress=lambda done, total: progress_calls.append((done, total)),
        on_file_done=lambda result: done_calls.append(result),
    )

    assert batch.total == 3
    assert batch.success_count == 3
    assert progress_calls == [(1, 3), (2, 3), (3, 3)]
    assert len(done_calls) == 3


def test_convert_batch_stops_when_cancelled(tmp_path):
    files = _make_files(tmp_path, 5)
    conv = FakeConverter()
    seen = []

    batch = convert_batch(
        files,
        conv,
        ConversionOptions(output_dir=tmp_path),
        on_file_done=lambda result: seen.append(result),
        should_cancel=lambda: len(seen) >= 2,
    )

    assert batch.total == 2
    assert len(seen) == 2


def test_convert_batch_no_qt_required():
    """convert_batch, callback'ler olmadan da (None) çalışabilmeli."""
    batch = convert_batch([], FakeConverter(), ConversionOptions())
    assert batch.total == 0
    assert batch.all_succeeded is True
