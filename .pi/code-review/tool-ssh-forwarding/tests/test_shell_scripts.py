#!/usr/bin/env python3
"""Shell-script guardrails for the operator scripts in scripts/.

macOS ships bash 3.2, which parses `$VAR` immediately followed by a multibyte
character by swallowing that character's first byte into the variable name
(`$TRANSPORT（` -> "TRANSPORT\\xef: unbound variable" under `set -u`).  Every
message in these scripts is Chinese, so this is easy to reintroduce.
"""
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = sorted((ROOT / "scripts").glob("*.sh"))
VAR_BEFORE_MULTIBYTE = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)(?=[^\x00-\x7f])")


class ShellScriptGuardrailTest(unittest.TestCase):
    def test_scripts_exist(self):
        self.assertTrue(SCRIPTS, "scripts/*.sh 不应为空")

    def test_no_bare_variable_before_multibyte_character(self):
        offenders = []
        for path in SCRIPTS:
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for match in VAR_BEFORE_MULTIBYTE.finditer(line):
                    offenders.append(f"{path.name}:{lineno}: ${match.group(1)} 紧跟非 ASCII 字符（请写成 ${{{match.group(1)}}}）")
        self.assertEqual(offenders, [], "bash 3.2 会把多字节字符首字节吞进变量名：\n" + "\n".join(offenders))

    def test_scripts_parse_with_bash(self):
        for path in SCRIPTS:
            result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"{path.name} bash -n 失败：{result.stderr}")


if __name__ == "__main__":
    unittest.main()
