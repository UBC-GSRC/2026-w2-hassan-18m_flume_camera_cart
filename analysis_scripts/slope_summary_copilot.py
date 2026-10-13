from pathlib import Path
from datetime import datetime
import pandas
import tomllib
from scipy.stats import linregress


def load_toml_rois():
    """Open regions of interest from toml file"""

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    rois = []

    for roi_config in config["roi"]:
        name = roi_config["name"]
        start = roi_config["start"]
        end = roi_config["end"]

        rois.append((name, start, end))

    return rois


def load_data_directories():
    """Load parent scan directories from config"""

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    water_scan_parent_dir = config["directories"]["water_scans"]
    dry_scan_parent_dir = config["directories"]["dry_scans"]

    return water_scan_parent_dir, dry_scan_parent_dir


def build_dry_scan_lookup(dry_scan_parent_dir):
    lookup = {}

    dry_root = Path(dry_scan_parent_dir)

    for hour_dir in dry_root.iterdir():

        if not hour_dir.is_dir():
            continue

        csv_files = sorted(hour_dir.glob("*.csv"))

        if csv_files:
            lookup[hour_dir.name] = csv_files[0]

    return lookup


def analyze_roi(df, roi_name, roi_start, roi_end, label):

    roi_data = df[
        (df["position_mm"] >= roi_start)
        & (df["position_mm"] < roi_end)
    ]

    if label == "depth":
        mean_key = f"{roi_name}_mean_depth_mm"
    else:
        mean_key = f"{roi_name}_mean_{label}_height_mm"

    if len(roi_data) < 2:
        return {
            mean_key: None,
            f"{roi_name}_{label}_slope_mm_per_mm": None,
        }

    fit = linregress(
        roi_data["position_mm"],
        roi_data["water_height_mm"]
    )

    return {
        mean_key: roi_data["water_height_mm"].mean(),
        f"{roi_name}_{label}_slope_mm_per_mm": fit.slope,
    }


def analyze_scan(scan_file, rois, label):

    df = pandas.read_csv(scan_file)

    results = {}

    for roi_name, roi_start, roi_end in rois:

        results.update(
            analyze_roi(
                df,
                roi_name,
                roi_start,
                roi_end,
                label,
            )
        )

    return results


def calculate_depth_dataframe(water_df, dry_df):

    depth_df = water_df.copy()

    depth_df["water_height_mm"] = (
        water_df["water_height_mm"]
        - dry_df["water_height_mm"]
    )

    return depth_df


def extract_datetime_from_filename(filename):

    timestamp = filename.removeprefix(
        "water_height_scan_"
    ).removesuffix(
        ".csv"
    )

    dt = datetime.strptime(
        timestamp,
        "%Y%m%d-%H%M%S"
    )

    return (
        dt.date().isoformat(),
        dt.time().isoformat()
    )


def main():

    rois = load_toml_rois()

    water_scan_parent_dir, dry_scan_parent_dir = load_data_directories()

    dry_scan_lookup = build_dry_scan_lookup(dry_scan_parent_dir)

    rows = []

    water_root = Path(water_scan_parent_dir)

    for hour_dir in sorted(water_root.iterdir()):

        if not hour_dir.is_dir():
            continue

        water_scans = sorted(hour_dir.glob("*.csv"))

        if not water_scans:
            continue

        dry_hour = hour_dir.name.split("-")[1]

        dry_scan_file = dry_scan_lookup.get(dry_hour)

        last_water_scan = water_scans[-1]

        for water_scan_file in water_scans:

            scan_date, scan_time = extract_datetime_from_filename(
                water_scan_file.name
            )

            row = {
                "hour": hour_dir.name,
                "scan_date": scan_date,
                "scan_time": scan_time,
                "scan_file": water_scan_file.name,
            }

            row.update(
                analyze_scan(
                    water_scan_file,
                    rois,
                    "water",
                )
            )

            if (
                dry_scan_file is not None
                and water_scan_file == last_water_scan
            ):

                row.update(
                    analyze_scan(
                        dry_scan_file,
                        rois,
                        "bed",
                    )
                )

                water_df = pandas.read_csv(water_scan_file)
                dry_df = pandas.read_csv(dry_scan_file)

                depth_df = calculate_depth_dataframe(
                    water_df,
                    dry_df,
                )

                for roi_name, roi_start, roi_end in rois:

                    row.update(
                        analyze_roi(
                            depth_df,
                            roi_name,
                            roi_start,
                            roi_end,
                            "depth",
                        )
                    )

            rows.append(row)

    summary_df = pandas.DataFrame(rows)

    summary_df = summary_df.round(4)

    output_file = "scan_summary.csv"

    summary_df.to_csv(
        output_file,
        index=False,
        na_rep="",
    )

    print(f"Wrote {len(summary_df)} rows to {output_file}")


if __name__ == "__main__":
    main()
