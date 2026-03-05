import os
import platform
import shutil
import subprocess
import tkinter as tk
import tkinter.filedialog as filedialog
from pathlib import Path
from PIL import Image, ImageTk

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
ENV_SAMPLE = ".env.sample"
ENV_FILE = ".env"
WORKSPACE_SOURCE_KEY = "WORKSPACE_SOURCE"
WORKSPACE_TARGET_KEY = "WORKSPACE_TARGET"
CONTAINER_NAME = "skynet"


class DockerManagerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Skynet")
        self.root.geometry("300x300")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="white")

        self.selected_folder: str = ""
        self.env_values: dict[str, str] = {}
        self._previous_folder: str = ""
        self._folder_changed: bool = False

        self._setup_ui()
        self._check_docker()
        self._initialize_env()

    def _setup_ui(self) -> None:
        folder_frame = tk.Frame(self.root, bg="white")
        folder_frame.pack(fill=tk.X, padx=10, pady=(50, 0))

        self.folder_entry = tk.Entry(
            folder_frame, width=20, state="readonly", bg="#e0e0e0", justify="center"
        )
        self.folder_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        folder_btn = self._create_icon_button(
            folder_frame, "folder.png", "Set Workspace", self._select_folder
        )
        folder_btn.pack(side=tk.LEFT, padx=(5, 0))

        button_frame = tk.Frame(self.root, bg="white")
        button_frame.pack(pady=(25, 0))

        self.start_btn = self._create_icon_button(
            button_frame, "play.png", "Start Skynet", self._start_session
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.connect_btn = self._create_icon_button(
            button_frame, "add.png", "Connect to Skynet", self._connect_session
        )
        self.connect_btn.pack(side=tk.LEFT, padx=10)

        self.reload_btn = self._create_icon_button(
            button_frame, "refresh.png", "Restart Skynet", self._reload_session
        )
        self.reload_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = self._create_icon_button(
            button_frame, "stop.png", "Pause Skynet temporarily", self._stop_session
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        self.nuke_btn = self._create_icon_button(
            button_frame, "remove.png", "Destroy Skynet", self._nuke_session
        )
        self.nuke_btn.pack(side=tk.LEFT, padx=10)

        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.CENTER,
            height=2,
            bg="#c0c0c0",
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_status(self, message: str, error: bool = False) -> None:
        self.status_bar.config(
            text=message,
            fg="red" if error else "black",
            bg="#ffcccc" if error else "lightgray",
        )

    def _create_icon_button(
        self, parent: tk.Widget, icon_name: str, tooltip: str, command: callable
    ) -> tk.Button:
        icon_path = os.path.join(ASSETS_DIR, icon_name)
        try:
            img = Image.open(icon_path)
            img = img.resize((24, 24), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
        except Exception:
            photo = None

        btn = tk.Button(parent, image=photo, command=command, width=32, height=32)
        btn.image = photo

        tooltip_label = tk.Label(
            self.root,
            text=tooltip,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
        )
        tooltip_label.place_forget()

        def on_enter(event: tk.Event) -> None:
            btn_x = btn.winfo_x()
            btn_width = btn.winfo_width()
            tooltip_width = tooltip_label.winfo_reqwidth()
            root_width = self.root.winfo_width()

            if btn_x + btn_width + tooltip_width > root_width:
                x_offset = -tooltip_width
            else:
                x_offset = 0

            tooltip_label.place(in_=btn, x=x_offset, y=btn.winfo_height(), anchor="nw")

        def on_leave(event: tk.Event) -> None:
            tooltip_label.place_forget()

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def _set_button_states(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        self.start_btn.config(state=state)
        self.connect_btn.config(state=state)
        self.stop_btn.config(state=state)
        self.nuke_btn.config(state=state)

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

            if folder_selected != self._previous_folder:
                self._folder_changed = True
                self._set_button_states(False)
                self._update_status(
                    "Workspace changed, reload container to apply changes"
                )
            else:
                self._folder_changed = False
                self._set_button_states(True)
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

        self._previous_folder = self.selected_folder

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
        stop_result = self._run_docker_command(
            ["docker", "compose", "down"], "Reloading session (stopping)..."
        )
        start_result = self._run_docker_command(
            ["docker", "compose", "up", "-d"], "Reloading session (starting)..."
        )

        if stop_result and start_result and self._folder_changed:
            self._folder_changed = False
            self._previous_folder = self.selected_folder
            self._set_button_states(True)
            self._update_status("Container reloaded with new workspace")

    def _nuke_session(self) -> None:
        self._run_docker_command(
            ["docker", "compose", "down", "-v", "--rmi", "all"], "Nuking session..."
        )

    def _connect_session(self) -> None:
        system = platform.system()
        exec_cmd = f"docker exec -it {CONTAINER_NAME} bash"

        try:
            if system == "Windows":
                subprocess.Popen(
                    ["wt", "docker", "exec", "-it", CONTAINER_NAME, "bash"]
                )
            elif system == "Darwin":
                subprocess.Popen(
                    [
                        "osascript",
                        "-e",
                        f'tell app "Terminal" to do script "{exec_cmd}"',
                    ]
                )
            else:
                terminal_emulator = os.environ.get("TERMINAL", "x-terminal-emulator")
                subprocess.Popen([terminal_emulator, "-e", exec_cmd])

            self._update_status("Opening terminal...")
        except Exception as e:
            self._update_status(f"Error: {str(e)}", error=True)


def main() -> None:
    root = tk.Tk()
    DockerManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
