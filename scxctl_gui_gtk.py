import sys
import subprocess
import ast
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio, Pango, Gdk

class SCXCtlGUI(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.bluecxt.scxctl_gui",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.load_css()

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css = b"""
        window {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        .card {
            background-color: #2d2d2d;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        label {
            color: #ffffff;
        }

        entry, dropdown {
            background-color: #3e3e3e;
            color: #ffffff;
            border: 1px solid #4e4e4e;
            border-radius: 6px;
        }

        button {
            border-radius: 8px;
            font-weight: bold;
            padding: 8px 16px;
        }

        .suggested-action {
            background-color: #007acc;
            color: white;
        }

        .destructive-action {
            background-color: #d32f2f;
            color: white;
        }
        
        textview {
            background-color: #1e1e1e;
            color: #cccccc;
            font-family: 'Monospace';
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("scxctl GUI")
        window.set_default_size(500, -1)

        # Header Bar
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)
        window.set_titlebar(header)
        
        refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Status")
        refresh_btn.connect("clicked", self.on_refresh_clicked)
        header.pack_start(refresh_btn)

        # Main Scroll
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_propagate_natural_height(True)
        window.set_child(scrolled)

        # Main Box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        scrolled.set_child(main_box)

        # --- Status Card ---
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        status_box.add_css_class("card")
        
        status_title = Gtk.Label(label="Current Status")
        status_title.set_halign(Gtk.Align.START)
        status_title.add_css_class("title-4")
        status_box.append(status_title)
        
        self.status_label = Gtk.Label(label="Checking...")
        self.status_label.set_use_markup(True)
        self.status_label.set_margin_top(10)
        self.status_label.set_margin_bottom(10)
        status_box.append(self.status_label)
        
        main_box.append(status_box)

        # --- Controls Card ---
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        controls_box.add_css_class("card")
        
        controls_title = Gtk.Label(label="Scheduler Settings")
        controls_title.set_halign(Gtk.Align.START)
        controls_title.add_css_class("title-4")
        controls_box.append(controls_title)

        # Grid for form
        grid = Gtk.Grid()
        grid.set_row_spacing(15)
        grid.set_column_spacing(15)
        controls_box.append(grid)

        # Scheduler
        sched_label = Gtk.Label(label="Scheduler")
        sched_label.set_halign(Gtk.Align.START)
        self.sched_combo = Gtk.DropDown()
        self.sched_model = Gtk.StringList.new(["default"])
        self.sched_combo.set_model(self.sched_model)
        self.sched_combo.set_hexpand(True)
        
        grid.attach(sched_label, 0, 0, 1, 1)
        grid.attach(self.sched_combo, 1, 0, 1, 1)

        # Mode
        mode_label = Gtk.Label(label="Mode")
        mode_label.set_halign(Gtk.Align.START)
        self.mode_combo = Gtk.DropDown()
        self.mode_model = Gtk.StringList.new(["auto", "gaming", "powersave", "lowlatency", "server"])
        self.mode_combo.set_model(self.mode_model)
        self.mode_combo.set_hexpand(True)
        
        grid.attach(mode_label, 0, 1, 1, 1)
        grid.attach(self.mode_combo, 1, 1, 1, 1)

        # Arguments
        args_label = Gtk.Label(label="Arguments")
        args_label.set_halign(Gtk.Align.START)
        self.args_entry = Gtk.Entry()
        self.args_entry.set_placeholder_text("e.g. -v, --performance")
        self.args_entry.set_hexpand(True)
        
        grid.attach(args_label, 0, 2, 1, 1)
        grid.attach(self.args_entry, 1, 2, 1, 1)

        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_halign(Gtk.Align.FILL)  # Fill width
        btn_box.set_margin_top(10)
        
        stop_btn = Gtk.Button(label="Stop / Default")
        stop_btn.connect("clicked", self.on_stop_clicked)
        stop_btn.add_css_class("destructive-action")
        stop_btn.set_hexpand(True)  # Expand horizontally
        
        apply_btn = Gtk.Button(label="Apply Scheduler")
        apply_btn.connect("clicked", self.on_apply_clicked)
        apply_btn.add_css_class("suggested-action")
        apply_btn.set_hexpand(True)  # Expand horizontally
        
        btn_box.append(stop_btn)
        btn_box.append(apply_btn)
        controls_box.append(btn_box)
        
        main_box.append(controls_box)

        # --- Log Card ---
        log_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        log_box.add_css_class("card")
        log_box.set_vexpand(True)
        
        log_title = Gtk.Label(label="Activity Log")
        log_title.set_halign(Gtk.Align.START)
        log_title.add_css_class("title-4")
        log_box.append(log_title)
        
        log_scroll = Gtk.ScrolledWindow()
        log_scroll.set_min_content_height(150)
        log_scroll.set_vexpand(True)
        
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.log_view.set_monospace(True)
        self.log_view.set_bottom_margin(10)
        self.log_view.set_top_margin(10)
        self.log_view.set_left_margin(10)
        self.log_view.set_right_margin(10)
        
        self.log_buffer = self.log_view.get_buffer()
        log_scroll.set_child(self.log_view)
        log_box.append(log_scroll)
        
        main_box.append(log_box)

        window.present()
        
        # Initial Load
        GLib.idle_add(self.list_schedulers)

    def run_command(self, args):
        try:
            result = subprocess.run(["scxctl"] + args, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"❌ Error: {e.stderr.strip() or e.stdout.strip()}"
        except FileNotFoundError:
             return "❌ Error: scxctl not found in PATH"

    def append_log(self, cmd, text):
        end_iter = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end_iter, f"[{cmd}]\n{text}\n\n")
        # Auto scroll
        mark = self.log_buffer.create_mark(None, end_iter, False)
        self.log_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

    def list_schedulers(self):
        output = self.run_command(["list"])
        
        items = ["default"]
        for line in output.splitlines():
            if "supported schedulers:" in line:
                try:
                    sched_list = line.split("supported schedulers:")[1].strip()
                    schedulers = ast.literal_eval(sched_list)
                    items.extend(schedulers)
                except:
                    pass
        
        self.sched_model = Gtk.StringList.new(items)
        self.sched_combo.set_model(self.sched_model)
        
        self.get_status()

    def get_status(self):
        output = self.run_command(["get"])
        self.append_log("get", output)
        self.update_ui_from_status(output)

    def update_ui_from_status(self, output):
        text_lower = output.strip().lower()
        if "no scx scheduler running" in text_lower:
            self.status_label.set_markup("<span foreground='#4caf50' weight='bold' size='x-large'>🟢 Default Kernel Scheduler</span>")
            self.set_combo_active_string(self.sched_combo, "default")
            return

        if text_lower.startswith("running"):
            parts = output.split()
            active_sched = parts[1].strip() if len(parts) >= 2 else "Unknown"
            
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

            active_mode = "Default"
            if " in " in output.lower():
                try:
                    active_mode = output.lower().split(" in ", 1)[1].split()[0].strip()
                except:
                    pass
            
            self.status_label.set_markup(f"<span foreground='#2196f3' weight='bold' size='x-large'>{emoji} {active_sched}</span>\n<span size='medium' color='#aaaaaa'>Mode: {active_mode}</span>")
            self.set_combo_active_string(self.sched_combo, active_sched)
            self.set_combo_active_string(self.mode_combo, active_mode)

    def set_combo_active_string(self, combo, text):
        model = combo.get_model()
        if not model: return
        for i in range(model.get_n_items()):
            item = model.get_string(i)
            if item.lower() == text.lower():
                combo.set_selected(i)
                break

    def on_refresh_clicked(self, btn):
        self.get_status()

    def on_stop_clicked(self, btn):
        output = self.run_command(["stop"])
        self.append_log("stop", output)
        self.get_status()

    def on_apply_clicked(self, btn):
        selected_idx = self.sched_combo.get_selected()
        if selected_idx == Gtk.INVALID_LIST_POSITION:
            return
        
        sched = self.sched_model.get_string(selected_idx)
        
        mode_idx = self.mode_combo.get_selected()
        mode = self.mode_model.get_string(mode_idx) if mode_idx != Gtk.INVALID_LIST_POSITION else ""
        
        args = self.args_entry.get_text()

        if sched == "default":
            self.on_stop_clicked(None)
            return

        status_output = self.run_command(["get"])
        if "no scx scheduler running" in status_output.lower():
            cmd = ["start", "-s", sched]
        else:
            cmd = ["switch", "-s", sched]

        if mode:
            cmd += ["-m", mode]
        if args:
            cmd += ["-a", args]

        output = self.run_command(cmd)
        self.append_log(cmd[0], output)
        self.get_status()

if __name__ == "__main__":
    app = SCXCtlGUI()
    app.run(sys.argv)
