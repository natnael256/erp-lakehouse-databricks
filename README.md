# ERP Lakehouse on Databricks

I'm combining ERP data from two companies in one Databricks lakehouse. Company A runs Business Central. Company B is an acquired business whose old system only exports CSV files.

## Status
- [x] Business Central extract (customers, items, sales orders, sales invoices)
- [x] Company B customers and items, with planted data problems
- [ ] Company B orders and order lines
- [ ] Upload to Databricks and build bronze
- [ ] Silver, quality checks, dashboard

## How It Works
1. A Python script pulls Business Central data through its API and saves JSON files.
2. Python scripts generate Company B's messy CSV files.
3. Both get uploaded to a Databricks volume, then loaded into bronze, silver and gold.

The extract runs on my laptop because Databricks Free Edition blocks most outside websites.

## Planted Data Problems
Company B's data has problems on purpose, so I can find and fix them in silver.

| Problem | File |
|---|---|
| Alpine Ski House is B-9000 in Company B and 40000 in Business Central | customers.csv |
| 3 products have different part numbers in each company | items.csv |
| One duplicate part number with two prices | items.csv |
| Units spelled `EA`, `ea` and `Each` | items.csv |

## Repo Structure
```
api_test/api_test.py         Business Central extract
src/faker_customers_gen.py   Company B customers
src/items_gen.py             Company B items
data/                        Output files ( in gitignore) will not be commited. 
```

## Next Steps
1. Generate Company B orders and order lines
2. Upload both sources to Databricks
3. Build bronze and silver