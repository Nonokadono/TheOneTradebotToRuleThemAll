import os
from pathlib import Path

def main():
    src_dir = r"C:\Users\tastb\Desktop\tradebot"
    extensions = {".py"}  # only Python files

    src_path = Path(src_dir).resolve()
    output_path = src_path / "SourceCode.txt"
    skip_dirs = {".git", "__pycache__", "logs", "data"}  # add more if needed

    with open(output_path, "w", encoding="utf-8") as out_file:
        for file_path in src_path.rglob("*"):
            if any(part in skip_dirs for part in file_path.parts):
                continue
            if (
                file_path.is_file()
                and file_path.suffix.lower() in extensions
                and file_path != output_path
            ):
                out_file.write("=" * 80 + "\n")
                out_file.write(f"FILE: {file_path.relative_to(src_path)}\n")
                out_file.write("-" * 80 + "\n")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        out_file.write(f.read())
                except Exception as e:
                    out_file.write(f"[ERROR reading file: {e}]\n")
                out_file.write("\n" + "=" * 80 + "\n\n")

    print(f"Source code written to: {output_path}")

if __name__ == "__main__":
    main()



