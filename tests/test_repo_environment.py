import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepoEnvironmentTests(unittest.TestCase):
    def test_sdk_is_pinned_and_tool_directory_is_ignored(self) -> None:
        global_json = json.loads((ROOT / "global.json").read_text(encoding="utf-8"))

        self.assertEqual("10.0.302", global_json["sdk"]["version"])
        self.assertEqual("disable", global_json["sdk"]["rollForward"])
        self.assertFalse(global_json["sdk"]["allowPrerelease"])
        self.assertIn(".tools/", (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())

    def test_environment_state_is_repo_local_and_process_scoped(self) -> None:
        environment_script = (ROOT / "eng" / "RepoEnvironment.ps1").read_text(encoding="utf-8")
        expected_variables = (
            "DOTNET_ROOT",
            "DOTNET_CLI_HOME",
            "NUGET_PACKAGES",
            "NUGET_HTTP_CACHE_PATH",
            "TEMP",
            "TMP",
        )

        for variable in expected_variables:
            self.assertIn(f"$env:{variable}", environment_script)

        forbidden_machine_mutations = (
            "SetEnvironmentVariable",
            "Set-ItemProperty",
            "New-ItemProperty",
            "setx ",
        )
        for mutation in forbidden_machine_mutations:
            self.assertNotIn(mutation, environment_script)

    def test_canonical_setup_uses_the_repo_bootstrap(self) -> None:
        project = json.loads((ROOT / "harness" / "project.json").read_text(encoding="utf-8"))

        self.assertEqual(
            "powershell -NoProfile -ExecutionPolicy Bypass -File eng/bootstrap.ps1",
            project["commands"]["setup"],
        )
        bootstrap = (ROOT / "eng" / "bootstrap.ps1").read_text(encoding="utf-8")
        self.assertIn("$globalJsonPath", bootstrap)
        self.assertIn("-InstallDir $repoEnvironment.DotNetRoot", bootstrap)


if __name__ == "__main__":
    unittest.main()
