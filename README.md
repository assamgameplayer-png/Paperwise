<div align="center">

# 📚 PaperWise

**A research paper organizer built by a student, for students.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow.svg)](https://python.org)
[![KivyMD](https://img.shields.io/badge/KivyMD-1.2.0-green.svg)](https://kivymd.readthedocs.io)
[![Platform](https://img.shields.io/badge/Platform-Android%20%7C%20Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

*Stop losing your research papers in a mess of browser tabs and sticky notes.*

</div>

---

## 🤔 Why I Built This

I'm a student doing research and I kept running into the same problem — I'd find a great paper on Google Scholar, save it somewhere vague, and then spend 20 minutes hunting for it later when I actually needed to cite it. My notes app wasn't built for this. Spreadsheets felt overkill. Zotero is powerful but heavy.

So I built PaperWise. It's lightweight, runs on my phone and my laptop, stores everything locally, and generates APA/MLA citations in one tap. Nothing fancy — just something that solves the actual problem.

If you're a student doing literature reviews, thesis work, or just keeping track of reading — I hope this helps you too.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📖 **Paper Library** | Add, search, and manage your research papers |
| 🔍 **Quick Search** | Filter by title, author, keyword, or journal instantly |
| 📝 **APA & MLA Citations** | Auto-generated citations — one tap to copy |
| 🏷️ **Keywords / Tags** | Organize papers by topic with comma-separated tags |
| 🌐 **External Search** | Jump to Google Scholar or Shodhganga right from the app |
| 💾 **Local Storage** | All data stays on your device — no account, no cloud |
| 📱 **Mobile + Desktop** | Same codebase runs on Android and PC |

---

## 📸 Screenshots

> *(Add screenshots here after running the app — drag images into this section on GitHub)*

| Library | Add Paper | Citation |
|---|---|---|
| `screenshot_library.png` | `screenshot_add.png` | `screenshot_cite.png` |

---

## 🚀 Getting Started

### Run on Desktop (Windows / Linux / macOS)

Make sure you have Python 3.8 or higher installed.

```bash
# 1. Clone this repo
git clone https://github.com/YOUR_USERNAME/paperwise.git
cd paperwise

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

That's it. No setup wizard, no config files.

---

### Build for Android

You'll need a Linux machine (or WSL on Windows) for this.

```bash
# Install buildozer
pip install buildozer

# First build — downloads Android SDK/NDK automatically (takes a while!)
buildozer android debug

# Your APK will be here:
# bin/paperwise-2.0-debug.apk
```

Transfer the APK to your phone via USB or Google Drive, install it (you may need to allow "Install from unknown sources" in your phone settings), and you're good.

---

## 📁 Project Structure

```
paperwise/
├── main.py              # Entire app — UI + logic
├── requirements.txt     # Python dependencies
├── buildozer.spec       # Android build configuration
├── LICENSE              # MIT License
├── CONTRIBUTING.md      # How to contribute
└── README.md            # This file
```

All paper data is saved in `paperwise_papers.json` in the app folder. You can back it up or copy it between devices freely.

---

## 🗺️ Roadmap

Things I want to add — contributions are very welcome!

- [ ] Import from `.bib` (BibTeX) file
- [ ] Export full library as a formatted reference list
- [ ] Chicago citation style
- [ ] Sort papers by year, author, or date added
- [ ] Dark mode toggle
- [ ] PDF attachment support
- [ ] Filter view by tag/keyword

---

## 🛠️ Built With

- **[Python](https://python.org)** — core language
- **[Kivy](https://kivy.org)** — cross-platform UI framework
- **[KivyMD](https://kivymd.readthedocs.io)** — Material Design components for Kivy
- **[Buildozer](https://buildozer.readthedocs.io)** — Android packaging tool

---

## 🤝 Contributing

All contributions are welcome — bug reports, ideas, code, or docs. Read [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

If you're a fellow student who uses the app and has ideas, open an Issue. I genuinely want to hear what would make this more useful.

---

## 📄 License

This project is under the **MIT License** — see [LICENSE](LICENSE) for details.

Free to use, fork, and build on. If you do something cool with it, I'd love to know!

---

<div align="center">

Made with 💙 by a student tired of losing research papers

*If this helped you, consider giving it a ⭐ — it means a lot!*

</div>
