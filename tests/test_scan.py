# -*- coding: utf-8 -*-
from click.testing import CliRunner
from tests import TEST_DIR, ROOT_DIR
from fastcdc.cli import cli

r = CliRunner()


def test_scan_no_args():
    result = r.invoke(cli, "scan")
    assert result.exit_code == 0
    assert "Scan files" in result.output


def test_scan_path():
    result = r.invoke(cli, ["scan", TEST_DIR])
    assert result.exit_code == 0
    assert "Chunk Sizes" in result.output


def test_scan_custom_params():
    result = r.invoke(cli, ["scan", "-r", "-s", "1024", "-hf", "xxh64", ROOT_DIR])
    assert result.exit_code == 0
