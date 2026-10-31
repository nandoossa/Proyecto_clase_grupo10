"""Pruebas de la carga de datos originales (sin conexión a internet)."""
import pandas as pd

from proyecto.data.load import RAW_FILENAME, load_raw_saber11


def _fake_source(tmp_path):
    """Crea un CSV que hace las veces de la fuente remota y devuelve su URL file://."""
    source = tmp_path / "fuente.csv"
    pd.DataFrame({"estu_consecutivo": ["A1", "A2"], "punt_global": [250, 300]}).to_csv(source, index=False)
    return source, source.as_uri()


def test_downloads_when_file_is_missing(tmp_path):
    source, url = _fake_source(tmp_path)
    raw_dir = tmp_path / "data" / "raw"

    df = load_raw_saber11(raw_dir, url=url)

    saved = raw_dir / RAW_FILENAME
    assert saved.exists()
    assert saved.read_bytes() == source.read_bytes()  # se guarda sin modificar
    assert not (raw_dir / (RAW_FILENAME + ".part")).exists()
    assert df["punt_global"].tolist() == [250, 300]


def test_uses_local_copy_without_downloading(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    pd.DataFrame({"punt_global": [111]}).to_csv(raw_dir / RAW_FILENAME, index=False)

    # Una URL inválida demuestra que no se intenta descargar si el archivo ya existe.
    df = load_raw_saber11(raw_dir, url="file:///no/existe.csv")

    assert df["punt_global"].tolist() == [111]
