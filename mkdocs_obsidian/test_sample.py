import unittest
from pathlib import Path
from mkdocs_obsidian.common import (
    convert_one as one,
    convert_all as all,
    config as cfg)

class MyTestCase(unittest.TestCase) :
    def test_minimal(self) :
        source_path = Path('../docs_tests/input/source_file.md').resolve()
        print(f'testing {source_path}')
        configuration = cfg.open_value("0", actions="minimal", test=True)
        one.overwrite_file(str(source_path), configuration, True)
        with open(source_path, "r", encoding = "utf-8") as source:
            new_notes = source.read()
        print(new_notes)

    def test_multiple_notes(self) :
        output_blog = Path("../docs_tests/output_blog").resolve()
        input_blog = Path('../docs_tests/input').resolve()
        configuration = cfg.open_value("0", test=True)
        all.convert_all(configuration, False, False, 0, 0, 1)


if __name__ == '__main__' :
    unittest.main()