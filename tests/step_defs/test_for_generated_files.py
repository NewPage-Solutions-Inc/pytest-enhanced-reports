from pytest_bdd import scenario
import pytest
import glob
from os import path, getcwd


@scenario("../features/first_page.feature", "Tests for generated files")
def test_generated_files(selenium):
    pass


@pytest.mark.order(after="test_generated_files")
def test_verify_generated_files():
    # TODO: 1. no temp files <> json (report), image, video, txt
    allowed_list = [".json", ".png", "", ".txt"]
    files = list(filter(path.isfile, glob.glob(f"{getcwd()}/reports/*")))

    for a_file in files:
        assert (
            path.splitext(a_file) in allowed_list
        ), f"file {a_file} is a temp file and not cleaned up accordingly"
