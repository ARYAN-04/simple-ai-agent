import os
import pytest
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file
from functions.call_function import call_function


# ── get_files_info ──────────────────────────────────────────────


class TestGetFilesInfo:
    def test_lists_real_directory(self, tmp_working_dir):
        os.makedirs(os.path.join(tmp_working_dir, "subdir"))
        with open(os.path.join(tmp_working_dir, "file.txt"), "w") as f:
            f.write("hello")

        result = get_files_info(tmp_working_dir)
        assert "file.txt: file_size=" in result
        assert "is_dir=False" in result
        assert "subdir: file_size=" in result
        assert "is_dir=True" in result

    def test_lists_subdirectory(self, tmp_working_dir):
        os.makedirs(os.path.join(tmp_working_dir, "pkg"))
        result = get_files_info(tmp_working_dir, "pkg")
        assert "Result for pkg:" in result

    def test_out_of_bounds_returns_error(self, tmp_working_dir):
        result = get_files_info(tmp_working_dir, "../")
        assert "Error:" in result
        assert "outside the permitted working directory" in result

    def test_nonexistent_directory_returns_error(self, tmp_working_dir):
        result = get_files_info(tmp_working_dir, "nonexistent")
        assert "Error:" in result


# ── get_file_content ────────────────────────────────────────────


class TestGetFileContent:
    def test_reads_file_exactly(self, tmp_working_dir):
        path = os.path.join(tmp_working_dir, "test.py")
        with open(path, "w") as f:
            f.write("print('hi')")

        result = get_file_content(tmp_working_dir, "test.py")
        assert result == "print('hi')"

    def test_truncates_large_file(self, tmp_working_dir):
        path = os.path.join(tmp_working_dir, "big.txt")
        with open(path, "w") as f:
            f.write("x" * 15000)

        result = get_file_content(tmp_working_dir, "big.txt")
        assert len(result) < 15000
        assert "truncated at 10000 characters" in result

    def test_missing_file_returns_error(self, tmp_working_dir):
        result = get_file_content(tmp_working_dir, "nope.txt")
        assert "Error:" in result

    def test_out_of_bounds_returns_error(self, tmp_working_dir):
        result = get_file_content(tmp_working_dir, "../etc/passwd")
        assert "Error:" in result
        assert "outside the permitted working directory" in result


# ── write_file ──────────────────────────────────────────────────


class TestWriteFile:
    def test_writes_new_file(self, tmp_working_dir):
        result = write_file(tmp_working_dir, "new.txt", "content here")
        assert "Successfully wrote" in result

        content = get_file_content(tmp_working_dir, "new.txt")
        assert content == "content here"

    def test_overwrites_existing_file(self, tmp_working_dir):
        write_file(tmp_working_dir, "file.txt", "old")
        write_file(tmp_working_dir, "file.txt", "new")

        content = get_file_content(tmp_working_dir, "file.txt")
        assert content == "new"

    def test_creates_parent_directories(self, tmp_working_dir):
        result = write_file(tmp_working_dir, "a/b/c.txt", "nested")
        assert "Successfully wrote" in result

        content = get_file_content(tmp_working_dir, "a/b/c.txt")
        assert content == "nested"

    def test_out_of_bounds_returns_error(self, tmp_working_dir):
        result = write_file(tmp_working_dir, "../bad.txt", "nope")
        assert "Error:" in result
        assert not os.path.exists(os.path.join(tmp_working_dir, "..", "bad.txt"))


# ── run_python_file ─────────────────────────────────────────────


class TestRunPythonFile:
    def test_runs_script_stdout(self, tmp_working_dir):
        write_file(tmp_working_dir, "hello.py", "print('hi')")
        result = run_python_file(tmp_working_dir, "hello.py")
        assert "hi" in result
        assert "STDOUT:" in result

    def test_nonzero_exit_code(self, tmp_working_dir):
        write_file(
            tmp_working_dir,
            "fail.py",
            "import sys; print('error', file=sys.stderr); sys.exit(1)",
        )
        result = run_python_file(tmp_working_dir, "fail.py")
        assert "STDERR:" in result
        assert "Process exited with code 1" in result

    def test_non_python_file_returns_error(self, tmp_working_dir):
        write_file(tmp_working_dir, "file.txt", "hello")
        result = run_python_file(tmp_working_dir, "file.txt")
        assert "Error:" in result
        assert "not a Python file" in result

    def test_missing_file_returns_error(self, tmp_working_dir):
        result = run_python_file(tmp_working_dir, "missing.py")
        assert "Error:" in result

    def test_out_of_bounds_returns_error(self, tmp_working_dir):
        result = run_python_file(tmp_working_dir, "../something.py")
        assert "Error:" in result


# ── call_function ───────────────────────────────────────────────


class TestCallFunction:
    def test_injects_working_directory(self, tmp_working_dir):
        os.makedirs(os.path.join(tmp_working_dir, "sub"))
        result = call_function("get_files_info", {}, tmp_working_dir)
        assert "sub" in result

    def test_unknown_function_returns_error(self, tmp_working_dir):
        result = call_function("unknown_tool", {}, tmp_working_dir)
        assert "Error: Unknown function: unknown_tool" in result

    def test_missing_required_arg_returns_error(self, tmp_working_dir):
        result = call_function("get_file_content", {}, tmp_working_dir)
        assert "Error:" in result
