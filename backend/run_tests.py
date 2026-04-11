"""Run pytest programmatically."""
import sys
import pytest

sys.exit(pytest.main(["tests/talk_to_data", "-v", "--tb=short"]))
