from core.interfaces.converter_interface import ConversionOptions
from tests._fakes import FakeConverter


def test_validate_rejects_wrong_extension(tmp_path):
    conv = FakeConverter()
    wrong = tmp_path / "input.txt"
    wrong.write_text("x")

    assert conv.validate(wrong) is False


def test_validate_rejects_missing_file(tmp_path):
    conv = FakeConverter()
    missing = tmp_path / "ghost.foo"

    assert conv.validate(missing) is False


def test_convert_success_writes_output(tmp_path):
    conv = FakeConverter()
    source = tmp_path / "input.foo"
    source.write_text("hello")

    result = conv.convert(source, ConversionOptions(output_dir=tmp_path))

    assert result.success is True
    assert result.output_path == tmp_path / "input.bar"
    assert result.output_path.read_text() == "hello"
    assert result.error_message == ""


def test_convert_reports_unavailable_hint(tmp_path):
    conv = FakeConverter(available=False)
    source = tmp_path / "input.foo"
    source.write_text("hello")

    result = conv.convert(source, ConversionOptions(output_dir=tmp_path))

    assert result.success is False
    assert result.error_message == conv.unavailable_hint


def test_convert_wraps_exception_as_failure(tmp_path):
    conv = FakeConverter(raise_error=True)
    source = tmp_path / "input.foo"
    source.write_text("hello")

    result = conv.convert(source, ConversionOptions(output_dir=tmp_path))

    assert result.success is False
    assert "boom" in result.error_message
    assert result.output_path is None


def test_convert_rejects_invalid_file(tmp_path):
    conv = FakeConverter()
    wrong = tmp_path / "input.txt"
    wrong.write_text("x")

    result = conv.convert(wrong, ConversionOptions(output_dir=tmp_path))

    assert result.success is False
    assert "Geçersiz dosya" in result.error_message
