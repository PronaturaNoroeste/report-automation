"""Minimal DBF (dBase III) attribute-table reader.

The monthly ZIP ships track attributes in shapefile .dbf sidecars. We only
need the attribute rows — not the geometry — so a ~60-line parser avoids a
GDAL/geopandas dependency in the Docker image.
"""

import struct


def read_dbf(data: bytes) -> list[dict]:
    """Parse DBF bytes into a list of {field_name: value} dicts.

    Numeric fields ('N', 'F') become int/float (None when blank); logical
    fields ('L') become bool/None; everything else is a stripped string
    (None when blank). Deleted rows (marked '*') are skipped.
    """
    if len(data) < 32:
        raise ValueError("Not a DBF file: header truncated")

    n_records = struct.unpack("<I", data[4:8])[0]
    header_size = struct.unpack("<H", data[8:10])[0]
    record_size = struct.unpack("<H", data[10:12])[0]

    fields: list[tuple[str, str, int]] = []
    pos = 32
    while pos < header_size and data[pos] != 0x0D:
        name = data[pos:pos + 11].split(b"\0")[0].decode("ascii", "replace")
        ftype = chr(data[pos + 11])
        length = data[pos + 16]
        fields.append((name, ftype, length))
        pos += 32

    records: list[dict] = []
    for i in range(n_records):
        start = header_size + i * record_size
        raw = data[start:start + record_size]
        if len(raw) < record_size or raw[0:1] == b"*":
            continue
        offset = 1  # first byte is the deletion flag
        row: dict = {}
        for name, ftype, length in fields:
            text = raw[offset:offset + length].decode("latin-1").strip()
            offset += length
            row[name] = _convert(text, ftype)
        records.append(row)
    return records


def _convert(text: str, ftype: str):
    if not text or text.strip("*") == "":
        return None
    if ftype in ("N", "F"):
        try:
            return float(text) if ("." in text or "e" in text.lower()) else int(text)
        except ValueError:
            return None
    if ftype == "L":
        if text in "YyTt":
            return True
        if text in "NnFf":
            return False
        return None
    return text
