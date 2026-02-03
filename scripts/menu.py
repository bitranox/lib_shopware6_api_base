"""Interactive TUI menu for running automation targets."""

from __future__ import annotations

import asyncio
import contextlib
import os
import signal
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from rich.text import Text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts._utils import get_project_metadata
from scripts.target_metadata import ParamSpec, TargetSpec, get_targets

PROJECT = get_project_metadata()

if TYPE_CHECKING:
    from textual import events
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.reactive import reactive
    from textual.screen import Screen
    from textual.widgets import (
        Button,
        Footer,
        Input,
        Label,
        ListItem,
        ListView,
        RichLog,
        Select,
        Static,
    )
else:  # pragma: no cover
    try:
        from textual import events
        from textual.app import App, ComposeResult
        from textual.containers import Container, Horizontal, Vertical
        from textual.reactive import reactive
        from textual.screen import Screen
        from textual.widgets import (
            Button,
            Footer,
            Input,
            Label,
            ListItem,
            ListView,
            RichLog,
            Select,
            Static,
        )
    except Exception as exc:  # pragma: no cover - textual import errors surface clearly
        import sys
        import traceback

        print("[menu-tui] Failed to import Textual components:", file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(
            "textual is not installed or incompatible in this environment. Install dev extras: pip install -e .[dev]"
        ) from exc


TARGETS: tuple[TargetSpec, ...] = tuple(target for target in get_targets() if target.name != "menu")


class MenuScreen(Screen[None]):
    """Main selection screen styled to mimic a whiptail menu."""

    BINDINGS = [
        ("enter", "run", "Run target"),
        ("f2", "edit", "Edit parameters"),
        ("escape", "app.quit", "Quit"),
        ("q", "app.quit", "Quit"),
    ]

    selected_index: reactive[int | None] = reactive(None)

    def __init__(self, targets: list[TargetSpec]) -> None:
        """Initialize the menu screen with available targets.

        Args:
            targets: List of automation targets to display in the menu.
        """
        super().__init__()
        self._targets = targets
        self._param_cache: dict[str, dict[str, str]] = {}
        self._pending_target: TargetSpec | None = None
        self._should_run_after_edit = False
        self._status: Static | None = None
        self._buttons: list[Button] = []

    def compose(self) -> ComposeResult:  # type: ignore[override]
        """Build the widget tree for the menu screen."""
        with Container(id="backdrop"), Vertical(id="window", classes="whiptail-window"):
            yield Static(f"{PROJECT.name} — Make Targets", id="title")
            self._description = Static("Select a target and press Enter.", id="description")
            yield self._description
            yield self._build_list()
            self._status = Static("", id="status")
            yield self._status
            yield Static(
                "↑↓ to move • Enter to run • F2 to edit parameters • Esc to quit",
                id="hint",
            )
            with Horizontal(id="buttons"):
                run_btn = Button("Run", id="run-btn")
                edit_btn = Button("Edit Params", id="edit-btn")
                quit_btn = Button("Quit", id="quit-btn")
                self._buttons = [run_btn, edit_btn, quit_btn]
                yield run_btn
                yield edit_btn
                yield quit_btn
        yield Footer()

    def on_mount(self) -> None:  # type: ignore[override]
        """Initialize focus on the menu list after mounting."""
        menu = self.query_one(ListView)
        if menu.children:
            menu.index = 0
            self.selected_index = 0
            menu.focus()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:  # type: ignore[override]
        """Update the description when a different target is highlighted."""
        if event.list_view.id != "menu":
            return
        index = event.list_view.index
        if index is None:
            return
        self.selected_index = index
        self._update_description(index)

    def on_list_view_selected(self, event: ListView.Selected) -> None:  # type: ignore[override]
        """Run the selected target when Enter is pressed on a list item."""
        if event.list_view.id != "menu":
            return
        index = event.list_view.index
        if index is None:
            return
        self.selected_index = index
        self.action_run()

    def on_key(self, event: events.Key) -> None:  # type: ignore[override]
        """Handle left/right arrow keys for button navigation."""
        if event.key not in {"left", "right"}:
            return
        focused = self.focused
        if isinstance(focused, ListView) and event.key == "right":
            self._focus_button(0)
            event.stop()
            return
        if isinstance(focused, Button):
            try:
                current = self._buttons.index(focused)
            except ValueError:
                return
            if event.key == "left":
                if current == 0:
                    self._focus_menu()
                else:
                    self._focus_button(current - 1)
            else:  # right
                next_index = min(current + 1, len(self._buttons) - 1)
                self._focus_button(next_index)
            event.stop()

    def _focus_menu(self) -> None:
        """Return focus to the menu list view."""
        menu = self.query_one(ListView)
        if self.selected_index is not None:
            menu.index = self.selected_index
        menu.focus()

    def _focus_button(self, index: int) -> None:
        """Focus the button at the given index, clamped to valid bounds."""
        if not self._buttons:
            return
        index = max(0, min(index, len(self._buttons) - 1))
        self._buttons[index].focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore[override]
        """Dispatch button press events to the appropriate action."""
        if event.button.id == "run-btn":
            self.action_run()
        elif event.button.id == "edit-btn":
            self.action_edit()
        elif event.button.id == "quit-btn":
            self.menu_app.exit()

    def action_run(self) -> None:
        """Run the currently selected target, prompting for params if needed."""
        target = self._current_target()
        if target is None:
            self.menu_app.bell()
            return
        if target.params:
            self._open_param_editor(target, run_after=True)
            return
        self._launch_run(target, {})

    def action_edit(self) -> None:
        """Open the parameter editor for the current target without running."""
        target = self._current_target()
        if target is None or not target.params:
            self.menu_app.bell()
            return
        self._open_param_editor(target, run_after=False)

    def _build_list(self) -> ListView:
        """Construct the ListView widget populated with target items."""
        items: list[ListItem] = []
        for target in self._targets:
            line = Text()
            line.append(target.name.ljust(16), style="bold")
            line.append(" ")
            line.append(target.description)
            items.append(ListItem(Static(line, classes="item-label"), id=f"target-{target.name}"))
        return ListView(*items, id="menu")

    def _update_description(self, index: int) -> None:
        """Update the description label with the target at the given index."""
        try:
            target = self._targets[index]
        except IndexError:
            self._description.update("Select a target and press Enter.")
            return
        self._description.update(target.description)

    def _current_target(self) -> TargetSpec | None:
        """Return the currently selected target or None if none selected."""
        if self.selected_index is None:
            return None
        try:
            return self._targets[self.selected_index]
        except IndexError:
            return None

    def _open_param_editor(self, target: TargetSpec, *, run_after: bool) -> None:
        """Push the parameter editor screen for the given target."""
        self._pending_target = target
        self._should_run_after_edit = run_after
        preset = self._param_cache.get(target.name, {})
        self.menu_app.push_screen(ParamScreen(target, preset), self._receive_params)

    def _receive_params(self, values: dict[str, str] | None) -> None:
        """Handle parameter values returned from the ParamScreen."""
        target = self._pending_target
        should_run = self._should_run_after_edit
        self._pending_target = None
        self._should_run_after_edit = False
        if target is None:
            return
        if values is None:
            return
        self._param_cache[target.name] = values
        if should_run:
            self._launch_run(target, values)

    def _launch_run(self, target: TargetSpec, env: dict[str, str]) -> None:
        """Push the run screen to execute the target with the given environment."""
        self.menu_app.push_screen(RunScreen(target, env), self._handle_run_result)

    def _handle_run_result(self, exit_code: int | None) -> None:
        """Update the status bar with the result and refocus the menu."""
        if self._status is None:
            return
        if exit_code is None:
            self._status.update("Run cancelled.")
        else:
            self._status.update(f"Last exit code: {exit_code}")
        menu = self.query_one(ListView)
        menu.focus()

    @property
    def menu_app(self) -> MenuApp:
        """Return the parent application typed as MenuApp."""
        app = super().app  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        assert isinstance(app, MenuApp)
        return app


class ParamScreen(Screen[dict[str, str] | None]):
    """Simple whiptail-style form for editing target parameters."""

    BINDINGS = [("escape", "cancel", "Cancel"), ("q", "cancel", "Cancel")]

    def __init__(self, target: TargetSpec, preset: dict[str, str]) -> None:
        """Initialize the parameter editor for a target.

        Args:
            target: Target whose parameters are being edited.
            preset: Previously entered values to pre-fill the form.
        """
        super().__init__()
        self._target = target
        self._preset = preset
        self._inputs: dict[str, Input | Select[str]] = {}
        self._error: Static | None = None
        self._ok_button: Button | None = None

    def compose(self) -> ComposeResult:  # type: ignore[override]
        """Build the parameter form widgets."""
        with Container(id="backdrop"), Vertical(id="window", classes="whiptail-window"):
            yield Static(f"Parameters for {self._target.name}", id="title")
            self._error = Static("", id="error")
            yield self._error
            for param in self._target.params:
                yield Label(param.description)
                preset_value = self._preset.get(param.name, param.default or "")
                if param.choices:
                    widget = Select(
                        tuple((choice, choice) for choice in param.choices),
                        value=preset_value or (param.choices[0] if param.choices else ""),
                        id=f"select-{param.name}",
                    )
                else:
                    widget = Input(
                        value=preset_value,
                        placeholder=param.description,
                        id=f"input-{param.name}",
                    )
                self._inputs[param.name] = widget
                yield widget
            with Horizontal(id="buttons"):
                ok_btn = Button("OK", id="ok-btn")
                self._ok_button = ok_btn
                yield ok_btn
        yield Footer()

    def on_mount(self) -> None:  # type: ignore[override]
        """Focus the OK button after the screen mounts."""
        self._focus_ok_button()

    def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore[override]
        """Submit form values when OK button is pressed."""
        if event.button.id == "ok-btn":
            self._submit()

    def on_input_submitted(self, event: Input.Submitted) -> None:  # type: ignore[override]
        """Submit form when Enter is pressed in an input field."""
        if event.input.id and event.input.id.startswith("input-"):
            self._submit()

    def action_cancel(self) -> None:
        """Dismiss the screen without returning values."""
        self.dismiss(None)

    def _focus_first_input(self) -> None:
        """Move focus to the first input widget in the form."""
        for widget in self._inputs.values():
            widget.focus()
            return

    def _focus_ok_button(self) -> None:
        """Move focus to the OK button."""
        if self._ok_button is not None:
            self._ok_button.focus()

    def _submit(self) -> None:
        """Validate and dismiss with the gathered parameter values."""
        values, error = self._gather_values()
        if error:
            if self._error is not None:
                self._error.update(error)
            self.menu_app.bell()
            self._focus_first_input()
            return
        self.dismiss(values)

    def _gather_values(self) -> tuple[dict[str, str], str | None]:
        """Collect and validate all parameter values from the form widgets."""
        result: dict[str, str] = {}
        for param in self._target.params:
            raw_value = self._extract_widget_value(param.name)
            error = self._validate_param_value(param, raw_value)
            if error:
                return result, error
            result[param.name] = raw_value
        self._apply_bump_defaults(result)
        return result, None

    def _extract_widget_value(self, param_name: str) -> str:
        """Extract the string value from a widget (Input or Select)."""
        widget = self._inputs[param_name]
        if isinstance(widget, Select):
            selection = widget.value
            return selection if isinstance(selection, str) else ""
        return widget.value.strip() or ""

    def _validate_param_value(self, param: ParamSpec, value: str) -> str | None:
        """Validate a parameter value, returning error message if invalid."""
        if param.validator is None or not value:
            return None
        try:
            valid = param.validator(value)
        except Exception:
            valid = False
        if not valid:
            return f"Invalid value for {param.name}"
        return None

    def _apply_bump_defaults(self, result: dict[str, str]) -> None:
        """Apply default PART value for bump target when VERSION is empty."""
        if self._target.name == "bump" and not result.get("VERSION"):
            result["PART"] = result.get("PART") or "patch"

    @property
    def menu_app(self) -> MenuApp:
        """Return the parent application typed as MenuApp."""
        app = super().app  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        assert isinstance(app, MenuApp)
        return app


class RunScreen(Screen[int | None]):
    """Run the selected make target and stream output inside a whiptail-like window."""

    BINDINGS = [("escape", "cancel", "Cancel"), ("q", "cancel", "Cancel")]

    def __init__(self, target: TargetSpec, env: dict[str, str]) -> None:
        """Initialize the run screen with target and environment.

        Args:
            target: Target to execute.
            env: Environment variables to pass to the subprocess.
        """
        super().__init__()
        self._target = target
        self._env = env
        self._log = RichLog(highlight=True, markup=True, id="log")
        self._status = Static("", id="status")
        self._ok_button = Button("OK", id="ok-btn", disabled=True)
        self._proc: asyncio.subprocess.Process | None = None
        self._runner: asyncio.Task[None] | None = None
        self._exit_code: int | None = None

    def compose(self) -> ComposeResult:  # type: ignore[override]
        """Build the run output window widgets."""
        with Container(id="backdrop"), Vertical(id="window", classes="whiptail-window"):
            yield Static(f"Running: make {self._target.name}", id="title")
            env_preview = _format_env(self._env)
            if env_preview:
                yield Static(env_preview, id="env")
            yield self._log
            yield self._status
            with Horizontal(id="buttons"):
                yield self._ok_button
        yield Footer()

    async def on_mount(self) -> None:  # type: ignore[override]
        """Start the subprocess task after the screen mounts."""
        self._status.update("Running… Press Esc to cancel.")
        self._ok_button.focus()
        self._runner = asyncio.create_task(self._run_process())

    async def on_unmount(self) -> None:  # type: ignore[override]
        """Cancel the runner task if still running when unmounting."""
        if self._runner and not self._runner.done():
            self._runner.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._runner

    def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore[override]
        """Dismiss screen with exit code when OK button is pressed."""
        if event.button.id == "ok-btn":
            self.dismiss(self._exit_code)

    def action_cancel(self) -> None:
        """Send cancel signal to process or dismiss screen if finished."""
        if self._proc and self._proc.returncode is None:
            self._send_cancel_signal()
            return
        self.dismiss(self._exit_code)

    async def _run_process(self) -> None:
        """Execute the make target and stream output to the log widget."""
        self._log.write(_format_command(self._env, ["make", self._target.name]))
        env = {k: v for k, v in self._env.items() if v}
        merged_env = os.environ | env
        try:
            self._proc = await asyncio.create_subprocess_exec(
                "make",
                self._target.name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=merged_env,
            )
        except Exception as exc:
            self._log.write(f"[red]Failed to start process:[/] {exc}")
            self._status.update("Process failed to start. Press OK to return.")
            self._ok_button.disabled = False
            self._ok_button.focus()
            return
        assert self._proc.stdout is not None
        assert self._proc.stderr is not None
        await asyncio.gather(
            self._pump(self._proc.stdout, "stdout", "white"),
            self._pump(self._proc.stderr, "stderr", "bright_black"),
        )
        self._exit_code = await self._proc.wait()
        self._log.write(f"\n[b]Exit code:[/] {self._exit_code}")
        self._status.update("Finished. Press OK to return.")
        self._ok_button.disabled = False
        self._ok_button.focus()

    async def _pump(self, stream: asyncio.StreamReader, label: str, style: str) -> None:
        """Read lines from stream and write them to the log widget."""
        while True:
            line = await stream.readline()
            if not line:
                return
            text = line.decode("utf-8", "replace").rstrip("\n")
            if text:
                self._log.write(f"[{style}]{label}[/] {text}")

    def _send_cancel_signal(self) -> None:
        """Send interrupt signal to the running subprocess."""
        assert self._proc is not None
        try:
            if os.name == "nt":
                self._proc.terminate()
                self._log.write("[yellow]Sent terminate to process (Windows).[/]")
            else:
                self._proc.send_signal(signal.SIGINT)
                self._log.write("[yellow]Sent SIGINT to process.[/]")
        except Exception as exc:  # pragma: no cover - defensive logging only
            self._log.write(f"[red]Failed to cancel:[/] {exc}")


class MenuApp(App[None]):
    """Application entry point providing a whiptail-inspired experience."""

    CSS = """
    Screen {
        background: #002b36;
    }
    #backdrop {
        align: center middle;
        padding: 1 1;
    }
    .whiptail-window {
        width: 80%;
        max-width: 110;
        height: 90vh;
        max-height: 90vh;
        border: round #6ea0ff;
        background: #083f7f;
        color: #f5f7ff;
        padding: 1 1;
    }
    #title {
        text-align: center;
        text-style: bold;
    }
    #description {
        color: #cfe2ff;
    }
    #status {
        color: #d9ecff;
    }
    #hint {
        color: #c2d7ff;
    }
    ListView#menu {
        height: 1fr;
        max-height: 1fr;
    }
    ListView#menu > ListItem {
        border: none;
    }
    ListView#menu > ListItem.-highlighted {
        background: #d9ecff;
        color: black;
    }
    .item-label {
        padding: 0 1;
    }
    #buttons {
        content-align: center middle;
        padding-top: 1;
    }
    Button {
        min-width: 12;
    }
    #error {
        height: 1;
        color: #ffb4b4;
    }
    #log {
        height: 16;
        background: black;
        color: #f4f4f4;
        border: solid #6ea0ff;
    }
    #env {
        color: #c0dcff;
    }
    """

    def __init__(self) -> None:
        """Initialize the app with the main menu screen."""
        super().__init__()
        self._menu_screen = MenuScreen(list(TARGETS))

    def on_mount(self) -> None:  # type: ignore[override]
        """Push the main menu screen after the app mounts."""
        self.push_screen(self._menu_screen)


def _format_env(env: dict[str, str]) -> str:
    """Format environment variables for display in the UI."""
    if not env:
        return ""
    pairs = [f"{key}={value}" for key, value in env.items() if value]
    return "Environment: " + " ".join(pairs)


def _format_command(env: dict[str, str], cmd: list[str]) -> str:
    """Format a command with its environment for rich text display."""
    preview_env = " ".join(f"{key}={value}" for key, value in env.items() if value)
    formatted_cmd = " ".join(cmd)
    if preview_env:
        return f"[cyan]{preview_env}[/] [b]{formatted_cmd}[/]"
    return f"[b]{formatted_cmd}[/]"


def run_menu() -> None:
    """Launch the Textual-based automation menu."""
    MenuApp().run()


if __name__ == "__main__":
    run_menu()
