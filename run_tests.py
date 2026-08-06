import sys
from processor import process_file

def test_process_file_returns_list():
    file_bytes = b"task,budget,actual\nroofing,20000,22000"
    result = process_file(file_bytes)
    assert isinstance(result, list), "Should return list"
    if result:
        assert "title" in result[0]
        assert "status" in result[0]
        assert "details" in result[0]
        # due_date may be None
    print("Basic structure test passed.")

def test_empty_input():
    result = process_file(b"")
    assert result == [], "Should return empty list for no content"

if __name__ == "__main__":
    try:
        test_process_file_returns_list()
        test_empty_input()
        print("All tests passed.")
        sys.exit(0)
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
