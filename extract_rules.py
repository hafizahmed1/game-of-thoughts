from pypdf import PdfReader

pdf_path = "data/raw/connect_four/rules.pdf"   # path to your pdf
output_path = "data/raw/connect_four/rules.txt"

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Rules extracted and saved to:", output_path)