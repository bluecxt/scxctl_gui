# 🎮 scxctl_gui

> A minimal, modern GUI for **scxctl** to manage your sched_ext schedulers with ease. Available in **Qt6** (KDE) and **GTK4** (GNOME) flavors.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Qt6](https://img.shields.io/badge/Qt-6-green?style=for-the-badge&logo=qt&logoColor=white)
![GTK4](https://img.shields.io/badge/GTK-4-orange?style=for-the-badge&logo=gtk&logoColor=white)

> **⭐ Please star this repository to show support! It motivates me to make the project better for everyone.**

---

## 📖 Overview

**scxctl_gui** provides a user-friendly graphical interface for `scxctl`, the command-line tool used to manage extensible schedulers (sched_ext) on Linux. Instead of remembering command-line arguments, you can switch schedulers, change modes, and monitor status with a few clicks.

> **Caution:** This project is under active development. Ensure you have a compatible kernel and `scxctl` installed.

## ✨ Features

### ✅ Fully Implemented

* **🎨 Two Flavors:**
    * **Qt6 Version:** Perfect for KDE Plasma and other Qt-based environments.
    * **GTK4 Version:** Native look and feel for GNOME and GTK-based desktops.
* **🔄 Real-time Status:** View the currently running scheduler and its mode with visual indicators (emojis 🦀, 🚀, etc.).
* **🚀 Easy Switching:** Select from a list of supported schedulers detected on your system.
* **⚙️ Mode Management:** Quickly toggle between modes like `gaming`, `powersave`, `lowlatency`, and `server`.
* **⌨️ Custom Arguments:** Pass additional flags and arguments to the scheduler directly from the GUI.
* **⛔ One-Click Stop:** Revert to the default kernel scheduler instantly.
* **📦 Portable:** Available as standalone AppImages.

## 🛠️ Prerequisites

* **Linux Kernel** with `sched_ext` support.
* **scxctl** installed and available in your system PATH.
* **For GTK version:** System packages `python3-gi` and `gir1.2-gtk-4.0` must be installed on the target system.

## 🖥️ Installation Guide

### 📦 AppImage (Recommended)

1. Download the latest `.AppImage` release from the **Releases** section.
   * Choose `scxctl_gui_qt-*.AppImage` for KDE/Qt.
   * Choose `scxctl_gui_gtk-*.AppImage` for GNOME/GTK.
2. Make it executable:

   ```bash
   chmod +x scxctl_gui_qt-x86_64.AppImage
   # or
   chmod +x scxctl_gui_gtk-x86_64.AppImage
   ```

3. Run it:

   ```bash
   ./scxctl_gui_qt-x86_64.AppImage
   ```

### 🔧 Running from Source

#### Qt Version
1. Install dependencies:
   ```bash
   pip install PyQt6
   ```
2. Run:
   ```bash
   python3 scxctl_gui_qt.py
   ```

#### GTK Version
1. Install dependencies (Ubuntu/Debian):
   ```bash
   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
   ```
2. Run:
   ```bash
   python3 scxctl_gui_gtk.py
   ```

## 🏗️ Building from Source

To build the AppImages yourself, you can use the provided build script.

1. Ensure you have `pyinstaller` and `wget` installed.
2. Run the build script:

   ```bash
   # Build both versions
   ./build.sh

   # Build only Qt version
   ./build.sh qt

   # Build only GTK version
   ./build.sh gtk
   ```

3. The output AppImages will be generated in the current directory.

## 📸 Screenshots

Screenshots coming soon.

## 🖥️ Troubleshooting

* **"No scx scheduler running"**: This means the default kernel scheduler is active. Use the GUI to start a scheduler.
* **Scheduler list empty**: Ensure `scxctl` is in your PATH and that `scxctl list` returns valid output.
* **Permission denied**: You might need `sudo` privileges depending on how `scxctl` is configured on your system, though typically it runs in userspace communicating with the kernel.

## ❤️ Powered by

* **[scxctl](https://github.com/sched-ext/scx)**: The underlying tool for managing sched_ext.
* **[PyQt6](https://pypi.org/project/PyQt6/)** & **[PyGObject](https://pygobject.readthedocs.io/)**: For the graphical user interfaces.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the interface or add new features.

## 📄 License

This project is open source.
