from pathlib import Path

def fix_template_encoding():
    template_path = Path("templates/template_python.txt")
    # Read the content (let Python detect the encoding)
    content = template_path.read_text(encoding='utf-8', errors='replace')
    # Write back with UTF-8 encoding
    template_path.write_text(content, encoding='utf-8')

if __name__ == "__main__":
    fix_template_encoding() 