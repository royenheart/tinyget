import pytest
from tinyget.common_utils import setup_logger, strip_str_lines

setup_logger(debug=True)


def test_strip_str_lines():
    assert strip_str_lines("") == ""
    assert strip_str_lines("   ") == ""
    assert strip_str_lines("  \n  ") == "\n"
    orig = """#!/bin/bash
    echo 't'
ls
        print 'y'"""
    predict = """#!/bin/bash
echo 't'
ls
print 'y'"""
    assert strip_str_lines(orig) == predict


if __name__ == "__main__":
    pytest.main([__file__])
