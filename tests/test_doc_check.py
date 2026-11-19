from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'source/project/.agents/sdd/scripts/doc_check.py'
spec = importlib.util.spec_from_file_location('doc_check', CLI)
doc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doc)


class DocCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def put(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text if isinstance(text, bytes) else text.encode('utf-8'))
        return p

    def check(self, *paths):
        return doc.Checker(self.root).run(list(paths))

    def codes(self, result):
        return [d['code'] for d in result['diagnostics']]

    def test_unicode_duplicate_headings_reference_links_and_balanced_paths(self):
        self.put('docs/目标 (v1).md', '# 标题\n## 重复\n## 重复\n<a id="explicit"></a>\n')
        self.put('index.md', '[a](<docs/目标 (v1).md#重复-1>)\n'
                 '[b](docs/%E7%9B%AE%E6%A0%87%20(v1).md#explicit)\n'
                 '[ref][Target]\n[Target]: <docs/目标 (v1).md#标题> "title"\n'
                 '[skip](https://example.invalid/no-network)\n')
        result = self.check('index.md')
        self.assertEqual(result['diagnostics'], [])
        self.assertEqual(result['files'], ['index.md'])

    def test_missing_targets_anchors_references_have_source_lines(self):
        self.put('target.md', '# Real\n')
        self.put('input.md', '[a](missing.md)\n[b](target.md#absent)\n[x][undefined]\n')
        result = self.check('input.md')
        self.assertEqual([(x['line'], x['code']) for x in result['diagnostics']],
                         [(1, 'DOC007'), (2, 'DOC008'), (3, 'DOC009')])

    def test_code_comments_frontmatter_and_escaped_links_are_not_prose(self):
        self.put('input.md', '---\nexample: "[x](absent.md)"\n---\n# Doc\n'
                 '```md\n[x](absent.md)\n### ignored\n```\n'
                 '`[x](absent.md)`\n<!-- [x](absent.md) -->\n'
                 '    [x](absent.md)\n\\[x](absent.md)\n')
        self.assertEqual(self.check('input.md')['diagnostics'], [])

    def test_table_columns_escaped_and_code_pipes(self):
        self.put('input.md', '| A | B |\n| --- | --- |\n| a\\|b | `x|y` |\n| bad |\n')
        result = self.check('input.md')
        self.assertEqual([(x['line'], x['code']) for x in result['diagnostics']], [(4, 'DOC004')])

    def test_duplicate_declarations_but_not_references_or_result_rows(self):
        self.put('input.md', '- FR-001: one\nSee FR-001.\n- FR-001: two\n'
                 '| ID | Given |\n| --- | --- |\n| AC-001 | one |\n| AC-001 | two |\n'
                 '\n| ID | Result |\n| --- | --- |\n| AC-001 | PASS |\n| AC-001 | FAIL |\n')
        result = self.check('input.md')
        self.assertEqual([(x['line'], x['code']) for x in result['diagnostics']],
                         [(3, 'DOC005'), (7, 'DOC005')])

    def test_encoding_bom_unclosed_fence_and_frontmatter(self):
        self.put('bom.md', b'\xef\xbb\xbf# OK\r\n')
        self.put('bad.md', b'\xff')
        self.put('fence.md', '# Heading\n```python\npass\n')
        self.put('front.md', '---\nname: missing close\n')
        self.assertEqual(self.check('bom.md')['errors'], 0)
        self.assertEqual(self.codes(self.check('bad.md')), ['DOC001'])
        self.assertEqual(self.codes(self.check('fence.md')), ['DOC002'])
        self.assertEqual(self.codes(self.check('front.md')), ['DOC002'])

    def test_input_boundary_dedup_no_files_and_directory_exclusions(self):
        self.put('docs/a.md', '# A\n')
        self.put('docs/.build/b.md', '[bad](none.md)\n')
        self.assertEqual(self.check('docs', 'docs/a.md')['files'], ['docs/a.md'])
        self.assertEqual(self.codes(self.check('../outside.md')), ['DOC000'])
        self.put('docs/a.md', '[outside](../../outside.md)\n')
        self.assertEqual(self.codes(self.check('docs/a.md')), ['DOC007'])
        (self.root / 'empty').mkdir()
        self.assertEqual(self.codes(self.check('empty')), ['DOC000'])

    def test_cli_json_exit_codes_and_no_mutation(self):
        self.put('input.md', '# Title\n### Jump\n')
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        command = [sys.executable, '-B', '-X', 'utf8', str(CLI), '--root', str(self.root), '--format', 'json']
        result = subprocess.run(command + ['input.md'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['warnings'], 1)
        self.assertEqual(subprocess.run(command + ['--strict', 'input.md'], capture_output=True).returncode, 1)
        self.assertEqual(subprocess.run(command + ['missing.md'], capture_output=True).returncode, 1)
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_setext_headings_and_non_markdown_fragment_warning(self):
        self.put('target.md', 'Hello\n=====\n')
        self.put('page.html', '<div id="x"></div>')
        self.put('input.md', '[ok](target.md#hello)\n[html](page.html#x)\n')
        result = self.check('input.md')
        self.assertEqual(result['errors'], 0)
        self.assertEqual(self.codes(result), ['DOC010'])

    def test_text_diagnostics_and_semantic_non_goal(self):
        self.put('input.md', '# Requirements\n- FR-001: timeout is 5 seconds\n- FR-002: timeout is 10 seconds\n')
        self.assertEqual(self.check('input.md')['errors'], 0)  # Conflicts need Agent judgment.
        self.put('input.md', '[missing](missing.md)\n')
        result = subprocess.run(
            [sys.executable, '-B', '-X', 'utf8', str(CLI), '--root', str(self.root), 'input.md'],
            capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 1)
        self.assertIn('input.md:1: error DOC007:', result.stdout)
        self.assertIn('mechanical only', result.stdout)

    def test_read_sections_and_rows_without_returning_unselected_rules(self):
        original = ('# 通用\n保留授权。\n\n## 交接\n'
                    '```md\n## 示例标题\n```\n'
                    '| 角色 | 规则 |\n| --- | --- |\n'
                    '| documenter | 保留 Gate |\n| coder | 不在本轮 |\n\n'
                    '共同要求。\n\n### 其他流程\n不返回。\n')
        target = self.put('rules.md', original)
        command = [sys.executable, '-B', '-X', 'utf8', str(CLI),
                   '--root', str(self.root), '--read']
        result = subprocess.run(command + ['rules.md#通用', 'rules.md#交接:documenter'],
                                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout,
                         '# 通用\n保留授权。\n\n## 交接\n'
                         '```md\n## 示例标题\n```\n'
                         '| 角色 | 规则 |\n| --- | --- |\n'
                         '| documenter | 保留 Gate |\n\n共同要求。\n')
        self.assertEqual(target.read_bytes(), original.encode('utf-8'))
        for selector in ('rules.md#缺失', 'rules.md#交接:validator', '../rules.md#交接'):
            with self.subTest(selector=selector):
                result = subprocess.run(command + [selector], capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b'')

    def test_installed_flat_links_allow_shared_references_but_not_foreign_targets(self):
        from test_build import builder

        build = builder.build(self.root / 'initializer')
        spec = importlib.util.spec_from_file_location('installed_govern', build / 'scripts/govern.py')
        govern = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(govern)
        project = self.root / 'project'
        project.mkdir()
        initialized = subprocess.run(
            [sys.executable, '-B', '-X', 'utf8', str(build / 'scripts/govern.py'),
             '--root', str(project), '--harness', 'both', 'init'], capture_output=True)
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        checker = project / '.agents/sdd-workflow/sdd/scripts/doc_check.py'
        command = [sys.executable, '-B', '-X', 'utf8', str(checker), '--root', str(project)]
        checked = subprocess.run(command + ['--format', 'json', 'AGENTS.md'], capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertEqual(json.loads(checked.stdout)['errors'], 0)
        selector = '.agents/skills/sdd-bugfix/SKILL.md#缺陷修复与定向复验'
        selected = subprocess.run(command + ['--read', selector], capture_output=True)
        self.assertEqual(selected.returncode, 0, selected.stderr)
        self.assertIn('缺陷修复与定向复验'.encode(), selected.stdout)
        foreign = self.root / 'foreign'
        foreign.mkdir()
        (foreign / 'SKILL.md').write_text('# Foreign\n', encoding='utf-8')
        link = project / '.agents/skills/foreign'
        govern.transaction.create_workflow_link(link, foreign)
        (project / 'outside.md').write_text('[foreign](.agents/skills/foreign/SKILL.md)\n', encoding='utf-8')
        checked = subprocess.run(command + ['--format', 'json', 'outside.md'], capture_output=True)
        self.assertEqual(checked.returncode, 1, checked.stderr)
        self.assertEqual(self.codes(json.loads(checked.stdout)), ['DOC007'])
        selected = subprocess.run(command + ['--read', '.agents/skills/foreign/SKILL.md#foreign'], capture_output=True)
        self.assertEqual(selected.returncode, 2)

    def test_shared_checker_without_skill_payload_can_still_read_rules(self):
        import shutil

        shared = self.root / '.agents/sdd-workflow/sdd'
        checker = shared / 'scripts/doc_check.py'
        checker.parent.mkdir(parents=True)
        shutil.copyfile(CLI, checker)
        rules = shared / 'references/rules.md'
        rules.parent.mkdir()
        rules.write_text('# Rules\nShared rules only.\n', encoding='utf-8')
        result = subprocess.run(
            [sys.executable, '-B', '-X', 'utf8', str(checker), '--root', str(self.root),
             '--read', '.agents/sdd-workflow/sdd/references/rules.md#rules'], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b'Shared rules only.', result.stdout)

    def test_read_english_aliases_used_by_distributed_templates(self):
        references = CLI.parents[1] / 'references'
        checker = doc.Checker(references)
        for path, alias, heading in (
            ('sdd-repository-governance.md', 'document-and-artifact-locations', '文档与产物落点'),
            ('sdd-repository-governance.md', 'authoritative-documents', '权威实体'),
            ('sdd-repository-governance.md', 'testing-scope-constraints', '测试范围约束'),
            ('prototype.md', 'prototype-scope', '适用范围'),
        ):
            with self.subTest(alias=alias):
                expected = checker.excerpts([f'{path}#{heading}'])
                self.assertEqual(checker.excerpts([f'{path}#{alias}']), expected)


if __name__ == '__main__':
    unittest.main()
