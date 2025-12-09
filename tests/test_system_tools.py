from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from system_tools import configure_logging
from system_tools.bloatware import remove_bloatware
from system_tools.performance import PerformancePreset, apply_performance_preset
from system_tools.registry import RegistryTweak, apply_tweaks
from system_tools.safety import confirm_action
from system_tools.services import ServiceAction, apply_service_actions


class SafetyTests(unittest.TestCase):
    def test_confirm_action_accepts_yes_variations(self) -> None:
        responses = iter(["y", "Yes", "n"])
        input_func = lambda prompt: next(responses)
        self.assertTrue(confirm_action("Proceed?", input_func=input_func))
        self.assertTrue(confirm_action("Proceed?", input_func=input_func))
        self.assertFalse(confirm_action("Proceed?", input_func=input_func))


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        configure_logging()

    @patch("system_tools.registry.ensure_windows")
    @patch("system_tools.registry.create_restore_point")
    @patch("system_tools.registry.backup_registry_key")
    def test_apply_tweaks_prompts_and_applies(self, backup_mock, restore_mock, ensure_mock) -> None:
        tweak = RegistryTweak(
            hive="HKEY_CURRENT_USER",
            path="Software\\Better11",
            name="TestValue",
            value="enabled",
            value_type=1,
        )
        with patch("system_tools.registry.winreg") as winreg_mock:
            winreg_mock.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
            created_keys = {}

            def create_key(hive, path):
                key = MagicMock()
                key.__enter__.return_value = key
                key.__exit__.return_value = False
                created_keys[(hive, path)] = key
                return key

            winreg_mock.CreateKeyEx.side_effect = create_key
            apply_tweaks([tweak], confirm=False, create_restore=True, create_backup=True)
            winreg_mock.SetValueEx.assert_called_once()
            backup_mock.assert_called_once()
            restore_mock.assert_called_once()
            ensure_mock.assert_called()


class ServiceTests(unittest.TestCase):
    @patch("system_tools.services.ensure_windows")
    @patch("system_tools.services.create_restore_point")
    def test_apply_service_actions(self, restore_mock, ensure_mock) -> None:
        actions = [ServiceAction(name="DiagTrack", action="disable")]
        with patch("subprocess.run") as run_mock:
            apply_service_actions(actions, confirm=False)
            run_mock.assert_called_once()
            restore_mock.assert_called_once()
            ensure_mock.assert_called_once()


class BloatwareTests(unittest.TestCase):
    @patch("system_tools.bloatware.ensure_windows")
    @patch("system_tools.bloatware.create_restore_point")
    def test_remove_bloatware_runs_command(self, restore_mock, ensure_mock) -> None:
        with patch("subprocess.run") as run_mock:
            remove_bloatware(["Microsoft.XboxApp"], confirm=False)
            run_mock.assert_called_once()
            restore_mock.assert_called_once()
            ensure_mock.assert_called_once()


class PerformancePresetTests(unittest.TestCase):
    @patch("system_tools.performance.ensure_windows")
    @patch("system_tools.performance.create_restore_point")
    def test_apply_performance_preset_applies_children(self, restore_mock, ensure_mock) -> None:
        preset = PerformancePreset(
            name="High Performance",
            registry_tweaks=[
                RegistryTweak(
                    hive="HKEY_CURRENT_USER",
                    path="Software\\Better11",
                    name="FastStartup",
                    value=1,
                    value_type=4,
                )
            ],
            service_actions=[ServiceAction(name="SysMain", action="disable")],
        )
        with patch("system_tools.performance.apply_tweaks") as tweaks_mock, patch(
            "system_tools.performance.apply_service_actions"
        ) as service_mock:
            apply_performance_preset(preset, confirm=False)
            tweaks_mock.assert_called_once()
            service_mock.assert_called_once()
            restore_mock.assert_called_once()
            ensure_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
