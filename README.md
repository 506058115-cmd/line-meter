# line-meter

Inspect file size, line-ending counts, final-newline state, and common Unicode byte-order marks. It reads files as bytes and never prints their contents.

Requires Python 3.8+ and uses only the standard library.

    python line_meter.py README.md src/main.py

Each file gets one summary with its byte count, physical line count, CRLF/LF/CR counts, final-newline state, and detected BOM (or none). Counts are byte-level; the tool does not decode or validate file text. Unreadable files are reported while the remaining inputs are still processed.

Exit status: 0 when every file was read, 2 when one or more files could not be read.

## License

MIT. See [LICENSE](LICENSE).
