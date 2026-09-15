"""
Dosya Türü İkon Eşlemesi
=========================
`FileListWidget`'ın dönüşüm için sürüklenen dosyanın uzantısına göre
doğru ikonu göstermesini sağlar. Önceden ikon her zaman sabit
`file_pptx.svg` idi — dosya türünden bağımsızdı.

Bilinmeyen bir uzantı (henüz ikonu eklenmemiş yeni bir converter)
`file_generic` ikonuna düşer, hata fırlatmaz — tak-çıkar mimariyle
tutarlı: yeni converter eklerken özel bir ikon eklemek zorunlu değil,
opsiyonel bir iyileştirmedir.
"""

from __future__ import annotations

from pathlib import Path

from core.utils.resource_helper import get_resource_path

_EXTENSION_ICONS = {
    ".pptx": "file_pptx",
    ".pdf": "file_pdf",
    ".jpg": "file_jpg",
    ".jpeg": "file_jpg",
}
_DEFAULT_ICON = "file_generic"

_ICON_DIR = "assets/icons"


def icon_name_for(suffix: str) -> str:
    """Dosya uzantısına karşılık gelen ikon temel adını döndürür (uzantısız)."""
    return _EXTENSION_ICONS.get(suffix.lower(), _DEFAULT_ICON)


def icon_path_for(suffix: str) -> str:
    """
    Dosya uzantısına karşılık gelen ikonun tam yolunu döndürür.
    Önce `.svg` denenir (mevcut varlıkların çoğu bu formatta); yoksa
    `.png`'ye düşer (örn. `file_pdf` yalnızca `.png` olarak mevcut).
    """
    basename = icon_name_for(suffix)
    svg_path = get_resource_path(f"{_ICON_DIR}/{basename}.svg")
    if Path(svg_path).exists():
        return svg_path
    return get_resource_path(f"{_ICON_DIR}/{basename}.png")
