from backend.app.ingestion.file_scanner import scan_repository


def test_scan_repository():
    files = scan_repository(
        "data/repositories/psf__requests"
    )

    assert len(files) > 0

    for file in files:
        assert "file_path" in file
        assert "language" in file
        assert "size" in file