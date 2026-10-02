#!/usr/bin/env python3
"""Measure text-file line endings and byte-level metadata without showing content."""

import argparse
import sys
from pathlib import Path

CHUNK_SIZE = 64 * 1024
BOMS = (
    (b"\x00\x00\xfe\xff", "UTF-32 BE"),
    (b"\xff\xfe\x00\x00", "UTF-32 LE"),
    (b"\xef\xbb\xbf", "UTF-8"),
    (b"\xfe\xff", "UTF-16 BE"),
    (b"\xff\xfe", "UTF-16 LE"),
)


def measure(path):
    with path.open("rb") as source:
        prefix = source.read(4)
        bom = next((name for marker, name in BOMS if prefix.startswith(marker)), "none")
        source.seek(0)

        byte_count = crlf_count = lf_count = cr_count = 0
        previous_chunk_ended_cr = False
        last_byte = None

        while True:
            chunk = source.read(CHUNK_SIZE)
            if not chunk:
                break

            byte_count += len(chunk)
            chunk_crlf = chunk.count(b"\r\n")
            chunk_lf = chunk.count(b"\n") - chunk_crlf
            chunk_cr = chunk.count(b"\r") - chunk_crlf

            if previous_chunk_ended_cr and chunk.startswith(b"\n"):
                chunk_crlf += 1
                chunk_lf -= 1
                chunk_cr -= 1

            crlf_count += chunk_crlf
            lf_count += chunk_lf
            cr_count += chunk_cr
            previous_chunk_ended_cr = chunk.endswith(b"\r")
            last_byte = chunk[-1]

    terminators = crlf_count + lf_count + cr_count
    if byte_count == 0:
        line_count = 0
    elif last_byte in (10, 13):
        line_count = terminators
    else:
        line_count = terminators + 1

    return {
        "bytes": byte_count,
        "lines": line_count,
        "crlf": crlf_count,
        "lf": lf_count,
        "cr": cr_count,
        "final_newline": byte_count > 0 and last_byte in (10, 13),
        "bom": bom,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Count file bytes, line endings, and BOMs without printing file contents."
    )
    parser.add_argument("files", nargs="+", type=Path, help="one or more files to inspect")
    args = parser.parse_args()
    failed = False

    for path in args.files:
        try:
            result = measure(path)
        except OSError as error:
            print(f"line-meter: {path}: {error}", file=sys.stderr)
            failed = True
            continue

        final_newline = "yes" if result["final_newline"] else "no"
        print(
            f"{path}: bytes={result['bytes']} lines={result['lines']} "
            f"CRLF={result['crlf']} LF={result['lf']} CR={result['cr']} "
            f"final-newline={final_newline} BOM={result['bom']}"
        )

    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
