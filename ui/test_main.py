import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main import DockerManagerApp


class TestDockerManagerApp(unittest.TestCase):
    def setUp(self):
        with patch("ui.main.tk.Tk"):
            self.root = MagicMock()
            self.app = DockerManagerApp.__new__(DockerManagerApp)
            self.app.root = self.root
            self.app.selected_folder = "/test/folder"
        self.app.env_values = {"WORKSPACE_SOURCE": "/test/folder"}
        self.app._update_status = MagicMock()
        self.app._folder_changed = False
        self.app._previous_folder = "/test/folder"

    @patch("ui.main.subprocess.run")
    def test_start_session_container_not_built(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        self.app._is_container_built = MagicMock(return_value=False)
        self.app._start_session()

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "docker-compose")
        self.assertIn("up", args)
        self.assertIn("--build", args)

    @patch("ui.main.subprocess.run")
    def test_start_session_container_already_built(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        self.app._is_container_built = MagicMock(return_value=True)
        self.app._start_session()

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "docker")
        self.assertEqual(args[1], "compose")
        self.assertIn("up", args)
        self.assertNotIn("--build", args)

    @patch("ui.main.subprocess.run")
    def test_stop_session(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        self.app._stop_session()

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "docker")
        self.assertEqual(args[1], "compose")
        self.assertEqual(args[2], "down")

    @patch("ui.main.subprocess.run")
    def test_reload_session(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        self.app._reload_session()

        self.assertEqual(mock_run.call_count, 2)

        first_call = mock_run.call_args_list[0][0][0]
        self.assertEqual(first_call[0], "docker")
        self.assertEqual(first_call[1], "compose")
        self.assertEqual(first_call[2], "down")

        second_call = mock_run.call_args_list[1][0][0]
        self.assertEqual(second_call[0], "docker")
        self.assertEqual(second_call[1], "compose")
        self.assertEqual(second_call[2], "up")

    @patch("ui.main.subprocess.run")
    def test_nuke_session(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        self.app._nuke_session()

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "docker")
        self.assertEqual(args[1], "compose")
        self.assertEqual(args[2], "down")
        self.assertIn("-v", args)
        self.assertIn("--rmi", args)
        self.assertEqual(args[args.index("--rmi") + 1], "all")

    @patch("ui.main.subprocess.run")
    def test_is_container_built_true(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout='[{"Name": "container"}]', stderr=""
        )

        result = self.app._is_container_built()

        self.assertTrue(result)

    @patch("ui.main.subprocess.run")
    def test_is_container_built_false(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = self.app._is_container_built()

        self.assertFalse(result)

    @patch("ui.main.platform.system")
    @patch("ui.main.subprocess.Popen")
    def test_connect_session_linux(self, mock_popen, mock_system):
        mock_system.return_value = "Linux"

        self.app._connect_session()

        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        self.assertEqual(args[0], "x-terminal-emulator")
        self.assertIn("-e", args)
        exec_cmd = " ".join(args)
        self.assertIn("docker exec", exec_cmd)
        self.assertIn("skynet-debug-develop", exec_cmd)

    @patch("ui.main.platform.system")
    @patch("ui.main.subprocess.Popen")
    def test_connect_session_windows(self, mock_popen, mock_system):
        mock_system.return_value = "Windows"

        self.app._connect_session()

        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        self.assertEqual(args[0], "start")
        self.assertEqual(args[1], "wt")

    @patch("ui.main.platform.system")
    @patch("ui.main.subprocess.Popen")
    def test_connect_session_mac(self, mock_popen, mock_system):
        mock_system.return_value = "Darwin"

        self.app._connect_session()

        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        self.assertEqual(args[0], "osascript")


if __name__ == "__main__":
    unittest.main()
