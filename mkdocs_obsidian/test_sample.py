import unittest
from pathlib import Path

import yaml

from mkdocs_obsidian.common import convert_one as one, convert_all as all, config as cfg


class MyTestCase(unittest.TestCase):
    def test_minimal(self):
        print("Testing Minimal configuration")
        source_path = Path("./docs_tests/input/source_file.md").resolve()
        configuration = cfg.open_value(actions=True, configuration_name='minimal_test')
        one.overwrite_file(str(source_path), configuration, True)

    def test_multiple_notes(self):
        print("testing multiple note without share state")
        configuration = cfg.open_value("test")
        all.convert_all(configuration, False, False, 0, 0, 1)

    def test_one_file(self):
        print("Testing one file with all configuration")
        configuration = cfg.open_value("test")
        source_path = Path("./docs_tests/input/source_file.md").resolve()
        one.convert_one(source_path, configuration, False, 1)

    def test_multiple_share(self):
        print("testing multiple note with share state")
        configuration = cfg.open_value("test")
        all.convert_all(configuration, False, False, 0, 0, 0)

    def test_convert_big_config(self):
        print('convert an old configuration')
        basedir = cfg.get_Obs2mk_dir('test_config', False)
        config_test = Path(basedir, ".test_config")
        with open(config_test, 'w', encoding="utf-8") as f:
            f.write(f'''
                vault={Path(basedir, 'input')}
                blog_path={Path(basedir, 'output')}
                blog=https://www.mara-li.fr/
                share=share
                index_key=(i)
                default_blog=notes
                category_key=category
            ''')
        cfg.checking_old_config('test_config', config_test, basedir)
        with open(Path(basedir, 'configuration.yml'), 'r', encoding='utf-8') as config:
            new_config = yaml.safe_load(config)
        new_config = new_config['test_config']
        attended_result = '''
        configuration:
            input: D:\\Users\Lili\Documents\GitHub\mkdocs obsidian publish\mkdocs_obsidian_publish\docs_tests\output\input
            output: D:\\Users\Lili\Documents\GitHub\mkdocs obsidian publish\mkdocs_obsidian_publish\docs_tests\output\output
        frontmatter:
            category:
                default value: notes
                key: category
            index: (i)
            share: share
        weblink: https://www.mara-li.fr/
        '''
        attended_result_to_yaml = yaml.safe_load(attended_result)
        print(attended_result_to_yaml == new_config)

    def test_convert_mini_config(self):
        print('convert an old configuration')
        basedir = cfg.get_Obs2mk_dir('test_mini_config', False)
        config_test = Path(basedir, ".test_mini_config")
        with open(config_test, 'w', encoding="utf-8") as f:
            f.write(f'''
            index_key=(i)
            default_blog=notes
            category_key=category
            ''')
        cfg.checking_old_config('test_mini_config', config_test, basedir)
if __name__ == "__main__":
    unittest.main()
