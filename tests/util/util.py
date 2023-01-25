import glob
from os import path, getcwd, curdir, makedirs
import json
from shutil import rmtree


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


def count_file_match(extension: str, report_dir: str) -> int:
    """Helper to count matching files with extension inside the  report folder"""
    files = list(
        filter(path.isfile, glob.glob(f"{getcwd()}/{report_dir}/{extension}"))
    )
    return len(files)


def clean_up_report_directories(report_dir):
    """Remove report dir then create a new one"""
    if path.exists(path.join(curdir, report_dir)):
        rmtree(path.join(curdir, report_dir))
    makedirs(path.join(curdir, report_dir), exist_ok=True)


def collect_files_from_report(source, name, path_prefix):
    output = []
    if source.get("attachments"):
        for attachment in source["attachments"]:
            if name in attachment.get("name"):
                output.append(f"{path_prefix}/" + attachment.get("source"))
    return output


def collect_files_in_report_json(current_dir, report_dir, scenario, file_type):
    """Collect files in the report json file
    file_tpe: Screenshot/Video/Logs from browser console
    """
    report_file = find_newest_report(scenario, report_dir)

    # read report file
    with open(report_file) as f:
        output = json.load(f)

    if not output:
        assert False, "Test was not run successfully or file not found!"

    # collect files in the report json
    actual_files = []
    actual_report_dir = f"{current_dir}/{report_dir}/"
    # collect files in steps (output > steps > attachments)
    for step in output["steps"]:
        actual_files.extend(
            collect_files_from_report(step, file_type, actual_report_dir)
        )
    # collect files in attachment (output > attachments)
    actual_files.extend(
        collect_files_from_report(output, file_type, actual_report_dir)
    )
    return actual_files
