from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import re

import matplotlib.pyplot as plt
import pandas as pd


STOPWORDS = {
    "a",
    "and",
    "at",
    "for",
    "in",
    "is",
    "near",
    "not",
    "of",
    "on",
    "the",
    "to",
    "two",
}


def summarize_counts(values):
    total_count = sum(values)
    average_count = total_count / len(values)
    return total_count, average_count


def load_dataset(file_path: str | Path) -> pd.DataFrame:
    return pd.read_csv(file_path, parse_dates=["timestamp"])


def clean_dataset(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned = dataframe.copy()
    cleaned.columns = [column.strip() for column in cleaned.columns]

    object_columns = cleaned.select_dtypes(include="object").columns
    for column in object_columns:
        cleaned[column] = cleaned[column].astype(str).str.strip()

    cleaned["status"] = cleaned["status"].str.lower()
    cleaned["category"] = cleaned["category"].str.title()
    cleaned["location"] = cleaned["location"].str.title()
    cleaned["description"] = cleaned["description"].str.replace(r"\s+", " ", regex=True)

    cleaned["complaint_date"] = cleaned["timestamp"].dt.date.astype("string")
    cleaned["complaint_hour"] = cleaned["timestamp"].dt.hour
    cleaned["resolution_delay_bucket"] = pd.cut(
        cleaned["response_time_hours"],
        bins=[0, 12, 24, 48, float("inf")],
        labels=["fast", "moderate", "slow", "critical"],
        include_lowest=True,
    )

    return cleaned.sort_values("timestamp").reset_index(drop=True)


def build_project_outputs(cleaned: pd.DataFrame) -> dict[str, pd.DataFrame | dict[str, object]]:
    summary = {
        "row_count": int(len(cleaned)),
        "column_count": int(cleaned.shape[1]),
        "date_start": cleaned["timestamp"].min().isoformat(),
        "date_end": cleaned["timestamp"].max().isoformat(),
        "resolved_count": int((cleaned["status"] == "resolved").sum()),
        "pending_count": int((cleaned["status"] == "pending").sum()),
        "average_response_time_hours": float(cleaned["response_time_hours"].mean()),
        "max_response_time_hours": int(cleaned["response_time_hours"].max()),
        "min_response_time_hours": int(cleaned["response_time_hours"].min()),
    }

    category_summary = (
        cleaned.groupby("category", dropna=False)
        .agg(
            complaint_count=("complaint_id", "count"),
            average_response_time_hours=("response_time_hours", "mean"),
            resolved_count=("status", lambda values: (values == "resolved").sum()),
            pending_count=("status", lambda values: (values == "pending").sum()),
        )
        .reset_index()
        .sort_values(["complaint_count", "category"], ascending=[False, True])
    )

    location_summary = (
        cleaned.groupby("location", dropna=False)
        .agg(
            complaint_count=("complaint_id", "count"),
            average_response_time_hours=("response_time_hours", "mean"),
        )
        .reset_index()
        .sort_values(["complaint_count", "location"], ascending=[False, True])
    )

    daily_summary = (
        cleaned.groupby("complaint_date", dropna=False)
        .agg(
            complaint_count=("complaint_id", "count"),
            average_response_time_hours=("response_time_hours", "mean"),
        )
        .reset_index()
        .sort_values("complaint_date")
    )

    keywords = extract_keywords(cleaned["description"])
    keyword_summary = pd.DataFrame(keywords, columns=["keyword", "count"])

    hotspot_summary = location_summary.rename(columns={"complaint_count": "hotspot_score"})

    return {
        "summary": summary,
        "category_summary": category_summary,
        "location_summary": location_summary,
        "daily_summary": daily_summary,
        "keyword_summary": keyword_summary,
        "hotspot_summary": hotspot_summary,
    }


def extract_keywords(descriptions: pd.Series, limit: int = 10) -> list[tuple[str, int]]:
    words: list[str] = []
    for description in descriptions.fillna(""):
        tokens = re.findall(r"[a-zA-Z]+", description.lower())
        words.extend(token for token in tokens if token not in STOPWORDS and len(token) > 2)

    return Counter(words).most_common(limit)


def save_outputs(cleaned: pd.DataFrame, outputs: dict[str, pd.DataFrame | dict[str, object]], processed_dir: str | Path, output_dir: str | Path) -> None:
    processed_path = Path(processed_dir)
    output_path = Path(output_dir)
    processed_path.mkdir(parents=True, exist_ok=True)
    output_path.mkdir(parents=True, exist_ok=True)

    cleaned.to_csv(processed_path / "municipal_complaints_processed.csv", index=False)

    for name in ["category_summary", "location_summary", "daily_summary", "keyword_summary", "hotspot_summary"]:
        outputs[name].to_csv(output_path / f"{name}.csv", index=False)

    with (output_path / "summary.json").open("w", encoding="ascii") as file_handle:
        json.dump(outputs["summary"], file_handle, indent=2)

    _save_bar_chart(
        dataframe=outputs["category_summary"],
        label_column="category",
        value_column="complaint_count",
        title="Complaints by Category",
        file_path=output_path / "category_summary.png",
    )
    _save_bar_chart(
        dataframe=outputs["location_summary"],
        label_column="location",
        value_column="complaint_count",
        title="Complaints by Location",
        file_path=output_path / "location_summary.png",
    )


def _save_bar_chart(
    dataframe: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str,
    file_path: str | Path,
) -> None:
    plt.figure(figsize=(8, 4))
    plt.bar(dataframe[label_column], dataframe[value_column], color="#2f6db3")
    plt.title(title)
    plt.xlabel(label_column.replace("_", " ").title())
    plt.ylabel(value_column.replace("_", " ").title())
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
