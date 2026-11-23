# Copyright 2026 Team D.A.V.E.Y. Contributors
# This project is licensed under GNU GENERAL PUBLIC LICENSE
# See LICENSE.txt

"""
get_csv_files.py gathers and combines all CSV data files from Polar devices.

parameters/inputs:
- root_directory: root folder containing Polar CSV data

"""

import os
import csv
import pandas as pd
from collections import defaultdict


def gather_folder_data(root_path):
    """Count folders under the root and record each folder name and its parent."""
    folder_count = 0
    name_counter = defaultdict(int)
    parent_map = defaultdict(list)

    for current_path, dirnames, _ in os.walk(root_path):
        for dirname in dirnames:
            folder_count += 1
            name_counter[dirname] += 1
            parent_map[dirname].append(current_path)

    return folder_count, dict(name_counter), dict(parent_map)


def find_csv_in_target_folders(root_path, device_folder_name):
    """Find CSV files inside directories whose name matches the device folder."""
    csv_files = []

    for current_path, dirnames, _ in os.walk(root_path):
        if os.path.basename(current_path) == device_folder_name:
            for sub_path, _, files in os.walk(current_path):
                for file in files:
                    if file.lower().endswith(".csv"):
                        full_path = os.path.join(sub_path, file)
                        csv_files.append(full_path)

    return csv_files


def merge_csv_files(csv_files, output_filename="merged_output_small.csv"):
    """
    Merge CSV files by copying their rows into one output file.

    The first non-empty file supplies the header; all input files are expected
    to use the same columns. This older implementation currently processes at
    most three files.
    """
    if not csv_files:
        print("No CSV files found to merge.")
        return

    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_directory, output_filename)

    header_saved = False
    total_count = len(csv_files)
    count = 0

    print("saving to csv file output")

    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = None

        for file in csv_files:
            print(f"\ncurr progress: {count} / {total_count} ({count/total_count*100})")
            count += 1
            with open(file, mode="r", newline="", encoding="utf-8") as infile:
                reader = csv.reader(infile)
                header = next(reader, None)

                if not header:
                    continue  # skip empty files

                if not header_saved:
                    writer = csv.writer(outfile)
                    writer.writerow(header)
                    header_saved = True

                for row in reader:
                    writer.writerow(row)
            
            if count == 3:
                break

    print(f"\nMerged CSV created at: {output_path}")


def polar_formatter(dataframe):
    """Return combined Polar data unchanged until its export format is known."""
    return dataframe

def merge_csv_files_to_csv(csv_files, output_filename="polar.csv"):
    """
    Load, combine, and save Polar CSV files while reporting row counts.

    Malformed CSV rows are skipped during loading. The combined data is passed
    through ``polar_formatter`` and saved beside this script using the given
    output filename.
    """

    if not csv_files:
        print("No CSV files found to merge.")
        return

    dataframes = []
    total_expected_rows = 0
    total_loaded_rows = 0

    print("\n===== File Integrity Report =====\n")

    for file in csv_files:
        try:
            # Count raw rows (excluding header)
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                raw_line_count = sum(1 for _ in f)

            if raw_line_count <= 1:
                print(f"{file} -> Empty or header-only file.")
                continue

            expected_rows = raw_line_count - 1  # subtract header

            # Load safely, some lines are bad/not correctly saved, skipping these lines
            df = pd.read_csv(
                file,
                engine="python",
                on_bad_lines="skip",
                # low_memory=False
            )

            loaded_rows = len(df)
            skipped_rows = expected_rows - loaded_rows

            total_expected_rows += expected_rows
            total_loaded_rows += loaded_rows

            print(f"File: {os.path.basename(file)}")
            print(f"  Expected rows : {expected_rows}")
            print(f"  Loaded rows   : {loaded_rows}")
            print(f"  Skipped rows  : {skipped_rows}")
            print("-" * 40)

            dataframes.append(df)

        except Exception as e:
            print(f"Critical failure loading file: {file}")
            print(f"Error: {e}")
            print("-" * 40)

    if not dataframes:
        print("No valid CSV files could be loaded.")
        return

    combined_df = pd.concat(dataframes, ignore_index=True, sort=False)

    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_name = os.path.splitext(output_filename)[0] + ".csv"
    output_path = os.path.join(script_directory, output_name)

    combined_df = polar_formatter(combined_df)

    combined_df.to_csv(output_path, index=False)

    print("\n===== Final Summary =====")
    print(f"Total expected rows : {total_expected_rows}")
    print(f"Total loaded rows   : {total_loaded_rows}")
    print(f"Total skipped rows  : {total_expected_rows - total_loaded_rows}")
    print(f"Final dataframe rows: {len(combined_df)}")
    print(f"Saved to: {output_path}")

def print_summary(total_folders, name_counter):
    """Print the total folder count and number of distinct folder names."""
    print("===== Folder Summary =====")
    print(f"Total folders found: {total_folders}")
    print(f"Unique folder names: {len(name_counter)}\n")


if __name__ == "__main__":
    root_directory = input("Enter the root folder path: ").strip()

    if not os.path.isdir(root_directory):
        print("Invalid directory path.")
    else:
        total, counter, _ = gather_folder_data(root_directory)
        print_summary(total, counter)

        csv_files = find_csv_in_target_folders(root_directory, "polar")

        print(f"\nTotal CSV files found: {len(csv_files)}")
        for file in csv_files:
            print(f"  - {file}")

        # merge_csv_files(csv_files)
        merge_csv_files_to_csv(csv_files, output_filename="polar")