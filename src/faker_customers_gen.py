"""Generate Company B's customers.csv with Faker.

Planted problem (see README.md):
  #7 Same customer, different ID: B-9000 Alpine Ski House Inc is
     the same customer as Business Central customer 40000
"""
import csv
from pathlib import Path

from faker import Faker

Faker.seed(2)  # same seed every run -> same file every run
fake = Faker()

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = REPO_ROOT / "data" / "company_b" / "customers.csv"

NUM_CUSTOMERS = 40


def make_customers():
    """Build 40 fake customers plus the planted Alpine Ski House."""
    customers = []
    for _ in range(NUM_CUSTOMERS):
        customers.append({
            "cust_id": fake.unique.numerify("B-####"),
            "cust_nm": fake.company(),
            "city": fake.city(),
            "state": fake.state(),
            "email": fake.email(),
        })

    # #7: same customer as Business Central 40000, under a Company B ID
    customers.append({
        "cust_id": "B-9000",
        "cust_nm": "Alpine Ski House Inc",
        "city": fake.city(),
        "state": fake.state(),
        "email": fake.email(),
    })
    return customers


def save(customers):
    """Write all rows to data/company_b/customers.csv."""
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["cust_id", "cust_nm", "city", "state", "email"])
        writer.writeheader()
        for row in customers:
            writer.writerow(row)
    print(f"Saved {len(customers)} rows -> {OUT_FILE}")


def main():
    save(make_customers())


if __name__ == "__main__":
    main()