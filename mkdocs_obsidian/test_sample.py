import unittest
from pathlib import Path
from mkdocs_obsidian.common import convert_one as one, convert_all as all, config as cfg


class MyTestCase(unittest.TestCase):
    def test_minimal(self):
        print("Testing Minimal configuration")
        source_path = Path("../docs_tests/input/source_file.md").resolve()
        configuration = cfg.open_value("0", actions="minimal", test=True)
        one.overwrite_file(str(source_path), configuration, True)

    def test_multiple_notes(self):
        print("testing multiple note without share state")
        configuration = cfg.open_value("0", test=True)
        all.convert_all(configuration, False, False, 0, 0, 1)

    def one_file(self):
        print("Testing one file with all configuration")
        configuration = cfg.open_value("0", test=True)
        source_path = Path("../docs_tests/input/source_file.md").resolve()
        one.convert_one(source_path, configuration, False, 1)

    def multiple_share(self):
        print("testing multiple note with share state")
        configuration = cfg.open_value("0", test=True)
        all.convert_all(configuration, False, False, 0, 0, 0)


if __name__ == "__main__":
    unittest.main()
