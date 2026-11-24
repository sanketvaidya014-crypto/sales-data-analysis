# Sales Data Analysis with Python and SQL

A reproducible starter project: clean a line-item sales CSV with Python, load SQLite, and answer ten business questions in SQL. No real dataset has been supplied; no business findings are claimed.

## Run
Use Python 3.10+ with pandas and SQLite 3.25+.

```sh
pip install -r requirements.txt
python pipeline.py --input data/raw/sales.csv --date-format "%Y-%m-%d" --output artifacts
```
Use `%d/%m/%Y` only for confirmed day/month/year dates. Output files are replaced on rerun.

## Input
Required columns: order_id, order_date, product, quantity, unit_price.
Optional: customer_id, category, region.
One row = one order line. Order IDs must be globally unique per order. Use one currency and consistent product identifiers. Unit prices must be numeric, without currency symbols or thousands separators. Discounts must already be reflected in unit_price; otherwise revenue represents list-price extensions.

## Cleaning and audit
Trim text; preserve identifiers as text; explicitly parse dates; quarantine missing order/product, invalid dates, nonpositive/fractional quantities, invalid or negative prices, and conflicting order dates/customer/region. Zero-price promotions are retained. Missing category and region become Unknown; missing customer IDs remain null. Suspected duplicate lines are retained and exported for review, since identical lines may be legitimate. Negative returns are quarantined, not subtracted: this is positive-sales analysis, not net revenue. No profit claims without costs. Outliers require review. Revenue uses two-decimal rounding with floating-point storage; use integer minor units or decimal types for accounting-grade reconciliation.

## Ten business questions
1. What are revenue, orders, units, identified customers, and average order value?
2. How does monthly revenue grow?
3. Which ten products lead by revenue?
4. What is each category's revenue contribution?
5. How do regions compare on revenue, orders, and AOV?
6. Which ten identified customers generate most revenue?
7. What share of identified customers repeat within the extract?
8. How do weekday sales compare?
9. How does order value vary with basket size?
10. How concentrated is product revenue?

## Outputs
clean_sales.csv, rejected_rows.csv, possible_duplicates.csv, quality_report.json, sales.db, and ten query_results CSVs.

## Metric caveats
AOV = revenue / distinct orders, not average line revenue. Repeat rate excludes missing customer IDs and is not cohort retention. Monthly growth is null for the first month or calendar gaps; partial months are not corrected. Weekday averages use observed sales dates, not all operating dates. Category/region totals include Unknown. Revenue is not profit. Returns need a separate ledger. Do not publish customer identifiers or confidential files.

## Quality gates
Input = accepted + rejected; Python/SQLite accepted-row and revenue totals reconcile. Review rejection rates, duplicates, coverage, partial periods, and source totals before business conclusions.

## Suggested final report
Document dataset source/license, currency, period, grain, and exclusions. Show real quality counts, ten SQL answers, a monthly trend chart and product ranking. Link each recommendation to an observed result and explain limitations. Keep current status as a starter until real data is analyzed.
