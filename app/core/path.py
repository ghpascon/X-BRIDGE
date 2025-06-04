import sys
from pathlib import Path

def get_path(relative_path: str) -> Path:
    """
    Retorna o caminho absoluto do arquivo ou diretório, levando em consideração se o
    aplicativo está sendo executado como um script normal ou como um executável.

    :param relative_path: Caminho relativo do arquivo ou diretório.
    :return: Caminho absoluto correto.
    """
    if getattr(sys, 'frozen', False):
        # Quando o aplicativo é executado como executável (PyInstaller)
        base_path = Path(sys._MEIPASS)  # O diretório temporário onde o executável é descompactado
    else:
        # Quando o aplicativo está sendo executado do código-fonte
        base_path = Path(sys.argv[0]).resolve().parent  # O diretório onde o script foi executado

    return base_path / relative_path
