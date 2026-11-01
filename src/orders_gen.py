"""
Planted problems (see README.md):
  #1 Mixed date formats: some order_dt values are MM/DD/YYYY, others YYYY-MM-DD
  #3 Missing customer IDs: a few orders have a blank cust_id
  #4 Orphan lines: a few order lines point to an order_id that doesn't exist
  #8 Short file: on 2026-10-28, orders.csv has only about a third of the orders
  #9 Missing file: on 2026-10-29, orders.csv is not written at all
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)  # same seed every run -> same files every run

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = DATA_DIR / "company_b"

START_DATE = date(2026, 10, 26)
NUM_DAYS = 5                        # Oct 26 to Oct 30
SHORT_DAY = date(2026, 10, 28)      # #8
MISSING_DAY = date(2026, 10, 29)    # #9

# Products that also exist in Business Central (from items_gen.py)
CROSSWALK_PARTS = ["CHR-SYD-GRN", "DSK-ATH-001", "PRT-BC-003"]
ALPINE_ID = "B-9000"


def read_csv(path):
    """Read a CSV into a list of dictionaries, one per row."""
    if not path.exists():
        raise SystemExit(f"{path.name} not found. Run its generator first.")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_customers_and_items():
    customers = read_csv(DATA_DIR / "company_b" / "customers.csv")
    items = read_csv(DATA_DIR / "company_b" / "items.csv")

    customer_ids = []
    for row in customers:
        customer_ids.append(row["cust_id"])

    # part_no -> price. If a part appears twice (planted duplicate), the last price wins.
    prices = {}
    for row in items:
        prices[row["part_no"]] = float(row["list_price"])

    return customer_ids, prices


def make_orders_for_day(day, next_order_num, customer_ids, prices):
    """Build clean orders and lines for one day."""
    orders = []
    lines = []
    part_numbers = list(prices.keys())
    num_orders = random.randint(20, 30)

    for _ in range(num_orders):
        order_id = f"SO-B-{next_order_num}"
        next_order_num += 1

        orders.append({
            "order_id": order_id,
            "cust_id": random.choice(customer_ids),
            "order_dt": day.isoformat(),                                   # YYYY-MM-DD
            "ship_dt": (day + timedelta(days=random.randint(1, 5))).isoformat(),
        })

        num_lines = random.randint(1, 4)
        for line_no in range(1, num_lines + 1):
            part_no = random.choice(part_numbers)
            lines.append({
                "order_id": order_id,
                "line_no": line_no,
                "part_no": part_no,
                "qty": random.randint(1, 10),
                "unit_price": prices[part_no],
            })

    return orders, lines, next_order_num


def make_sure_matches_appear(orders, lines, prices):
    """Make sure Alpine Ski House and the 3 crosswalk products show up in the data,
    so silver has something to match."""
    orders[0]["cust_id"] = ALPINE_ID
    order_id = orders[0]["order_id"]

    for index in range(len(CROSSWALK_PARTS)):
        part_no = CROSSWALK_PARTS[index]
        if part_no in prices:
            lines.append({
                "order_id": order_id,
                "line_no": 10 + index,
                "part_no": part_no,
                "qty": random.randint(1, 5),
                "unit_price": prices[part_no],
            })
    print(f"  match check: {order_id} is Alpine Ski House ({ALPINE_ID}) "
          f"with the 3 crosswalk products")


def plant_mixed_dates(orders, day):
    """#1: switch about a quarter of order dates to MM/DD/YYYY."""
    count = 0
    for order in orders:
        if random.random() < 0.25:
            order["order_dt"] = day.strftime("%m/%d/%Y")
            count += 1
    print(f"  #1 mixed dates: {count} orders use MM/DD/YYYY")


def plant_missing_customers(orders):
    """#3: blank the cust_id on 2 orders (never the Alpine order)."""
    picked = random.sample(orders[1:], 2)
    for order in picked:
        order["cust_id"] = ""
        print(f"  #3 missing cust_id: {order['order_id']}")


def plant_orphan_lines(lines, prices):
    """#4: add 2 lines whose order_id doesn't exist in orders.csv."""
    part_numbers = list(prices.keys())
    for n in range(2):
        orphan_id = f"SO-B-{90000 + random.randint(0, 9999)}"
        part_no = random.choice(part_numbers)
        lines.append({
            "order_id": orphan_id,
            "line_no": 1,
            "part_no": part_no,
            "qty": random.randint(1, 10),
            "unit_price": prices[part_no],
        })
        print(f"  #4 orphan line: {orphan_id}")


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    customer_ids, prices = load_customers_and_items()
    next_order_num = 1001

    for offset in range(NUM_DAYS):
        day = START_DATE + timedelta(days=offset)
        print(f"{day}:")

        orders, lines, next_order_num = make_orders_for_day(
            day, next_order_num, customer_ids, prices)

        if offset == 0:
            make_sure_matches_appear(orders, lines, prices)

        plant_mixed_dates(orders, day)
        plant_missing_customers(orders)
        plant_orphan_lines(lines, prices)

        if day == SHORT_DAY:
            keep = len(orders) // 3
            print(f"  #8 short file: keeping {keep} of {len(orders)} orders")
            orders = orders[:keep]

        day_dir = OUT_DIR / day.isoformat()   
        day_dir.mkdir(parents=True, exist_ok=True)

        if day == MISSING_DAY:
            print("  #9 missing file: orders.csv not written today")
        else:
            write_csv(day_dir / "orders.csv", orders,
                      ["order_id", "cust_id", "order_dt", "ship_dt"])

        write_csv(day_dir / "order_lines.csv", lines,
                  ["order_id", "line_no", "part_no", "qty", "unit_price"])
        saved_orders = 0 if day == MISSING_DAY else len(orders)
        print(f"  saved {saved_orders} orders, {len(lines)} lines -> {day_dir}")


if __name__ == "__main__":
    main()