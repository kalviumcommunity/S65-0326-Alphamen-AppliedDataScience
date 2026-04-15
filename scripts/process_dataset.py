from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from grievance_insights.analysis import build_project_outputs, clean_dataset, load_dataset, save_outputs


def main() -> None:
    raw_data_path = PROJECT_ROOT / "data" / "raw" / "municipal_complaints.csv"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    output_dir = PROJECT_ROOT / "outputs"

    raw_dataset = load_dataset(raw_data_path)
    cleaned_dataset = clean_dataset(raw_dataset)
    outputs = build_project_outputs(cleaned_dataset)
    save_outputs(cleaned_dataset, outputs, processed_dir, output_dir)

    print(f"Processed dataset saved to: {processed_dir / 'municipal_complaints_processed.csv'}")
    print(f"Analysis outputs saved to: {output_dir}")
    print(f"Rows processed: {outputs['summary']['row_count']}")
    print(f"Columns in processed dataset: {outputs['summary']['column_count']}")


if __name__ == "__main__":
    main()
