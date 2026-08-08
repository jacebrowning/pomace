# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

from unittest.mock import Mock

import pytest

from .. import utils


def describe_run_script():
    def it_raises_the_original_exception(expect, tmp_path, monkeypatch):
        script = tmp_path / "fail.py"
        script.write_text("raise ValueError('original failure')\n")
        monkeypatch.setattr(utils.sys.stdin, "isatty", lambda: False)

        with pytest.raises(ValueError, match="original failure"):
            utils.run_script(str(script))

    def it_allows_scripts_to_import_traceback(expect, tmp_path, monkeypatch):
        script = tmp_path / "use_traceback.py"
        script.write_text(
            "\n".join(
                [
                    "import traceback",
                    "try:",
                    "    raise RuntimeError('boom')",
                    "except Exception:",
                    "    traceback.print_exc()",
                    "    raise",
                    "",
                ]
            )
        )
        monkeypatch.setattr(utils.sys.stdin, "isatty", lambda: False)

        with pytest.raises(RuntimeError, match="boom"):
            utils.run_script(str(script))

    def it_enters_post_mortem_then_raises_when_interactive(
        expect, tmp_path, monkeypatch
    ):
        script = tmp_path / "fail.py"
        script.write_text("raise ValueError('original failure')\n")
        monkeypatch.setattr(utils.sys.stdin, "isatty", lambda: True)
        post_mortem = Mock()
        monkeypatch.setattr(utils.ipdb, "post_mortem", post_mortem)

        with pytest.raises(ValueError, match="original failure"):
            utils.run_script(str(script))

        expect(post_mortem.call_count) == 1
        tb = post_mortem.call_args[0][0]
        expect(tb is not None) == True
