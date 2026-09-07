import tempfile
from pathlib import Path
from unittest.mock import patch

from devpilot import cli


def test_iter_files_ignores_build_and_devpilot():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / 'src').mkdir()
        (root / 'build').mkdir()
        (root / '.devpilot').mkdir()
        (root / 'src' / 'main.py').write_text('print(1)')
        (root / 'build' / 'x.txt').write_text('ignored')
        (root / '.devpilot' / 'config.json').write_text('{}')
        files = [p.relative_to(root).as_posix() for p in cli.iter_files(root)]
        assert files == ['src/main.py']


def test_extract_patch():
    text = '```diff\n--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n-old\n+new\n```'
    assert cli.extract_patch(text).startswith('--- a/a.txt')


def test_online_chat_requires_key():
    with patch.dict('os.environ', {}, clear=True):
        answer, error = cli.online_chat([])
    assert answer is None
    assert 'DEVPILOT_API_KEY' in error
