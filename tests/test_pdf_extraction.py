"""
Tests para el extractor de PDFs.
"""

import pytest
from pathlib import Path
from app.core.pdf_extractor import PDFExtractor


@pytest.fixture
def pdf_extractor():
    """Fixture del extractor."""
    return PDFExtractor()


@pytest.fixture
def sample_pdf_path():
    """Fixture con ruta a PDF de ejemplo."""
    # Usar uno del dataset
    base_path = Path("Fichas y documentación")
    sample = base_path / "Arrigorriaga (vizcaya) - Emergencia Social" / "Convocatoria Arrigorriaga Emergencia Social.pdf"

    if sample.exists():
        return sample
    return None


def test_extract_text_basic(pdf_extractor, sample_pdf_path):
    """Test básico de extracción de texto."""
    if sample_pdf_path is None:
        pytest.skip("PDF de ejemplo no encontrado")

    text = pdf_extractor.extract_text(sample_pdf_path)

    assert text is not None
    assert len(text) > 100
    assert isinstance(text, str)


def test_extract_metadata(pdf_extractor, sample_pdf_path):
    """Test de extracción de metadatos."""
    if sample_pdf_path is None:
        pytest.skip("PDF de ejemplo no encontrado")

    metadata = pdf_extractor.extract_metadata(sample_pdf_path)

    assert "filename" in metadata
    assert "pages" in metadata
    assert "size_mb" in metadata
    assert metadata["pages"] > 0


def test_extract_tables(pdf_extractor, sample_pdf_path):
    """Test de extracción de tablas."""
    if sample_pdf_path is None:
        pytest.skip("PDF de ejemplo no encontrado")

    tables = pdf_extractor.extract_tables(sample_pdf_path)

    assert isinstance(tables, list)
    # Puede o no tener tablas


def test_clean_text(pdf_extractor):
    """Test de limpieza de texto."""
    raw_text = "Test   con    espacios\n\n\n\nmúltiples\t\ttabs"
    cleaned = pdf_extractor.clean_text(raw_text)

    assert "   " not in cleaned
    assert "\t" not in cleaned
    assert "\n\n\n" not in cleaned


def test_invalid_pdf(pdf_extractor, tmp_path):
    """Test con archivo inválido."""
    # Crear archivo falso
    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_text("This is not a PDF")

    with pytest.raises(Exception):
        pdf_extractor.extract_text(fake_pdf)


def test_nonexistent_pdf(pdf_extractor):
    """Test con archivo inexistente."""
    with pytest.raises(FileNotFoundError):
        pdf_extractor.extract_text("nonexistent.pdf")
