import os
import unittest
from pathlib import Path

import yaml

from mkdocs_obsidian.common import config as cfg, convert_all as all, convert_one as one


def test_env_path(configuration_name: str, basedir: Path) -> tuple[Path, str]:
    env_path = Path(basedir, '.obs2mk')
    if 'minimal' in configuration_name:
        configuration_name = 'minimal'
    elif 'actions' in configuration_name:
        configuration_name = 'actions'
        env_path = Path(basedir, 'source', '.github-actions')
    return env_path, configuration_name


def get_basedir_test(configuration_name: str) -> Path:
    basedir = Path(os.getcwd())
    if 'test' in configuration_name:
        basedir = Path(basedir, 'docs_tests', 'output')
    return basedir


def checking_file_contents(output_file: Path) -> bool:
    with open(output_file, 'r', encoding='utf-8') as f:
        output_file_data = f.read()
    attend_name = os.path.basename(output_file)
    attend_file = Path(os.getcwd(), 'docs_tests', 'attended_results', attend_name)
    with open(attend_file, 'r', encoding='utf-8') as f:
        attend_file_data = f.read()
    return output_file_data == attend_file_data


class MyTestCase(unittest.TestCase):
    def test_minimal(self) -> bool:
        print('Testing Minimal configuration')
        source_path = Path('./docs_tests/input/source_file.md').resolve()
        basedir = get_basedir_test('minimal_test')
        env_path = test_env_path('minimal_test', basedir)[0]
        env = (basedir, env_path)
        configuration = cfg.open_value(actions=False, configuration_name='minimal', env_path=env)
        test_output = Path(source_path.resolve().parent.parent,
                           'output', 'docs', 'notes', os.path.basename(source_path))
        one.overwrite_file(str(source_path), configuration, True)
        print(checking_file_contents(test_output))
        return checking_file_contents(test_output)

    def test_multiple_notes(self) -> bool:
        print('testing multiple note without share state')
        configuration_name = 'test'
        basedir = get_basedir_test('test')
        env_path = test_env_path(configuration_name, basedir)[0]
        env = (basedir, env_path)
        configuration = cfg.open_value('default', env_path=env)
        all.convert_all(configuration, True, False, 0, 0, 1)

        return True

    def test_one_file(self) -> bool:
        print('Testing one file with all configuration')
        configuration_name = 'test'
        basedir = get_basedir_test(configuration_name)
        env_path = test_env_path(configuration_name, basedir)[0]
        env = (basedir, env_path)
        configuration = cfg.open_value('default', env_path=env)
        source_path = Path('./docs_tests/input/source_file.md').resolve()
        one.convert_one(source_path, configuration, False, 1)
        return True

    def test_multiple_share(self) -> bool:
        """
        Attended result : 🎉 Added to blog :
        • second_file in [second_file]
        • source_file in [notes]
        """
        print('testing multiple note with share state')
        configuration_name = 'test'
        basedir = get_basedir_test(configuration_name)
        env_path = test_env_path(configuration_name, basedir)[0]
        env = (basedir, env_path)
        configuration = cfg.open_value('default', env_path=env)
        all.convert_all(configuration, True, False, 0, 0, 0)

        return True

    def test_convert_big_config(self) -> bool:
        print('convert an old configuration')
        basedir = get_basedir_test('test_config')
        config_test = Path(basedir, '.test_config')
        with open(config_test, 'w', encoding='utf-8') as f:
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
        attended_result = f'''
        configuration:
            input: {Path(basedir, 'input')}
            output: {Path(basedir, 'output')}
        frontmatter:
            category:
                default value: notes
                key: category
            index: (i)
            share: share
        weblink: https://www.mara-li.fr/
        '''
        attended_result_to_yaml = yaml.safe_load(attended_result)
        if attended_result_to_yaml != new_config:
            raise 'Error in the new configuration'

    def test_convert_mini_config(self) -> bool:
        print('convert an old configuration')
        basedir = get_basedir_test('test_mini_config')
        config_test = Path(basedir, '.test_mini_config')
        with open(config_test, 'w', encoding='utf-8') as f:
            f.write(f'''
            index_key=(i)
            default_blog=notes
            category_key=category
            ''')
        cfg.checking_old_config('test_mini_config', config_test, basedir)
        return True

    def test_github_actions(self) -> bool:
        """
        Attended result : 🎉 Successfully converted github_actions_test.md
        """
        print('convert github configuration')
        basedir = Path(get_basedir_test('actions-test'), 'source')
        config_test = Path(basedir, '.github-actions')
        with open(config_test, 'w', encoding='utf-8') as f:
            f.write('''
            index_key=(i)
            default_blog=notes
            category_key=category
            ''')
        basedir = Path(basedir.parent)
        env_path = (basedir, config_test)
        config = cfg.open_value('actions-test', True, env_path=env_path)
        file_source = Path('./docs_tests/output/source/github_actions_test.md').resolve()
        config.output = Path(config.output, 'docs_tests', 'output')
        one.convert_one(Path(file_source), config, False, False)
        return True


if __name__ == '__main__':
    unittest.main()
