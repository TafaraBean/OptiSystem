# OptiSystem

OptiSystem is a lightweight, interactive personal productivity hub and study engine built with Python and Shiny. It is designed to help you read and annotate your study material, practise active recall, and systematically track your study metrics.

## 🚀 Features

* **📊 Analytics Dashboard:** Native web-rendered charts (powered by Chart.js) that visualize your daily and weekly study time, split into Encoding (Reading) and Retrieval (Blurt). KPI cards show today's reading and blurting minutes and your weekly recall ratio (goal: 80%).
* **📖 Reading Room:** Upload a PDF or paste source text/LaTeX and take notes side by side in an enhanced Markdown editor (EasyMDE) with full math support (KaTeX), a LaTeX symbol toolbar and image pasting. A conceptual coverage meter shows how much of the source your notes have captured and highlights what you've missed. For PDFs, **Mark Visual Area** crops a region of a page straight into your notes. Notes are saved as Markdown files per module and can be loaded, renamed, deleted or exported to PDF (via your browser's print dialog). Saving logs your reading time.
* **🧠 Blurt Studio:** Pick a saved note and OptiSystem turns its headings into a blank template. Write down everything you remember, then submit to see a semantic coverage score against the original, heading by heading, plus an engagement score based on idle breaks. A session timer automatically logs your study duration for data tracking.
* **🎮 Gamification:** Earn XP and levels, keep a daily streak, and complete three daily quests. A session timer sits in the header, a focus bar along the top of the page drains while you're inactive, and an idle overlay appears after 3 minutes without activity.

## 🛠️ Tech Stack

* **Backend:** Python, Shiny for Python (PyShiny), Pandas, NumPy, SciPy
* **PDF & NLP (optional):** PyMuPDF (`fitz`) for reading PDFs, sentence-transformers (`BAAI/bge-small-en-v1.5`) for semantic coverage scoring
* **Frontend:** HTML/CSS, JavaScript
* **Libraries:** Chart.js (Dashboards), EasyMDE (Text Editor), KaTeX (Math Rendering), highlight.js (Code Highlighting)

## 💻 Installation & Setup (Beginner Friendly)

If you have never coded before or don't have GitHub set up, don't worry! Follow these steps to get OptiSystem running on your machine.

### Step 1: Get the Tools
1. **Download Python:** Go to [python.org](https://www.python.org/downloads/) and download the latest version for your computer (OptiSystem needs Python 3.11 or newer). 
   * ⚠️ **CRITICAL (Windows Users):** When the installer opens, make sure to check the box at the very bottom that says **"Add Python.exe to PATH"** *before* you click Install.
2. **Download a Code Editor:** We recommend [Visual Studio Code (VS Code)](https://code.visualstudio.com/). It is a free, lightweight program that makes running the app very easy.

### Step 2: Get the OptiSystem Code
1. Scroll to the top of this GitHub page.
2. Click the green **"<> Code"** button.
3. Click **"Download ZIP"**.
4. Find the downloaded ZIP file on your computer, right-click it, and select **Extract All**. Move this extracted folder somewhere easy to find (like your Documents or Desktop).

### Step 3: Open the Project
1. Open Visual Studio Code.
2. Click **File > Open Folder...** at the top left, and select the OptiSystem folder you just extracted (it will be called something like `OptiSystem-main`).
3. Open the Terminal inside VS Code by clicking **Terminal > New Terminal** at the very top menu. A small command-line window will appear at the bottom of your screen.

### Step 4: Run the Setup Commands
In that terminal window at the bottom, type or paste these commands exactly as shown, pressing **Enter** after each step. 

**1. Create a "Virtual Environment"** *(This creates a safe, isolated bubble for the app's files so it doesn't mess with your computer).*
* **Windows:** `python -m venv .venv`
* **Mac/Linux:** `python3 -m venv .venv`

**2. Activate the Environment**
* **Windows:** `.venv\Scripts\activate`
* **Mac/Linux:** `source .venv/bin/activate`
*(You will know this worked if you see `(.venv)` appear at the start of your terminal line).*

**3. Install the required libraries**
*(This downloads the specific tools OptiSystem needs to run).*
* Type: `pip install -r requirements.txt`
* Then type: `pip install scipy` *(OptiSystem needs SciPy, which isn't in `requirements.txt` yet).*
* **Optional:** `pip install pymupdf sentence-transformers` *(Turns on PDF text extraction, **Mark Visual Area**, and the coverage scoring in the Reading Room and Blurt Studio. Without them the app still runs, but coverage scores stay at 0%. sentence-transformers also installs PyTorch, which is a large download, and fetches a small language model the first time the app starts).*

**4. Start the App!**
* Type: `shiny run --launch-browser OptiSystem.py`

🎉 *OptiSystem will automatically open in your default web browser at http://127.0.0.1:8000 (if it doesn't, open that address yourself). Keep the VS Code window open and running in the background while you use the app. When you are done studying, click inside the terminal and press `Ctrl + C` to shut the server down.*

## 📁 Project Structure

```
OptiSystem/
├── OptiSystem.py      # The whole app: UI, server logic and embedded CSS/JavaScript
├── requirements.txt   # Pinned Python dependencies
└── OptiSystem_Data/   # Your notes, images, PDFs and study logs (see below)
```

## 🗂️ Data Folder

OptiSystem saves everything in `OptiSystem_Data/`, inside the folder you start the app from:

* **One folder per module** (created with **➕ New Module**), holding your saved notes (`.md`) and any images you paste or capture (`.png`).
* **`pdf_cache/`**: copies of the PDFs you upload in the Reading Room.
* **`revision_log.csv`**: one row per study session (module, note, date, duration in minutes, activity). This feeds the dashboard.
* **`user_stats.csv`**: your XP, daily streak and today's completed quests.

On first run the app creates `OptiSystem_Data/` if it's missing. The two CSV files are not created at startup: you begin with an empty dashboard and 0 XP, and they are written the first time you save a note or finish a blurt. `pdf_cache/` appears with your first PDF upload. Older files you may see in the folder (`master_tasks.csv`, `node_mastery.csv`, `.temp_session/`) come from earlier versions and aren't used by the current app.

The copy in this repo holds the author's own study data. To start fresh, delete the contents of `OptiSystem_Data/` (or the whole folder) before your first run.

> 💡 **Tip:** Create a module with **➕ New Module** before saving your first note. Until you do, the module list shows a placeholder called `General` that doesn't exist on disk yet. Saving into it fails and the app disconnects (reload the page to continue).

## 📝 Notes

* The editor, charts and math rendering load from a CDN, so OptiSystem needs an internet connection.
