import sys
import subprocess
import ast
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QTextEdit, QHBoxLayout, QMessageBox,
    QGroupBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SCXCtlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("scxctl GUI")
        self.resize(500, 650)
        self.apply_stylesheet()

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- Header / Status Section ---
        # Header Layout for Title/Refresh
        header_layout = QHBoxLayout()
        
        self.status_group = QGroupBox("Current Status")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("Checking...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold)) # Larger font like GTK
        status_layout.addWidget(self.status_label)
        self.status_group.setLayout(status_layout)
        
        main_layout.addWidget(self.status_group)
        
        # Refresh Button (Small, top right-ish feel, but here we put it above or below status?)
        # Let's put it in a small row above status or inside status?
        # To match GTK "HeaderBar" feel, we can't easily, but we can add a refresh button 
        # at the top right of the window content.
        
        top_bar = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("Refresh Status")
        self.refresh_btn.setFixedSize(40, 40)
        self.refresh_btn.setObjectName("refreshBtn")
        top_bar.addWidget(self.refresh_btn)
        top_bar.addStretch()
        
        # Insert top bar before status group? Or maybe just keep refresh separate.
        # Actually, let's put the refresh button IN the status group layout for now or just above it.
        # Let's put it above the status group to simulate a toolbar action.
        main_layout.insertLayout(0, top_bar)

        # --- Controls Section ---
        self.controls_group = QGroupBox("Scheduler Settings")
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15) # Increased spacing

        # Scheduler Selection
        sched_layout = QHBoxLayout()
        sched_label = QLabel("Scheduler:")
        sched_label.setFixedWidth(100)
        self.sched_combo = QComboBox()
        self.sched_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sched_layout.addWidget(sched_label)
        sched_layout.addWidget(self.sched_combo)
        controls_layout.addLayout(sched_layout)

        # Mode Selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode:")
        mode_label.setFixedWidth(100)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["auto", "gaming", "powersave", "lowlatency", "server"])
        self.mode_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        controls_layout.addLayout(mode_layout)

        # Arguments Input
        args_layout = QHBoxLayout()
        args_label = QLabel("Arguments:")
        args_label.setFixedWidth(100)
        self.args_input = QLineEdit()
        self.args_input.setPlaceholderText("e.g. -v, --performance")
        args_layout.addWidget(args_label)
        args_layout.addWidget(self.args_input)
        controls_layout.addLayout(args_layout)

        # --- Action Buttons (Inside Controls Group like GTK) ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.stop_btn = QPushButton("Stop / Default")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.stop_btn.setMinimumHeight(40)

        self.set_btn = QPushButton("Apply Scheduler")
        self.set_btn.setObjectName("applyBtn")
        self.set_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.set_btn.setMinimumHeight(40)
        
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.set_btn)
        controls_layout.addLayout(btn_layout)

        self.controls_group.setLayout(controls_layout)
        main_layout.addWidget(self.controls_group)

        # --- Log Output ---
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout()
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        log_layout.addWidget(self.output)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        self.setLayout(main_layout)

        # Connections
        self.refresh_btn.clicked.connect(self.get_status)
        self.set_btn.clicked.connect(self.set_scheduler)
        self.stop_btn.clicked.connect(self.stop_scheduler)
        self.sched_combo.currentTextChanged.connect(self.on_scheduler_changed)

        # Initial Load
        self.list_schedulers()

    def apply_stylesheet(self):
        # Modern Dark Theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #3e3e3e;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
                color: #cccccc;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 5px;
                color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #3e3e3e;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4e4e4e;
            }
            QPushButton:pressed {
                background-color: #2e2e2e;
            }
            QPushButton#applyBtn {
                background-color: #007acc;
            }
            QPushButton#applyBtn:hover {
                background-color: #0062a3;
            }
            QPushButton#stopBtn {
                background-color: #d32f2f;
            }
            QPushButton#stopBtn:hover {
                background-color: #b71c1c;
            }
            QLabel {
                color: #dddddd;
            }
        """)

    def run_command(self, args: list[str]) -> str:
        try:
            result = subprocess.run(["scxctl"] + args, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"❌ Error: {e.stderr.strip() or e.stdout.strip()}"
        except FileNotFoundError:
             return "❌ Error: scxctl not found in PATH"

    def update_selection_from_status(self, output: str):
        text_lower = output.strip().lower()
        
        # Update Status Label
        if "no scx scheduler running" in text_lower:
            self.status_label.setText("🟢 Default Kernel Scheduler (No SCX)")
            self.status_label.setStyleSheet("color: #4caf50;") # Green
            
            idx = self.sched_combo.findText("default", Qt.MatchFlag.MatchFixedString)
            if idx != -1:
                self.sched_combo.setCurrentIndex(idx)
            self.mode_combo.setCurrentIndex(0)
            return
        
        if text_lower.startswith("running"):
            active_sched = "Unknown"
            active_mode = "Default"

            parts = output.split()
            if len(parts) >= 2:
                active_sched = parts[1].strip()

            # Determine emoji based on scheduler name
            emoji = "🚀"
            n = active_sched.lower()
            if "rust" in n: emoji = "🦀"
            elif "lavd" in n: emoji = "🌋"
            elif "flash" in n: emoji = "⚡"
            elif "cosmos" in n: emoji = "🌌"
            elif "bpfland" in n: emoji = "🎢"
            elif "p2dq" in n: emoji = "🏎️"
            elif "tickless" in n: emoji = "🕰️"
            elif "mitosis" in n: emoji = "🧬"
            elif "central" in n: emoji = "🎯"
            elif "layer" in n: emoji = "🍰"
            elif "nest" in n: emoji = "🪺"
            elif "joule" in n: emoji = "🔋"
            elif "flat" in n: emoji = "🥞"
            elif "pair" in n: emoji = "👯"
            elif "simple" in n: emoji = "👶"
            elif "bpf" in n: emoji = "🐝"

            if " in " in output.lower():
                try:
                    after_in = output.lower().split(" in ", 1)[1]
                    active_mode = after_in.split()[0].strip()
                except IndexError:
                    active_mode = "Default"
            
            self.status_label.setText(f"{emoji} Running: {active_sched} ({active_mode})")
            self.status_label.setStyleSheet("color: #2196f3;") # Blue

            if active_sched:
                idx_sched = self.sched_combo.findText(active_sched.lower(), Qt.MatchFlag.MatchFixedString)
                if idx_sched != -1:
                    self.sched_combo.setCurrentIndex(idx_sched)
            if active_mode:
                idx_mode = self.mode_combo.findText(active_mode.lower(), Qt.MatchFlag.MatchFixedString)
                if idx_mode != -1:
                    self.mode_combo.setCurrentIndex(idx_mode)

    def get_status(self):
        output = self.run_command(["get"])
        self.append_output("get", output)
        self.update_selection_from_status(output)
        return output

    def list_schedulers(self):
        output = self.run_command(["list"])
        self.sched_combo.clear()
        self.sched_combo.addItem("default")

        for line in output.splitlines():
            if "supported schedulers:" in line:
                try:
                    sched_list = line.split("supported schedulers:")[1].strip()
                    schedulers = ast.literal_eval(sched_list)
                    for sched in schedulers:
                        self.sched_combo.addItem(sched)
                except Exception as e:
                    self.append_output("parse_error", f"Parse error: {e}")

        status = self.run_command(["get"])
        self.update_selection_from_status(status)

    def set_scheduler(self):
        sched = self.sched_combo.currentText().strip().lower()
        mode = self.mode_combo.currentText()
        args = self.args_input.text()

        if not sched:
            QMessageBox.warning(self, "Error", "Please select a scheduler.")
            return

        if sched == "default":
            self.stop_scheduler()
            return

        status_output = self.run_command(["get"])
        status_lower = status_output.lower()

        if "no scx scheduler running" in status_lower:
            cmd = ["start", "-s", sched]
        else:
            # Check if we are just switching modes or schedulers
            # Simplified logic for now, just switch
            cmd = ["switch", "-s", sched]

        if mode:
            cmd += ["-m", mode]
        if args:
            # Split args string into list, respecting quotes if possible, but simple split for now
            cmd += ["-a", args]

        output = self.run_command(cmd)
        self.append_output(f"start/switch {sched}", output)
        
        # Refresh status after action
        self.get_status()

    def stop_scheduler(self):
        output = self.run_command(["stop"])
        self.append_output("stop", output)
        self.get_status()

    def on_scheduler_changed(self, text: str):
        is_default = (text.strip().lower() == "default")
        self.mode_combo.setEnabled(not is_default)
        self.args_input.setEnabled(not is_default)

    def append_output(self, cmd, text):
        self.output.append(f"<b>[{cmd}]</b><br>{text}<br>")
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SCXCtlGUI()
    gui.show()
    sys.exit(app.exec())
