import sys
from pdfminer.high_level import extract_text

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pdf_to_text.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    try:
        text = extract_text(pdf_path)
        print(text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
