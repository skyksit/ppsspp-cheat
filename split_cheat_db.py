import os
import re
from pathlib import Path
from collections import OrderedDict


def sanitize_s_code_to_filename(s_line: str) -> str | None:
    """Extract game code from an `_S` line and return a safe filename like ULUS10080.ini.

    Returns None if a safe name cannot be derived.
    """
    # Split by whitespace after `_S`
    parts = s_line.strip().split()
    if len(parts) < 2:
        return None
    game_code = parts[1]
    # Remove hyphens
    game_code = game_code.replace("-", "")
    # Keep only safe filename chars (alnum, underscore, dot, dash)
    game_code_safe = re.sub(r"[^A-Za-z0-9._-]", "", game_code)
    if not game_code_safe:
        return None
    return f"{game_code_safe}.ini"


def split_cheat_db(input_path: Path, output_dir: Path) -> int:
    """Read cheat.db and write .ini files per `_S` block into output_dir.

    - Dedupe identical blocks per file (same exact text) preserving first occurrence order.
    - Overwrite existing files instead of appending to avoid historical duplicates.

    Returns the number of files written/updated.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    files_written = 0
    current_block_lines = []  # type: list[str]
    current_filename = None  # type: str | None
    unknown_index = 1

    # Accumulate unique blocks per file while preserving insertion order
    file_to_blocks: "OrderedDict[str, list[str]]" = OrderedDict()
    file_to_seen_blocks: dict[str, set[str]] = {}

    def add_block_to_map():
        nonlocal current_block_lines, current_filename, unknown_index
        if not current_block_lines:
            return
        filename = current_filename
        if not filename:
            filename = f"UNKNOWN_{unknown_index:04}.ini"
            unknown_index += 1
        block_text = "".join(current_block_lines)
        if filename not in file_to_blocks:
            file_to_blocks[filename] = []
            file_to_seen_blocks[filename] = set()
        if block_text not in file_to_seen_blocks[filename]:
            file_to_blocks[filename].append(block_text)
            file_to_seen_blocks[filename].add(block_text)
        current_block_lines = []
        current_filename = None

    # Read preserving original lines as much as possible
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            stripped_lead = line.lstrip()
            # A new block starts when we see a line whose trimmed beginning starts with `_S`
            if stripped_lead.startswith("_S"):
                # If we already have a block, store it first
                add_block_to_map()
                # Start a new block
                current_block_lines = [line]
                current_filename = sanitize_s_code_to_filename(stripped_lead)
            else:
                # Only add lines if we're inside a block
                if current_filename is not None:
                    current_block_lines.append(line)

    # Store last block if present
    add_block_to_map()

    # Write files (overwrite) with deduped content
    for filename, blocks in file_to_blocks.items():
        target_file = output_dir / filename
        with open(target_file, "wb") as f_out:
            f_out.write("".join(blocks).encode("utf-8", errors="ignore"))
        files_written += 1

    return files_written


def main():
    project_root = Path(__file__).resolve().parent
    input_path = project_root / "cheat.db"
    output_dir = project_root / "output"
    count = split_cheat_db(input_path, output_dir)
    print(f"Done. Wrote/updated {count} files in '{output_dir}'.")


if __name__ == "__main__":
    main()


