# OptiSystem

OptiSystem is a lightweight, interactive personal productivity hub and study engine built with Python and Shiny. It is designed to help you manage project objectives, visualize complex concepts through dynamic mind maps, and systematically track your study metrics 

## 🚀 Features

* **📊 Analytics Dashboard:** Native web-rendered charts (powered by Chart.js) that visualize your daily and weekly study trends, average session lengths, and module time distribution.
* **🎯 Command Center & Progress Tracker:** Manage, edit, and track your daily objectives. Visual progress bars automatically calculate urgent and overdue deadlines.
* **🧠 Interactive Study Lab:** Write notes using an enhanced Markdown editor (EasyMDE) with full math support (KaTeX) and image pasting. Notes instantly render into an interactive, live-updating mind map.
* **🔄 Revision Hub:** Turn your mind maps into a sequential, node-by-node flashcard slideshow. A hidden session timer automatically logs your study duration for data tracking.

## 🛠️ Tech Stack

* **Backend:** Python, Shiny for Python (PyShiny), Pandas
* **Frontend:** HTML/CSS, JavaScript
* **Libraries:** Chart.js (Dashboards), EasyMDE (Text Editor), Markmap & D3.js (Mind Maps), KaTeX (Math Rendering)

## 💻 Installation & Setup (Beginner Friendly)

If you have never coded before or don't have GitHub set up, don't worry! Follow these steps to get OptiSystem running on your machine.

### Step 1: Get the Tools
1. **Download Python:** Go to [python.org](https://www.python.org/downloads/) and download the latest version for your computer. 
   * ⚠️ **CRITICAL (Windows Users):** When the installer opens, make sure to check the box at the very bottom that says **"Add Python.exe to PATH"** *before* you click Install.
2. **Download a Code Editor:** We recommend [Visual Studio Code (VS Code)](https://code.visualstudio.com/). It is a free, lightweight program that makes running the app very easy.

### Step 2: Get the OptiSystem Code
1. Scroll to the top of this GitHub page.
2. Click the green **"<> Code"** button.
3. Click **"Download ZIP"**.
4. Find the downloaded ZIP file on your computer, right-click it, and select **Extract All**. Move this extracted folder somewhere easy to find (like your Documents or Desktop).

### Step 3: Open the Project
1. Open Visual Studio Code.
2. Click **File > Open Folder...** at the top left, and select the `OptiSystem` folder you just extracted.
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

**4. Start the App!**
* Type: `shiny run app.py`

🎉 *OptiSystem will automatically open in your default web browser. Keep the VS Code window open and running in the background while you use the app. When you are done studying, click inside the terminal and press `Ctrl + C` to shut the server down.*
