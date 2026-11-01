
import csv
import json
import random
from pathlib import Path

"""Generate Company B's items.csv with planted data quality problems.

Planted problems (see docs/company_b_answer_key.md):
  #2 Duplicate part number: one part_no appears twice with different prices
  #5 Messy units: some uom values are 'ea' or 'Each' instead of 'EA'
  #6 Same product, different number: 3 Company B parts are really
     Business Central items, listed under Company B part numbers
"""

random.seed(42)  # same seed every run -> same file every run

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
OUT_FILE = DATA_DIR / "items.csv"

NUM_CLEAN_ITEMS = 25

# Words used to build furniture and office product descriptions
MATERIALS = ["Oak", "Walnut", "Steel", "Maple", "Glass", "Bamboo", "Leather", "Mesh"]
PRODUCTS = ["Desk", "Office Chair", "Bookshelf", "Filing Cabinet", "Conference Table",
            "Desk Lamp", "Monitor Stand", "Storage Bench", "Side Table", "Coat Rack"]
COLORS = ["Black", "White", "Gray", "Natural", "Blue", "Green"]

# Planted problem #6: Business Central item number -> Company B part number
# The first two are fixed. The third is picked from items.json in add_bc_matches().
CROSSWALK = {
    "2000-S": "CHR-SYD-GRN",   # SYDNEY Swivel Chair, green
    "1896-S": "DSK-ATH-001",   # ATHENS Desk
}
THIRD_ITEM_B_PART = "PRT-BC-003"   # Company B part number for the third item


def load_bc_items():
    """Read items.json from the newest Business Central extract folder."""
    bc_dir = DATA_DIR / "business_central"
    if not bc_dir.exists():
        raise SystemExit("No Business Central extract found. check the DATA_DIR")

    folders = []
    for p in bc_dir.iterdir():     # everything inside data/business_central
        if p.is_dir():             # keep only the dated folders
            folders.append(p)

    if not folders:
        raise SystemExit("No Business Central extract found. Run the extract script first.(There is not file like that)")

    folders.sort()                 # YYYY-MM-DD names sort in time order
    latest = folders[-1]           # newest extract

    with open(latest / "items.json", encoding="utf-8") as f:
        return json.load(f)


def make_clean_items():
    """Build Company B's normal product list."""
    items = []
    for i in range(1, NUM_CLEAN_ITEMS + 1):
        # use the material from line 22 - 27
        material = random.choice(MATERIALS) 
        product = random.choice(PRODUCTS)
        color = random.choice(COLORS)

        items.append({
            "part_no": f"PRT-{1000 + i}",
            "part_desc": f"{material} {product}, {color}",
            "uom": "EA", #unit of measure EA: each, one single item
            
            "list_price": round(random.uniform(25, 1500), 2),
        })
    return items


def plant_messy_uom(items):
    """#5: change 4 units of measure to inconsistent spellings."""
    bad_spellings = ["ea", "Each", "ea", "Each"]
    picked = random.sample(items[:NUM_CLEAN_ITEMS], 4)

    for index in range(len(picked)):
        item = picked[index]
        item["uom"] = bad_spellings[index]
        print(f"  #5 messy uom: {item['part_no']} -> {item['uom']}")
    return items


def plant_duplicate(items):
    """#2: copy one existing part and give the copy a higher price."""
    original = random.choice(items[:NUM_CLEAN_ITEMS])

    duplicate = dict(original)     # copy, so the original row isn't changed
    duplicate["list_price"] = round(original["list_price"] * 1.15, 2)
    items.append(duplicate)

    print(f"  #2 duplicate part_no: {original['part_no']} "
          f"({original['list_price']} and {duplicate['list_price']})")
    return items


def add_bc_matches(items, bc_items):
    """#6: add Business Central products under Company B part numbers."""
    # Build a lookup: Business Central item number -> full item record
    by_number = {}
    for bc_item in bc_items:
        by_number[bc_item["number"]] = bc_item

    # Pick the third item: the first Business Central item not already in CROSSWALK
    third = None
    for bc_item in bc_items:
        if bc_item["number"] not in CROSSWALK:
            third = bc_item
            break

    if third is None:
        raise SystemExit("items.json has no third item to use.")

    # Full crosswalk = the two fixed pairs plus the third
    crosswalk = dict(CROSSWALK)
    crosswalk[third["number"]] = THIRD_ITEM_B_PART

    for bc_number, b_part in crosswalk.items():
        if bc_number not in by_number:
            raise SystemExit(f"Business Central item {bc_number} not found in items.json.")
        bc = by_number[bc_number]

        # Reword the name slightly, the way a different system would store it
        b_desc = bc["displayName"].title().replace(",", " -")

        items.append({
            "part_no": b_part,
            "part_desc": b_desc,
            "uom": "EA",
            "list_price": bc["unitPrice"],
        })
        print(f"  #6 crosswalk: {b_part} = Business Central {bc_number} ({bc['displayName']})")
    return items


def save(items):
    """Write all rows to data/items.csv."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["part_no", "part_desc", "uom", "list_price"])
        writer.writeheader()
        for row in items:
            writer.writerow(row)
    print(f"Saved {len(items)} rows -> {OUT_FILE}")


def main():
    items = make_clean_items()
    print("Planted problems:")
    items = plant_messy_uom(items)
    items = plant_duplicate(items)
    items = add_bc_matches(items, load_bc_items())
    save(items)


if __name__ == "__main__":
    main()