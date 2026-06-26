import tabula
import os

print("Script started...")

pdf_path = "morth_traffic.pdf"

print("Checking if PDF exists...")
print("Exists:", os.path.exists(pdf_path))

print("Reading tables from PDF...")

tables = tabula.read_pdf(
    pdf_path,
    pages="all",
    multiple_tables=True,
    lattice=True
)

print("Total tables found:", len(tables))

for i, table in enumerate(tables):
    file_name = f"table_{i}.csv"
    table.to_csv(file_name, index=False)
    print(f"Saved {file_name}")

print("Script finished.")
