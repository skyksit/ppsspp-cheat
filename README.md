## PPSSPP Cheat DB Splitter

Split a PPSSPP `cheat.db` into per-game `.ini` files using `_S` blocks.

### Overview
- **Input**: `cheat.db` in the project root
- **Split rule**: Each block starts at a line beginning with `_S` and ends right before the next `_S`
- **Output**: `.ini` files under the `output/` folder (auto-created on run)
- **Filename rule**: Remove hyphens from the `_S` game code and keep only safe characters
  - Example: `_S ULUS-10080` → `ULUS10080.ini`
  - If the code is missing/invalid, use `UNKNOWN_####.ini`
- **De-duplication**: Identical block texts are written only once per file (first occurrence wins)
- **Write mode**: Overwrites files on each run to keep results clean

### cheat.db format
- `_S`: Game code (used as output filename seed)
- `_G`: Game title
- `_C0`: Cheat name/label
- `_L`: Cheat line (address/value)

Example input snippet:

```text
_S ULUS-10080
_G 007: From Russia With Love [US]
_C0 Handheld Screen (3:2)
_L 0x2024DA44 0x3F9851EC
... (omitted)
```

→ Output file: `output/ULUS10080.ini`

### Requirements
- Python 3.8+
- OS: Windows, macOS, Linux

### Usage
Run from the project root:

```powershell
python .\split_cheat_db.py
```

The script prints the number of files written/updated, and results are saved under `output/`.

### Implementation notes
- Lines beginning with `_S` (ignoring leading spaces) start a new block.
- Block text is written as-is to preserve spacing and newlines from the source.
- Filenames allow only letters, digits, underscore, dot, and dash; others are removed.
- Multiple blocks targeting the same file are merged with duplicates removed by exact-text match.

### FAQ
- Why do I still see duplicates?
  - Ensure you re-ran the script and reloaded files in your editor. Current version deduplicates per file.
- Invalid characters in filenames cause errors
  - The script sanitizes names. If it still cannot derive a code, it uses `UNKNOWN_####.ini`.
- Rebuild outputs from scratch
  - Delete the `output/` folder and run the script again.

### License
The script is provided for general use and modification. Please comply with the original data (`cheat.db`) distribution and usage policies applicable to your region.
