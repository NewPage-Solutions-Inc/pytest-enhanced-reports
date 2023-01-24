import glob
from os import path, getcwd
import json


def find_newest_report(test_name, report_dir="reports") -> str:
    """Helper to find the latest report json that contains `test_name` order by create date desc"""
    files = list(
        filter(path.isfile, glob.glob(f"{getcwd()}/{report_dir}/*.json"))
    )
    files.sort(key=lambda x: path.getmtime(x))
    files.reverse()

    for a_file in files:
        with open(a_file) as f:
            content = json.load(f)
            if content.get("name") == test_name:
                return a_file


def count_file_match(extension: str, report_dir: str) -> str:
    """Helper to count matching files with extension inside the  report folder"""
    files = list(
        filter(path.isfile, glob.glob(f"{getcwd()}/{report_dir}/{extension}"))
    )
    return len(files)
