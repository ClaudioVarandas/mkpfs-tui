"""Deploy view: push a built .exfat (or any file) to a jailbroken PS5 over FTP.

Deploy needs no root and no terminal, so unlike the build it runs as a cancelable
Textual worker with a live progress bar. FTP target fields pre-fill from the saved
config; "Save as default" persists them (never the password). Test/Refresh list the
remote directory; Deploy gates on an overwrite confirm when the name already exists.
"""

from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, DataTable, Input, ProgressBar, Static
from textual.worker import get_current_worker

from mkpfs_tui.config import FtpConfig, load, save
from mkpfs_tui.deploy.deployer import DeployOptions, DeployResult, run_deploy
from mkpfs_tui.deploy.ftp import FtpClient, FtpTarget
from mkpfs_tui.messages import DeployFinished, DeployListing, DeployProgressed
from mkpfs_tui.screens.confirm import ConfirmScreen
from mkpfs_tui.widgets.path_field import PathField
from mkpfs_tui.widgets.result_panel import ResultPanel

VIEW_ID = "deploy"


class DeployView(Container):
    """Form + worker for pushing a file to a PS5 over FTP."""

    def compose(self) -> ComposeResult:
        """Render the file/target fields, action buttons, progress, listing, result."""
        yield PathField("Local file", "file", id="deploy-file")
        with Horizontal(classes="field-row"):
            yield Input(id="deploy-host", placeholder="PS5 IP / host")
            yield Input(id="deploy-port", placeholder="port")
            yield Input(id="deploy-user", placeholder="user")
            yield Input(id="deploy-pass", password=True, placeholder="password (blank = anonymous)")
        with Horizontal(classes="field-row"):
            yield Input(id="deploy-path", placeholder="remote directory")
            yield Input(id="deploy-name", placeholder="remote filename (default: same as local)")
        with Horizontal(classes="option-row"):
            yield Button("Test", id="deploy-test")
            yield Button("Refresh listing", id="deploy-refresh")
            yield Button("Deploy", id="deploy-run", variant="primary")
            yield Button("Cancel", id="deploy-cancel", variant="error")
            yield Button("Save as default", id="deploy-save")
        yield ProgressBar(total=100, id="deploy-bar")
        yield Static("", id="deploy-phase")
        yield DataTable(id="deploy-listing")
        yield ResultPanel(id="deploy-result")

    def on_mount(self) -> None:
        """Pre-fill the FTP target from config and set up the listing table."""
        cfg = load()
        self.query_one("#deploy-host", Input).value = cfg.host
        self.query_one("#deploy-port", Input).value = str(cfg.port)
        self.query_one("#deploy-path", Input).value = cfg.path
        self.query_one("#deploy-user", Input).value = cfg.user
        table = self.query_one("#deploy-listing", DataTable)
        table.add_columns("Name", "Size")
        for wid, title in {
            "deploy-host": "PS5 host",
            "deploy-port": "Port",
            "deploy-user": "User",
            "deploy-pass": "Password",
            "deploy-path": "Remote dir",
            "deploy-name": "Remote name",
        }.items():
            self.query_one(f"#{wid}", Input).border_title = title

    def _port(self) -> int:
        """Parse the port field, defaulting to 2121."""
        try:
            return int(self.query_one("#deploy-port", Input).value)
        except (TypeError, ValueError):
            return 2121

    def _target(self) -> FtpTarget:
        """Read the form into an FtpTarget (call on the main thread)."""
        return FtpTarget(
            host=self.query_one("#deploy-host", Input).value.strip(),
            port=self._port(),
            path=self.query_one("#deploy-path", Input).value.strip() or "/data/etaHEN/games/",
            user=self.query_one("#deploy-user", Input).value.strip() or "anonymous",
            password=self.query_one("#deploy-pass", Input).value,
        )

    def _options(self, *, overwrite: bool) -> DeployOptions:
        """Read the form into a DeployOptions."""
        name = self.query_one("#deploy-name", Input).value.strip() or None
        return DeployOptions(
            local_file=Path(self.query_one("#deploy-file", PathField).value),
            target=self._target(),
            remote_name=name,
            overwrite=overwrite,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dispatch the Test / Refresh / Deploy / Cancel / Save buttons."""
        button_id = event.button.id
        if button_id not in {
            "deploy-test",
            "deploy-refresh",
            "deploy-run",
            "deploy-cancel",
            "deploy-save",
        }:
            return
        event.stop()
        if button_id == "deploy-cancel":
            self.app.workers.cancel_group(self, "default")
            self.query_one("#deploy-phase", Static).update("Cancelled.")
        elif button_id == "deploy-save":
            target = self._target()
            save(FtpConfig(host=target.host, port=target.port, path=target.path, user=target.user))
            self.query_one("#deploy-phase", Static).update("Saved default FTP target.")
        elif button_id in {"deploy-test", "deploy-refresh"}:
            self.query_one("#deploy-phase", Static).update("Connecting…")
            self._list(self._target())
        else:  # deploy-run
            self._start(self._options(overwrite=False))

    def _start(self, opts: DeployOptions) -> None:
        """Reset progress and launch the deploy worker."""
        self.query_one("#deploy-bar", ProgressBar).update(progress=0)
        self.query_one("#deploy-phase", Static).update("Uploading…")
        self.query_one("#deploy-result", ResultPanel).show((), ())
        self._deploy(opts)

    @work(thread=True)
    def _list(self, target: FtpTarget) -> None:
        """List the remote directory in a thread; post the rows (or an error)."""
        client = FtpClient()
        error = client.test_connect(target)
        if error:
            self.post_message(DeployListing(VIEW_ID, (), error))
            return
        try:
            rows = tuple(client.list_dir(target, target.path))
        except Exception as exc:  # report any ftplib/OS error to the UI
            self.post_message(DeployListing(VIEW_ID, (), str(exc) or exc.__class__.__name__))
            return
        self.post_message(DeployListing(VIEW_ID, rows, None))

    @work(thread=True, exclusive=True)
    def _deploy(self, opts: DeployOptions) -> None:
        """Run run_deploy in a thread, streaming progress + the final result."""
        worker = get_current_worker()

        def progress(sent: int, total: int) -> None:
            self.post_message(DeployProgressed(VIEW_ID, sent, total))

        result = run_deploy(opts, progress_cb=progress, should_cancel=lambda: worker.is_cancelled)
        self.post_message(DeployFinished(VIEW_ID, result))

    def on_deploy_progressed(self, message: DeployProgressed) -> None:
        """Advance the progress bar."""
        if message.view_id != VIEW_ID or message.total <= 0:
            return
        percent = int(message.sent * 100 / message.total)
        self.query_one("#deploy-bar", ProgressBar).update(progress=percent)

    def on_deploy_listing(self, message: DeployListing) -> None:
        """Fill the listing table, or show the error."""
        if message.view_id != VIEW_ID:
            return
        table = self.query_one("#deploy-listing", DataTable)
        table.clear()
        if message.error is not None:
            self.query_one("#deploy-phase", Static).update(f"Listing failed: {message.error}")
            return
        for name, size in message.rows:
            table.add_row(name, str(size))
        self.query_one("#deploy-phase", Static).update(f"Connected — {len(message.rows)} entries.")

    def on_deploy_finished(self, message: DeployFinished) -> None:
        """Handle confirm-retry, cancel, success, or error from the worker."""
        if message.view_id != VIEW_ID:
            return
        result = message.result
        if not isinstance(result, DeployResult):
            return
        if result.needs_confirm:
            self.query_one("#deploy-phase", Static).update("")
            self.app.push_screen(
                ConfirmScreen(f"{result.remote_path} exists. Overwrite?"),
                lambda ok: self._start(self._options(overwrite=True)) if ok else None,
            )
            return
        panel = self.query_one("#deploy-result", ResultPanel)
        if result.ok:
            self.query_one("#deploy-phase", Static).update("Done.")
            panel.show((), (), (f"Deployed {result.remote_path} — {result.bytes_sent} bytes",))
        elif result.cancelled:
            self.query_one("#deploy-phase", Static).update("Cancelled.")
        else:
            panel.show(("Deploy failed.", *result.errors), ())
