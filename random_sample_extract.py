import csv
import random

# =========================================================
# CONFIG
# =========================================================

INPUT_CSV = "./Dados/tts_ready.csv"
OUTPUT_CSV = "./Dados/tts_ready_200.csv"

SAMPLE_SIZE = 100

# =========================================================
# LOAD CSV
# =========================================================

with open(INPUT_CSV, "r", encoding="utf-8") as infile:

    reader = csv.DictReader(infile)

    rows = list(reader)

# =========================================================
# VALIDATION
# =========================================================

total_rows = len(rows)

print("=" * 60)
print(f"TOTAL ROWS: {total_rows}")

if SAMPLE_SIZE > total_rows:
    raise Exception(
        f"SAMPLE_SIZE ({SAMPLE_SIZE}) is larger than total rows ({total_rows})"
    )

# =========================================================
# RANDOM SAMPLE
# =========================================================

sample_rows = random.sample(rows, SAMPLE_SIZE)

print(f"RANDOM SAMPLE SIZE: {len(sample_rows)}")
print("=" * 60)

# =========================================================
# PRESERVE ORIGINAL FIELDNAMES
# =========================================================

fieldnames = reader.fieldnames

# =========================================================
# WRITE OUTPUT
# =========================================================

with open(
    OUTPUT_CSV,
    "w",
    newline="",
    encoding="utf-8"
) as outfile:

    writer = csv.DictWriter(
        outfile,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for row in sample_rows:
        writer.writerow(row)

# =========================================================
# DONE
# =========================================================

print(f"Sample CSV generated: {OUTPUT_CSV}")
print("=" * 60)
