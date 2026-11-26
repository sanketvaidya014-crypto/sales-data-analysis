import argparse
import json
import sqlite3
from pathlib import Path
import pandas as pd


def run(source, destination, date_format):
    out = Path(destination)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(source, dtype="string", keep_default_na=False)
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
    if df.columns.duplicated().any():
        raise ValueError("Duplicate normalized column names")
    required = {"order_id", "order_date", "product", "quantity", "unit_price"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing columns: {sorted(required - set(df.columns))}")
    for col in df:
        df[col] = df[col].str.strip().replace("", pd.NA)
    df.insert(0, "source_row", range(2, len(df)+2))
    raw = df.copy()
    for col in ["customer_id", "category", "region"]:
        if col not in df:
            df[col] = pd.NA
    df["order_date"] = pd.to_datetime(df["order_date"], format=date_format, errors="coerce")
    for col in ["quantity", "unit_price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    reasons = pd.Series("", index=df.index, dtype="string")
    checks = {
        "missing_order_id": df.order_id.isna(),
        "missing_product": df['product'].isna(),
        "invalid_date": df.order_date.isna(),
        "invalid_quantity": df.quantity.isna() | ~df.quantity.between(1, 1e12) | (df.quantity % 1 != 0),
        "invalid_price": df.unit_price.isna() | ~df.unit_price.between(0, 1e12)
    }
    conflict = set()
    for col in ["order_date", "customer_id", "region"]:
        counts = df.groupby("order_id")[col].nunique()
        conflict.update(counts[counts > 1].index)
    checks["conflicting_order_attributes"] = df.order_id.isin(conflict)
    for reason, mask in checks.items():
        mask = mask.fillna(True)
        reasons.loc[mask] += reason + ";"
    valid = reasons.eq("")
    rejected = raw.loc[~valid].copy()
    rejected["rejection_reason"] = reasons.loc[~valid]
    clean = df.loc[valid].copy()
    clean["quantity"] = clean.quantity.astype("int64")
    clean["unit_price"] = clean.unit_price.astype(float)
    clean["revenue"] = (clean.quantity * clean.unit_price).round(2)
    clean["order_date"] = clean.order_date.dt.strftime("%Y-%m-%d")
    clean[["category", "region"]] = clean[["category", "region"]].fillna("Unknown")
    duplicates = clean.duplicated(["order_id", "order_date", "product", "quantity", "unit_price"], keep=False)
    clean.to_csv(out/"clean_sales.csv", index=False)
    clean.loc[duplicates].to_csv(out/"possible_duplicates.csv", index=False)
    rejected.to_csv(out/"rejected_rows.csv", index=False)
    results = out/"query_results"
    results.mkdir(exist_ok=True)
    with sqlite3.connect(out/"sales.db") as conn:
        clean.to_sql("sales", conn, if_exists="replace", index=False)
        count, total = conn.execute("SELECT COUNT(*), COALESCE(SUM(revenue),0) FROM sales").fetchone()
        assert count == len(clean)
        assert abs(total-float(clean.revenue.sum())) < 0.01
        for query in sorted((Path(__file__).parent/"sql").glob("*.sql")):
            pd.read_sql_query(query.read_text(), conn).to_csv(results/(query.stem+".csv"), index=False)
    assert len(df) == len(clean) + len(rejected)
    report = {"input_rows": len(df), "accepted_rows": len(clean), "rejected_rows": len(rejected),
              "suspected_duplicate_rows_retained": int(duplicates.sum()),
              "missing_customer_rows": int(clean.customer_id.isna().sum()),
              "sales_revenue": round(float(clean.revenue.sum()), 2)}
    (out/"quality_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", default="artifacts")
    p.add_argument("--date-format", required=True)
    a = p.parse_args()
    run(a.input, a.output, a.date_format)
