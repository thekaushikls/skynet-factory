import os
import shutil
import subprocess
import tkinter as tk
import tkinter.filedialog as filedialog
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
ENV_SAMPLE = ".env.sample"
ENV_FILE = ".env"
WORKSPACE_SOURCE_KEY = "WORKSPACE_SOURCE"
WORKSPACE_TARGET_KEY = "WORKSPACE_TARGET"


class DockerManagerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Docker Session Manager")
        self.root.geometry("600x200")
        self.root.resizable(False, False)

        self.selected_folder: str = ""
        self.env_values: dict[str, str] = {}

        self._setup_ui()
        self._check_docker()
        self._initialize_env()

    def _setup_ui(self) -> None:
        folder_frame = tk.Frame(self.root, pady=10, padx=10)
        folder_frame.pack(fill=tk.X)

        self.folder_entry = tk.Entry(folder_frame, width=50, state="readonly")
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        select_btn = tk.Button(
            folder_frame, text="Select Folder", command=self._select_folder
        )
        select_btn.pack(side=tk.LEFT, padx=(10, 0))

        button_frame = tk.Frame(self.root, pady=10)
        button_frame.pack()

        self.start_btn = tk.Button(
            button_frame, text="Start Session", width=15, command=self._start_session
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(
            button_frame, text="Stop Session", width=15, command=self._stop_session
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.reload_btn = tk.Button(
            button_frame, text="Reload Session", width=15, command=self._reload_session
        )
        self.reload_btn.pack(side=tk.LEFT, padx=5)

        self.nuke_btn = tk.Button(
            button_frame, text="Nuke", width=15, command=self._nuke_session
        )
        self.nuke_btn.pack(side=tk.LEFT, padx=5)

        self.status_bar = tk.Label(
            self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_status(self, message: str, error: bool = False) -> None:
        self.status_bar.config(
            text=message,
            fg="red" if error else "black",
            bg="#ffcccc" if error else "lightgray",
        )

    def _read_env_file(self) -> dict[str, str]:
        env_values: dict[str, str] = {}
        env_path = os.path.join(ROOT_DIR, ENV_FILE)
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_values[key.strip()] = value.strip()
        return env_values

    def _write_env_file(self, env_values: dict[str, str]) -> None:
        env_path = os.path.join(ROOT_DIR, ENV_FILE)
        with open(env_path, "w") as f:
            for key, value in env_values.items():
                f.write(f"{key}={value}\n")

    def _select_folder(self) -> None:
        current_path = self.env_values.get(WORKSPACE_SOURCE_KEY, "./workspace")
        folder_selected = filedialog.askdirectory(initialdir=current_path)
        if folder_selected:
            self.env_values[WORKSPACE_SOURCE_KEY] = folder_selected
            self._write_env_file(self.env_values)
            self.selected_folder = folder_selected
            self.folder_entry.config(state="normal")
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, self.selected_folder)
            self.folder_entry.config(state="readonly")
            self._update_status(f"Updated WORKSPACE_SOURCE to: {folder_selected}")

    def _run_docker_command(self, args: list[str], message: str) -> bool:
        self._update_status(message)
        self.root.update()

        try:
            result = subprocess.run(
                args,
                cwd=ROOT_DIR,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                self._update_status(f"Success: {message}")
                return True
            else:
                error_msg = (
                    result.stderr.strip() or result.stdout.strip() or "Unknown error"
                )
                self._update_status(f"Error: {error_msg}", error=True)
                return False
        except subprocess.TimeoutExpired:
            self._update_status("Error: Command timed out", error=True)
            return False
        except FileNotFoundError:
            self._update_status("Error: docker not found", error=True)
            return False
        except Exception as e:
            self._update_status(f"Error: {str(e)}", error=True)
            return False

    def _is_container_built(self) -> bool:
        try:
            result = subprocess.run(
                ["docker", "compose", "ps", "-a", "--format", "json"],
                cwd=ROOT_DIR,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            return False

    def _check_docker(self) -> None:
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
            if result.returncode != 0:
                self._update_status("Docker is not running", error=True)
        except FileNotFoundError:
            self._update_status("Error: docker not found", error=True)
        except Exception:
            self._update_status("Error: Unable to check docker", error=True)

    def _initialize_env(self) -> None:
        env_path = os.path.join(ROOT_DIR, ENV_FILE)
        env_sample_path = os.path.join(ROOT_DIR, ENV_SAMPLE)

        if not os.path.exists(env_path):
            if os.path.exists(env_sample_path):
                shutil.copy(env_sample_path, env_path)
                self._update_status("Created .env from .env.sample")
            else:
                Path(env_path).touch()
                self._update_status("Created empty .env file")

        self.env_values = self._read_env_file()

        self.selected_folder = self.env_values.get(WORKSPACE_SOURCE_KEY, "./workspace")

        if not os.path.isabs(self.selected_folder):
            self.selected_folder = os.path.join(ROOT_DIR, self.selected_folder)

        self.folder_entry.config(state="normal")
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, self.selected_folder)
        self.folder_entry.config(state="readonly")

    def _start_session(self) -> None:
        if self._is_container_built():
            self._run_docker_command(
                ["docker", "compose", "up", "-d"], "Starting session..."
            )
        else:
            self._run_docker_command(
                ["docker-compose", "up", "-d", "--build"],
                "Building and starting session...",
            )

    def _stop_session(self) -> None:
        self._run_docker_command(["docker", "compose", "down"], "Stopping session...")

    def _reload_session(self) -> None:
        self._run_docker_command(
            ["docker", "compose", "down"], "Reloading session (stopping)..."
        )
        self._run_docker_command(
            ["docker", "compose", "up", "-d"], "Reloading session (starting)..."
        )

    def _nuke_session(self) -> None:
        self._run_docker_command(
            ["docker", "compose", "down", "-v", "--rmi", "all"], "Nuking session..."
        )


def main() -> None:
    root = tk.Tk()
    DockerManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
