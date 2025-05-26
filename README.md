
# QuickFile - Fast File Launcher

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development Roadmap](#development-roadmap)
- [Contribution](#contribution)
- [License](#license)

## Overview

**QuickFile** is a lightweight, cross-platform desktop tool developed in Python that enables users to quickly locate and open files/folders via **fuzzy search** and **persistent file indexing**. Built with the `tkinter` library, it streamlines file access by eliminating the need to manually navigate through complex directory structures. Whether you’re a developer, student, or professional, QuickFile helps you retrieve files in seconds.

## Features

| Feature                          | Description                                                                                                            |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Fuzzy Search**           | Finds files by partial keywords (e.g., typing "report2025" matches "Q2_Report_2025.pdf").                              |
| **Auto-Indexing**          | Builds a silent background index of your files (excluding system directories and large files) for sub-second searches. |
| **Search History**         | Stores the last 20 search queries for quick reuse; double-click to rerun past searches.                                |
| **Rich File Preview**      | Displays file size, modification date, and full path in the results table.                                             |
| **Cross-Platform Support** | Works on Windows, macOS, and Linux with native file-opening commands.                                                  |
| **Intuitive UI**           | Clean, responsive interface with keyboard shortcuts (Enter/Arrow keys).                                                |

## System Requirements

- **OS**: Windows 7+/macOS 10.12+/Linux (Ubuntu/Debian recommended)
- **Python**: 3.6 or newer (with `tkinter` pre-installed)
- **Windows Only**: `pywin32` package for disk enumeration (`pip install pywin32`)

## Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/your-username/QuickFile.git
cd QuickFile
```

### 2. Run the Program

#### **Windows**

```bash
python file_launcher.py
```

#### **macOS/Linux**

```bash
chmod +x file_launcher.py
./file_launcher.py
```

**Note**: The first run may take several minutes to index your files. Check the status bar for progress updates.

## Usage Guide

### 1. Basic Workflow

1. **Enter Keywords**: Type part of a filename (e.g., "budget" or "report.docx") in the search bar.
2. **Press Enter**: Results will populate below, sorted by match relevance.
3. **Open Files**: Double-click a result or select it and press `Enter` to open the file/folder.

### 2. Keyboard Shortcuts

| Key Combo           | Action                          |
| ------------------- | ------------------------------- |
| `Enter`           | Trigger search                  |
| `↓`              | Move focus to results list      |
| `↑/↓` (in list) | Navigate through search results |
| `Esc`             | Clear search query              |

### 3. History Management

- **View History**: Recent searches appear in the left panel.
- **Reuse a Query**: Double-click a history item to rerun the search.
- **Clear History**: Click "Clear History" to delete all saved queries.

## Configuration

### 1. Exclude Directories/File Types

Customize excluded paths and extensions in `file_launcher.py`:

```python
self.excluded_dirs = {
    "System Volume Information", "$Recycle.Bin", "AppData", ".git"  # Add your paths
}
self.excluded_extensions = {
    ".sys", ".dll", ".tmp", ".iso"  # Add file extensions to ignore
}
```

### 2. Index Management

- **Rebuild Index**: Delete `file_index.json` to force a fresh scan on next launch.
- **Limit Index Size**: Adjust the `max_file_size` check in the indexing logic (default: 100MB).

## Troubleshooting

- **Slow Performance**: Ensure `file_index.json` exists (if not, rebuild the index).
- **File Not Found**: Verify the file path in the results; some system files may be inaccessible due to permissions.
- **Crash on Launch (Windows)**: Install `pywin32` via `pip install pywin32`.

## Development Roadmap

- **v1.1**: Global hotkey support (e.g., `Ctrl+Space` to toggle the app).
- **v1.2**: File type filtering (e.g., show only PDFs/Excel files).
- **v1.3**: Dark mode and UI customization.
- **v1.4**: Portable mode (no installation required).

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your changes. For major features, open an issue first to discuss the implementation.

## License

This project is licensed under the **MIT License**. See `LICENSE` for details.

---

**Contact**: For feedback or support, open an issue on the [GitHub repository](https://github.com/your-username/QuickFile) or email `your-email@example.com`.
