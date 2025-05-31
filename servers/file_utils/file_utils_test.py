import pytest
from servers.file_utils.filename import sanitize, make_filename
from servers.file_utils.ripgrep import run_ripgrep
import os
import json

def test_sanitize():
    # Removes quotes, brackets, etc, replaces spaces, truncates
    assert sanitize("hello world") == "hello_world"
    assert sanitize("'quoted string'") == "quoted_string"
    assert sanitize('chars <>[]{}"`') == "chars_"
    assert sanitize("a"*25) == "a"*20


def test_make_filename():
    game_entity = {
        'name': 'Goblin',
        'description': 'small green menace',
        'id': '12345'
    }
    fname = make_filename(game_entity)
    assert fname.startswith("Goblin.small_green_menace.12345")
    assert fname.endswith(".json")


def test_rg_basic(tmp_path):
    import subprocess
    d = tmp_path / "output"
    d.mkdir()
    f = d / "testfile.txt"
    f.write_text('hello world\ngreen goblin\nfoo bar')
    # Run rg directly
    result = subprocess.run(['rg', 'goblin', str(d)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print('RG STDOUT:', result.stdout)
    print('RG STDERR:', result.stderr)
    assert result.returncode == 0 or result.stdout  # Should succeed or have output
    assert 'goblin' in result.stdout

def test_rg_multiple_results(tmp_path):
    import subprocess
    d = tmp_path / "output"
    d.mkdir()
    # Create multiple files with the search term
    for i in range(3):
        f = d / f"file_{i}.txt"
        f.write_text(f"line with goblin {i}\nanother line\n")
    # Run rg directly
    result = subprocess.run(['rg', 'goblin', str(d)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print('RG MULTIPLE STDOUT:', result.stdout)
    print('RG MULTIPLE STDERR:', result.stderr)
    # Should see three matches, one per file
    assert result.returncode == 0 or result.stdout
    # Count the number of matches
    matches = [line for line in result.stdout.splitlines() if 'goblin' in line]
    assert len(matches) == 3
