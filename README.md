# DriveMaster Downloads

**DriveMaster Downloads** is a modern, lightweight **desktop downloader** built with **Python + CustomTkinter** and powered by **yt-dlp** (embedded inside the app). It supports downloading from **YouTube**, **Google Drive public links**, and many direct-media URLs—through a clean UI with **progress**, **speed**, **ETA**, **pause/resume**, and **stop** controls.

> **Goal:** Build a single Windows app you can **double‑click to run** (EXE) without asking users to install Python or extra tools.

---

## ✨ Features

* **Turbo embedded engine** using `yt-dlp`
* **One-click UI** (CustomTkinter)
* **Progress bar** + **Speed** + **ETA**
* **Pause / Resume** (soft pause loop)
* **Stop / Cancel**
* Format modes:

  * **Best Video + Audio**
  * **Audio Only (MP3)**
  * **Video Only**
* Authentication modes:

  * **Public Link**
  * **Browser Cookies** (Chrome / Edge / Firefox / Brave / Opera)
  * **Cookies File** (`cookies.txt`)
  * **User/Pass (Basic)** *(only for sites that support it)*
* **Open output folder** button after completion

---

## 🖥️ Supported Platforms

* ✅ **Windows 10/11** (best supported)
* ⚠️ macOS/Linux: possible with modifications (build steps differ)

---

## 🚀 Quick Start (Users)

1. Download the latest release from the **Releases** page.
2. Run `DriveMasterDownloads.exe`.
3. Paste a URL.
4. Choose **Save Location** and **Format**.
5. Click **START DOWNLOAD**.

> Users do **not** need Python installed.

---

## 🔧 Developer Setup

### 1) Clone

```bash
git clone https://github.com/<YOUR-USERNAME>/DriveMaster-Downloads.git
cd DriveMaster-Downloads
```

### 2) Create & activate venv (recommended)

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -U pip
pip install customtkinter yt-dlp pyinstaller
```

---

## 📦 Build a Single EXE (One File)

### Why FFmpeg matters

* **Best Video + Audio** often requires **merging**, and **Audio Only (MP3)** requires conversion.
* That merging/conversion needs **FFmpeg**.

To make your EXE run on any PC **without users installing FFmpeg**, you should **bundle** `ffmpeg.exe` inside your build.

### Step A — Put FFmpeg in the project

Create a folder:

```
ffmpeg/
  ffmpeg.exe
  ffprobe.exe  (optional but recommended)
```

> You can download Windows FFmpeg builds from trusted sources (see FAQ below).

### Step B — Build with PyInstaller (One File)

> Replace `DriveMaster Download.py` with your real filename if different.

```bash
pyinstaller --noconsole --onefile --name "DriveMasterDownloads" \
  --add-binary "ffmpeg/ffmpeg.exe;." \
  --add-binary "ffmpeg/ffprobe.exe;." \
  "DriveMaster Download.py"
```

Output EXE will be in:

```
dist/DriveMasterDownloads.exe
```

✅ Your script already includes logic to detect bundled ffmpeg inside `sys._MEIPASS` and set `ffmpeg_location`.

---

## 🧠 Notes About “No Install / No Extra Files”

What you **can** achieve:

* Users can run a **single EXE** with no Python.
* You can bundle FFmpeg into the EXE so users don’t install it.

What you **cannot** fully control:

* If user selects **Browser Cookies**, the browser must exist on their PC.
* Some websites require sign-in / cookies / DRM restrictions and may block downloads.

---

## 🧪 Troubleshooting

### 1) EXE opens then closes immediately

* Build without `--noconsole` once to see logs:

```bash
pyinstaller --onefile --name "DriveMasterDownloads" "DriveMaster Download.py"
```

### 2) “ffmpeg not found” / merge fails

* Make sure you bundled `ffmpeg.exe` (and ideally `ffprobe.exe`).
* Or switch format to **Video Only** / **Best** that does not need merging.

### 3) Antivirus deletes the EXE

* Some AV tools flag one-file executables.
* Build on a clean machine, keep dependencies updated, and optionally code-sign.

### 4) Google Drive private links fail

* Use **Browser Cookies** or **Cookies File**.
* Public links should work in **Public Link** mode.

---

## 🧾 Legal & Responsible Use

This project is intended for downloading content you have the right to access and save.
Please respect:

* Copyright laws
* Platform terms of service
* Content ownership

---

## 🗂️ Suggested Repo Structure

```
DriveMaster-Downloads/
├─ DriveMaster Download.py
├─ README.md
├─ ffmpeg/
│  ├─ ffmpeg.exe
│  └─ ffprobe.exe
├─ .gitignore
└─ LICENSE
```

---

## 🧰 Tech Stack

* **Python**
* **CustomTkinter** (UI)
* **yt-dlp** (download engine)
* **PyInstaller** (packaging)

---

## 👤 Author

Developed by **AbdulRhman AbdulGhaffar**

---

## 📄 License

Choose one:

* MIT License (recommended for open-source)
* GPL (if you prefer copyleft)

> Add a `LICENSE` file to your repository.

---

## ⭐ Contributing

Contributions are welcome!

1. Fork the repo
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
