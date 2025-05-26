# QuickFile - Fast File Launcher

[English](https://github.com/AKAAKUNLEE/QuickFile/blob/main/README.md) | [中文](https://github.com/AKAAKUNLEE/QuickFile/blob/main/README_zh-CN.md)

## Table of Contents

- [QuickFile - Fast File Launcher](#quickfile---fast-file-launcher)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [System Requirements](#system-requirements)
  - [Installation](#installation)
    - [1. Clone or Download the Repository](#1-clone-or-download-the-repository)
    - [2. Run the Program](#2-run-the-program)
      - [**Windows**](#windows)
      - [**macOS/Linux**](#macoslinux)
  - [Usage Guide](#usage-guide)
    - [1. Basic Workflow](#1-basic-workflow)
    - [2. Workspace Management](#2-workspace-management)
    - [3. Custom Commands](#3-custom-commands)
  - [Configuration](#configuration)
    - [1. Exclude Directories/File Types](#1-exclude-directoriesfile-types)
    - [2. Data Storage](#2-data-storage)
  - [Troubleshooting](#troubleshooting)
  - [Changelog](#changelog)
    - [v1.0.2 (2025-05-28)](#v102-2025-05-28)
    - [v1.0.1 (2025-05-27)](#v101-2025-05-27)
    - [v1.0.0 (2025-05-26)](#v100-2025-05-26)
  - [Contribution](#contribution)
  - [Contact Us](#contact-us)
  - [License](#license)

## Overview

**QuickFile** is a lightweight, cross-platform desktop tool developed in Python. It enables users to quickly locate and open files/folders via **fuzzy search** and **persistent file indexing**. Built with the `tkinter` library, QuickFile streamlines file access by eliminating the need to manually navigate through complex directory structures. Whether you’re a developer, student, or professional, QuickFile helps you retrieve files in seconds.

## Features

| Feature                          | Description                                                                                                            |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Fuzzy Search**           | Finds files by partial keywords (e.g., typing "report2025" matches "Q2_Report_2025.pdf").                              |
| **Auto-Indexing**          | Builds a silent background index of your files (excluding system directories and large files) for sub-second searches. |
| **Search History**         | Stores the last 50 search queries; double-click to rerun past searches.                                                |
| **Workspace Management**   | Create custom workspaces to organize frequently used files, applications, and commands.                                |
| **Application Launcher**   | Launch applications directly from search results, supporting Windows/macOS/Linux.                                      |
| **Custom Commands**        | Add and execute custom commands to extend tool functionality.                                                          |
| **Cross-Platform Support** | Unified experience across Windows, macOS, and Linux.                                                                   |

## System Requirements

- **OS**: Windows 7+/macOS 10.12+/Linux (Ubuntu/Debian recommended)
- **Python**: 3.6 or newer (with `tkinter` pre-installed)
- **Windows Only**: `pywin32` package for disk enumeration (`pip install pywin32`)

## Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/AKAAKUNLEE/QuickFile.git
cd QuickFile
```

### 2. Run the Program

#### **Windows**

```bash
python quickfile.py
```

#### **macOS/Linux**

```bash
chmod +x quickfile.py
./quickfile.py
```

**Note**: The first run may take several minutes to index your files. Check the status bar for progress updates.

## Usage Guide

### 1. Basic Workflow

1. **Select Search Type**: Choose the search type (files, apps, workspaces, or commands) via radio buttons.
2. **Enter Keywords**: Type filename, app name, or command keywords in the search bar.
3. **Press Enter**: Results will populate below, sorted by match relevance.
4. **Execute Action**: Double-click a result to open a file, launch an app, or execute a command.

### 2. Workspace Management

- **Create Workspace**: Click "New" and enter a workspace name.
- **Add Items**: Select search results and click "Add to Workspace".
- **Load Workspace**: Double-click a workspace in the left panel.

### 3. Custom Commands

- Add custom commands via the configuration file in the format `{"Command Name": "Command Content"}`.

## Configuration

### 1. Exclude Directories/File Types

Customize excluded paths and extensions in `quickfile.py`:

```python
self.excluded_dirs = {
    "System Volume Information", "$Recycle.Bin", "AppData", ".git"  # Add your paths
}
self.excluded_extensions = {
    ".sys", ".dll", ".tmp", ".iso"  # Add file extensions to ignore
}
```

### 2. Data Storage

All configuration files are stored in `~/.quickfile`:

- `file_index.json`: File index
- `apps_index.json`: Application index
- `workspaces.json`: Workspace configurations
- `commands.json`: Custom commands
- `history.json`: Search history

## Troubleshooting

- **Slow Performance**: Delete `file_index.json` and restart the program to rebuild the index.
- **File Not Found**: Verify the file path in results; some system files may be inaccessible due to permissions.
- **Crash on Launch (Windows)**: Install `pywin32` via `pip install pywin32`.

## Changelog

### v1.0.2 (2025-05-28)

- Added Chinese/English language switching
- Fixed workspace save path issue
- Optimized application indexing algorithm for faster search
- Improved command execution feedback with output display

### v1.0.1 (2025-05-27)

- Fixed application launch issue on macOS/Linux
- Enhanced fuzzy search algorithm for better matching accuracy
- Added status bar to show current operation progress

### v1.0.0 (2025-05-26)

- Initial release
- Support for file and application search/launch
- Workspace management functionality
- Custom command support

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your changes. For major features, open an issue first to discuss the implementation.

## Contact Us

If you have any questions or suggestions, please contact us via:

- GitHub Repository: [https://github.com/AKAAKUNLEE/QuickFile.git](https://github.com/AKAAKUNLEE/QuickFile.git)
- Email: [WSDJLAK@163.com](mailto:WSDJLAK@163.com)

## License

This project is licensed under the **MIT License**. See `LICENSE` for details.