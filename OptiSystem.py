import os
import pandas as pd
import base64
import time
import re
import random
from datetime import datetime
from shiny import App, render, ui, reactive

# --- CONFIGURATION ---
BASE_PATH = os.path.join(os.getcwd(), "OptiSystem_Data")
TASK_LOG = os.path.join(BASE_PATH, "master_tasks.csv")
REV_LOG = os.path.join(BASE_PATH, "revision_log.csv")
NODE_LOG = os.path.join(BASE_PATH, "node_mastery.csv") # New Tracking File

if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

# --- JAVASCRIPT & CSS ---
custom_js = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">

<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>

<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github.min.css">
<script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>

<script src="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/d3@6"></script>
<script src="https://cdn.jsdelivr.net/npm/markmap-view@0.14.4"></script>
<script src="https://cdn.jsdelivr.net/npm/markmap-lib@0.14.4/dist/browser/index.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
    .CodeMirror { max-height: 400px !important; }
    .CodeMirror-scroll { min-height: 200px !important; max-height: 400px !important; overflow-y: auto !important; overflow-x: hidden !important; }
    #mindmap { width: 100%; height: 650px; border: 1px solid #ddd; border-radius: 8px; cursor: grab; background-color: #fff; }
    #mindmap:active { cursor: grabbing; }
    svg { width: 100%; height: 100%; } 
    foreignObject { overflow: visible; }
    img { max-width: 350px; max-height: 350px; border: 2px solid #555; border-radius: 6px; display: block; }
    .katex-mathml { display: none !important; }
    #mindmap strong, #mindmap b { font-weight: 900 !important; font-style: normal !important; color: #000 !important; }
    #mindmap foreignObject div { white-space: nowrap !important; }
    
    .slide-content { width: 100%; max-width: 100%; overflow-x: auto; box-sizing: border-box; word-wrap: break-word; overflow-wrap: break-word; }
    .slide-content > * { max-width: 100%; }
    .slide-content img { margin: 0 auto; }
    .slide-container { transition: all 0.3s ease-in-out; max-width: 100%; overflow: hidden; box-sizing: border-box; }
    
    .kpi-card { text-align: center; padding: 20px 10px; border-radius: 8px; background: #f8f9fa; border: 1px solid #dee2e6; }
    .kpi-val { font-size: 2em; font-weight: bold; margin: 10px 0; }
    .kpi-val.retrieval { color: #198754; }
    .kpi-val.encoding { color: #0dcaf0; }
    .kpi-title { font-size: 1em; color: #6c757d; text-transform: uppercase; letter-spacing: 1px; }
    
    .streak-glow { box-shadow: 0 0 20px 5px rgba(255, 193, 7, 0.6) !important; border-color: #ffc107 !important; transition: all 0.3s ease; }
    .mcq-btn { text-align: left; padding: 15px; border-radius: 8px; font-size: 1.1em; transition: all 0.2s; white-space: normal; height: auto; }
    .mcq-btn:hover { transform: translateX(5px); }
    .flashcard-box { min-height: 300px; display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; }
    
    .blurt-review-panel { max-height: 600px; overflow-y: auto; overflow-x: auto; padding: 15px; background: #fff; border-radius: 5px; border: 1px solid #eee; word-wrap: break-word; overflow-wrap: break-word; }
    .blurt-review-panel > * { max-width: 100%; }
    
    .reading-source-pane { padding: 15px; border-right: 2px solid #e9ecef; font-size: 1.1em; background-color: #f8f9fa; border-radius: 5px 0 0 5px; }
    .reading-notes-pane { padding: 15px; background-color: #fff; border-radius: 0 5px 5px 0; }
    .aligned-row { border: 1px solid #dee2e6; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    .katex-display { overflow-x: auto; overflow-y: hidden; max-width: 100%; padding-bottom: 5px; }
    
    #loot-counter { font-weight: 800; color: #198754; background: #e8f5e9; padding: 8px 15px; border-radius: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.3s ease; display: inline-block; font-size: 1.1em; }
    .loot-pop { transform: scale(1.15); background: #d4edda; box-shadow: 0 0 15px rgba(25, 135, 84, 0.5); }
</style>

<script>
    function updateMindMap(markdown) {
        const { Transformer } = window.markmap;
        const transformer = new Transformer();
        const { root } = transformer.transform(markdown);
        document.getElementById('mindmap').innerHTML = ''; 
        const mapOptions = { spacingHorizontal: 140, spacingVertical: 15 };
        const mm = markmap.Markmap.create('#mindmap', mapOptions, root);
        mm.fit(); 
    }
    
    function attachSyncScroll() {
        const leftPane = document.querySelector('.sync-scroll-left');
        const rightPane = document.querySelector('.sync-scroll-right textarea');

        if (!leftPane || !rightPane) return;
        if (leftPane.dataset.syncAttached) return; 
        
        leftPane.dataset.syncAttached = 'true';

        let isSyncingLeft = false;
        let isSyncingRight = false;

        leftPane.addEventListener('scroll', function(e) {
            if (!isSyncingLeft) {
                isSyncingRight = true;
                let percentage = this.scrollTop / (this.scrollHeight - this.clientHeight);
                if (!isNaN(percentage)) {
                    rightPane.scrollTop = percentage * (rightPane.scrollHeight - rightPane.clientHeight);
                }
            }
            isSyncingLeft = false;
        });

        rightPane.addEventListener('scroll', function(e) {
            if (!isSyncingRight) {
                isSyncingLeft = true;
                let percentage = this.scrollTop / (this.scrollHeight - this.clientHeight);
                if (!isNaN(percentage)) {
                    leftPane.scrollTop = percentage * (leftPane.scrollHeight - leftPane.clientHeight);
                }
            }
            isSyncingRight = false;
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            const textArea = document.getElementById('map_content');
            if (textArea) {
                const easymde = new EasyMDE({ 
                    element: textArea, spellChecker: false, status: false,
                    renderingConfig: { codeSyntaxHighlighting: true },
                    toolbar: ["bold", "italic", "heading", "|", "quote", "code", "unordered-list", "ordered-list", "|", "link", "image", "|", "guide"]
                });
                window.easymde_editor = easymde; 
                let timeout = null;
                easymde.codemirror.on("change", function() {
                    clearTimeout(timeout);
                    timeout = setTimeout(function() {
                        const content = easymde.value();
                        Shiny.setInputValue('map_content', content); 
                        // Ask Python to inject colors before updating the map
                        Shiny.setInputValue('map_content_for_map', content, {priority: 'event'});
                    }, 300); 
                });

                easymde.codemirror.on("paste", function(editor, e) {
                    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
                    for (let index in items) {
                        const item = items[index];
                        if (item.kind === 'file') {
                            const blob = item.getAsFile();
                            const reader = new FileReader();
                            reader.onload = function(event) {
                                Shiny.setInputValue('pasted_image_data', event.target.result);
                                Shiny.setInputValue('pasted_image_trigger', Math.random());
                            };
                            reader.readAsDataURL(blob);
                            e.preventDefault(); 
                        }
                    }
                });

                const initial_content = easymde.value();
                Shiny.setInputValue('map_content_for_map', initial_content, {priority: 'event'});
            }
        }, 1000); 
        
        // --- READING ROOM LOOT COUNTER LOGIC ---
        document.addEventListener('input', function(e) {
            if (e.target && e.target.id === 'read_note_main') {
                const content = e.target.value;
                const counterEl = document.getElementById('loot-counter');
                if (counterEl) {
                    // Triggers the completionist reward loop by counting '?'
                    const count = (content.match(/[?]/g) || []).length;
                    const currentCount = parseInt(counterEl.getAttribute('data-count') || '0');
                    
                    if (count !== currentCount) {
                        counterEl.innerText = `Flashcards Captured: ${count} 💎`;
                        counterEl.setAttribute('data-count', count);
                        
                        if (count > currentCount) {
                            counterEl.classList.add('loot-pop');
                            setTimeout(() => counterEl.classList.remove('loot-pop'), 300);
                        }
                    }
                }
            }
        });
        
        const observer = new MutationObserver((mutations) => {
            attachSyncScroll();
        });
        observer.observe(document.body, { childList: true, subtree: true });
    });

    Shiny.addCustomMessageHandler('render_colored_map', function(colored_md) {
        updateMindMap(colored_md);
    });

    // --- NEW BLOB GENERATOR FOR LARGE PDFS ---
    let currentPdfUrl = null;
    Shiny.addCustomMessageHandler('load_pdf_blob', function(dataUri) {
        setTimeout(async function() {
            const iframe = document.getElementById('pdf-viewer-iframe');
            if (iframe) {
                try {
                    // Use native fetch to rapidly convert base64 payload to memory blob
                    const res = await fetch(dataUri);
                    const blob = await res.blob();
                    
                    // Clear old blob to prevent memory leaks
                    if (currentPdfUrl) {
                        URL.revokeObjectURL(currentPdfUrl);
                    }
                    
                    currentPdfUrl = URL.createObjectURL(blob);
                    iframe.src = currentPdfUrl;
                } catch (e) {
                    console.error("Failed to load PDF blob:", e);
                }
            }
        }, 300); // 300ms delay ensures the UI has fully generated the iframe DOM element
    });

    document.addEventListener('paste', function(e) {
        const target = e.target;
        if (target.tagName === 'TEXTAREA' && target.id === 'read_note_main') {
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let index in items) {
                const item = items[index];
                if (item.kind === 'file') {
                    const blob = item.getAsFile();
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        Shiny.setInputValue('pasted_read_image_data', event.target.result);
                        Shiny.setInputValue('pasted_read_image_target', target.id);
                        Shiny.setInputValue('pasted_read_image_trigger', Math.random());
                    };
                    reader.readAsDataURL(blob);
                    e.preventDefault(); 
                }
            }
        }
    });

    Shiny.addCustomMessageHandler('update_editor', function(markdown) {
        if (window.easymde_editor) { window.easymde_editor.value(markdown); }
        Shiny.setInputValue('map_content_for_map', markdown, {priority: 'event'});
    });

    Shiny.addCustomMessageHandler('insert_at_cursor', function(payload) {
        const el = document.getElementById(payload.target);
        if (el) {
            const start = el.selectionStart;
            const end = el.selectionEnd;
            const text = el.value;
            const before = text.substring(0, start);
            const after  = text.substring(end, text.length);
            el.value = before + payload.text + after;
            el.selectionStart = el.selectionEnd = start + payload.text.length;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    });

    Shiny.addCustomMessageHandler('render_katex', function(msg) {
        setTimeout(function() {
            if (window.renderMathInElement) {
                renderMathInElement(document.body, { delimiters: [
                    {left: '$$', right: '$$', display: true}, 
                    {left: '$', right: '$', display: false}
                ] });
            }
        }, 50); 
    });

    window.optiCharts = {};
    Shiny.addCustomMessageHandler('update_dashboard_charts', function(payload) {
        const d_ctx = document.getElementById('dailyChart');
        if(d_ctx) {
            if(window.optiCharts.daily) window.optiCharts.daily.destroy();
            window.optiCharts.daily = new Chart(d_ctx, {
                type: 'bar',
                data: {
                    labels: payload.d_labels,
                    datasets: [
                        { label: 'Retrieval (Blurt/Revise)', data: payload.d_retrieval, backgroundColor: '#198754' },
                        { label: 'Encoding (Notes)', data: payload.d_encoding, backgroundColor: '#0dcaf0' }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { x: { stacked: true }, y: { stacked: true, title: { display: true, text: 'Minutes' } } } }
            });
        }
        
        const w_ctx = document.getElementById('weeklyChart');
        if(w_ctx) {
            if(window.optiCharts.weekly) window.optiCharts.weekly.destroy();
            window.optiCharts.weekly = new Chart(w_ctx, {
                type: 'bar',
                data: {
                    labels: payload.w_labels,
                    datasets: [
                        { label: 'Retrieval (Blurt/Revise)', data: payload.w_retrieval, backgroundColor: '#198754' },
                        { label: 'Encoding (Notes)', data: payload.w_encoding, backgroundColor: '#0dcaf0' }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { x: { stacked: true }, y: { stacked: true, title: { display: true, text: 'Minutes' } } } }
            });
        }
    });
</script>
"""

# --- HELPERS ---
def load_tasks():
    if os.path.exists(TASK_LOG):
        try:
            df = pd.read_csv(TASK_LOG)
            expected_cols = ["ID", "Objective", "Module", "Deadline", "Progress"]
            for col in expected_cols:
                if col not in df.columns: df[col] = 0 if col == "Progress" else ""
            return df[expected_cols]
        except: return pd.DataFrame(columns=["ID", "Objective", "Module", "Deadline", "Progress"])
    return pd.DataFrame(columns=["ID", "Objective", "Module", "Deadline", "Progress"])

def load_revisions():
    if os.path.exists(REV_LOG):
        try: 
            df = pd.read_csv(REV_LOG)
            if "Activity" not in df.columns:
                df["Activity"] = "Revision"
            return df
        except: pass
    return pd.DataFrame(columns=["Module", "Map", "Date", "Duration (min)", "Activity"])

def load_node_mastery():
    if os.path.exists(NODE_LOG):
        try:
            df = pd.read_csv(NODE_LOG)
            for col in ["Module", "Map", "Node_Raw", "Attempts", "Correct"]:
                if col not in df.columns: df[col] = 0 if col in ["Attempts", "Correct"] else ""
            return df
        except: pass
    return pd.DataFrame(columns=["Module", "Map", "Node_Raw", "Attempts", "Correct"])

def normalize_text(t):
    """Bulletproof string normalizer to fix invisible Markdown/PDF characters"""
    if pd.isna(t): return ""
    text = str(t).lower()
    # Remove all non-alphanumeric chars except spaces to ensure matching is bulletproof
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Collapse multiple spaces into one and strip edges
    return re.sub(r'\s+', ' ', text).strip()

def update_node_mastery(module, map_name, node_raw, is_correct):
    if not map_name: return
    # STRICT NORMALIZATION: Always replace spaces with underscores for DB tracking
    map_name = map_name.strip().replace(" ", "_")
    if not map_name.endswith(".md"): map_name += ".md"
    
    df = load_node_mastery()
    norm_node = normalize_text(node_raw)
    
    # Create a normalized temporary column for safe matching
    df['norm_raw'] = df['Node_Raw'].apply(normalize_text)
    mask = (df["Module"] == module) & (df["Map"] == map_name) & (df['norm_raw'] == norm_node)
    
    if mask.any():
        idx = df.index[mask][0]
        df.at[idx, "Attempts"] += 1
        if is_correct: df.at[idx, "Correct"] += 1
    else:
        new_row = pd.DataFrame({
            "Module": [module], "Map": [map_name], "Node_Raw": [str(node_raw).strip()],
            "Attempts": [1], "Correct": [1 if is_correct else 0]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        
    # Drop temporary column before saving
    if 'norm_raw' in df.columns:
        df = df.drop(columns=['norm_raw'])
        
    df.to_csv(NODE_LOG, index=False)

def inject_mastery_colors(module, map_name, raw_md):
    if not map_name: return raw_md
    
    # STRICT NORMALIZATION: Ensure we always lookup the version with underscores
    map_name = map_name.strip().replace(" ", "_")
    if not map_name.endswith(".md"): map_name += ".md"
    
    df = load_node_mastery()
    mask = (df["Module"] == module) & (df["Map"] == map_name)
    map_df = df[mask]
    
    score_dict = {}
    for _, row in map_df.iterrows():
        score_dict[normalize_text(row["Node_Raw"])] = row["Correct"] / row["Attempts"] if row["Attempts"] > 0 else -1

    lines = raw_md.split("\n")
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("```") and not stripped.startswith("$$"):
            # Target ONLY headings to be colored on the mind map (allows leading spaces)
            header_match = re.match(r'^(\s*#{1,6}\s)(.*)', line)

            if header_match:
                prefix, content = header_match.groups()
                clean_content = content.strip() # BUG FIX: Strip invisible trailing \r that breaks HTML tags
                raw_text = normalize_text(clean_content)
                score = score_dict.get(raw_text, -1)

                if score == -1: color = "#adb5bd" # Untested / Structural Node (Gray)
                elif score < 0.60: color = "#dc3545" # Gap (Red)
                elif score < 0.80: color = "#fd7e14" # Review (Orange)
                else: color = "#198754" # Mastered (Green)

                line = f"{prefix}<span style='color:{color}'>{clean_content}</span>"
        new_lines.append(line)
    return "\n".join(new_lines)

def get_module_names():
    if not os.path.exists(BASE_PATH): return ["General"]
    mods = [d for d in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, d))]
    mods = [m for m in mods if m != ".temp_session"]
    return mods if mods else ["General"]

def get_saved_maps(module):
    mod_path = os.path.join(BASE_PATH, module)
    if not os.path.exists(mod_path): return []
    return [f for f in os.listdir(mod_path) if f.endswith('.md')]

def protect_math(raw_text):
    if not raw_text: return ""
    def repl(m):
        block = m.group(0)
        block = block.replace("\\\\", "\\\\\\\\")
        block = block.replace("\\{", "\\\\{").replace("\\}", "\\\\}")
        block = block.replace("_", "\\_").replace("*", "\\*")
        return block
    text = re.sub(r'\$\$.*?\$\$', repl, raw_text, flags=re.DOTALL)
    text = re.sub(r'(?<!\$)\$.*?\$(?!\$)', repl, text, flags=re.DOTALL)
    return text

# --- UI ---
app_ui = ui.page_navbar(
    ui.head_content(ui.HTML(custom_js)), 

    ui.nav_panel("Analytics Dashboard",
        ui.layout_columns(
            ui.div(ui.output_ui("kpi_encoding_ui"), class_="kpi-card"),
            ui.div(ui.output_ui("kpi_retrieval_ui"), class_="kpi-card"),
            ui.div(ui.output_ui("kpi_ratio_ui"), class_="kpi-card"),
            col_widths=(4, 4, 4)
        ),
        ui.br(),
        ui.layout_columns(
            ui.card(
                ui.card_header(ui.tags.b("Daily Phase Split")),
                ui.HTML('<div style="position: relative; height: 300px; width: 100%;"><canvas id="dailyChart"></canvas></div>')
            ),
            ui.card(
                ui.card_header(ui.tags.b("Weekly Phase Split")),
                ui.HTML('<div style="position: relative; height: 300px; width: 100%;"><canvas id="weeklyChart"></canvas></div>')
            ),
            col_widths=(6, 6)
        )
    ),

    ui.nav_panel("Command Center",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### **Objective Manager**"),
                ui.input_select("mode", "Mode", {"add": "Create New", "edit": "Edit/Update Existing"}),
                ui.output_ui("task_selector_ui"),
                ui.hr(),
                ui.input_text("task_name", "Objective Name"),
                ui.input_select("mod_select", "Module", get_module_names()),
                ui.input_date("due_date", "Target Date", value=datetime.now().date()),
                ui.input_slider("progress_val", "Completion Status (%)", 0, 100, 0),
                ui.output_ui("action_button_ui"),
                ui.hr(),
                ui.markdown("### **Maintenance**"),
                ui.input_action_button("purge_completed", "Clear Completed Tasks", class_="btn-danger btn-sm w-100"),
                ui.br(), ui.br(),
                ui.input_text("new_mod", "New Module"),
                ui.input_action_button("create_mod", "Create Folder", class_="btn-secondary btn-sm"),
            ),
            ui.card(ui.output_table("summary_table"))
        )
    ),

    ui.nav_panel("Progress Tracker",
        ui.card(ui.output_ui("progress_bars_list"))
    ),

    ui.nav_panel("Reading Room",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### **1. Import Material**"),
                ui.input_select("read_mod", "Select Module", get_module_names()),
                ui.input_file("upload_pdf", "Upload PDF Textbook", accept=[".pdf"], multiple=False),
                ui.input_text_area("read_source", "Or Paste Textbook/Source Text", height="150px", placeholder="Paste your text or LaTeX here..."),
                ui.input_action_button("process_read_btn", "Load Reading View 📖", class_="btn-primary w-100 mb-2"),
                ui.hr(),
                ui.markdown("### **2. Export to Study Lab**"),
                ui.input_text("read_save_name", "File Name", placeholder="e.g., Chapter_1_Notes"),
                ui.input_checkbox("include_source", "Include source text as context (Text mode only)?", True),
                ui.input_action_button("save_read_btn", "Save Notes 💾", class_="btn-success w-100")
            ),
            ui.card(
                ui.card_header(ui.tags.b("Reading & Annotation Environment")),
                ui.output_ui("aligned_reading_ui")
            )
        )
    ),

    ui.nav_panel("Study Lab",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### **Concept Architect**"),
                ui.input_select("map_mod", "Select Module", get_module_names()),
                ui.output_ui("map_loader_ui"),
                ui.input_action_button("load_btn", "Load Map", class_="btn-light w-100 mb-2"),
                ui.hr(),
                ui.input_text("save_name", "File Name", placeholder="e.g., SAS_Unit_1"),
                ui.input_action_button("save_btn", "Save Map", class_="btn-primary w-100 mb-2"),
                ui.hr(),
                ui.output_ui("target_gaps_ui"),
                ui.hr(),
                ui.markdown("### **Session Timer**"),
                ui.input_action_button("start_sl_btn", "Start Note-taking", class_="btn-info w-100 mb-2"),
                ui.input_action_button("end_sl_btn", "End Session & Log", class_="btn-danger w-100"),
                ui.hr(),
                ui.input_text_area("map_content", None, height="200px", 
                    value="# Central Concept\n## Branch 1\n- Detail A\n\n- Example Math: $y_i$"),
            ),
            ui.card(
                ui.card_header(ui.HTML('Interactive Map <span style="float:right; font-size:0.8em; color:gray;">Legend: <span style="color:#198754">🟢 Mastered</span> | <span style="color:#fd7e14">🟠 Review</span> | <span style="color:#dc3545">🔴 Knowledge Gap</span> | ⚪ Untested / Structural</span>')),
                ui.HTML('<svg id="mindmap"></svg>')
            )
        )
    ),

    ui.nav_panel("Revision Hub",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### **Session Setup**"),
                ui.input_select("rev_mod_select", "Select Module", get_module_names()),
                ui.output_ui("rev_map_loader_ui"),
                ui.input_action_button("start_rev_btn", "Start Revision 🚀", class_="btn-success w-100"),
                ui.hr(),
                ui.markdown("### **Quick Stats**"),
                ui.output_ui("rev_quick_stats_ui")
            ),
            ui.card(ui.card_header("Slide Viewer"), ui.output_ui("revision_display_ui")),
            ui.card(ui.card_header("Recent Sessions"), ui.output_table("revision_history_table"))
        )
    ),
    
    ui.nav_panel("Blurt Studio",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### **Active Recall**"),
                ui.input_select("blurt_mod_select", "Select Module", get_module_names()),
                ui.output_ui("blurt_map_loader_ui"),
                ui.input_action_button("start_blurt_btn", "Generate Template & Start Timer", class_="btn-primary w-100"),
                ui.hr(),
                ui.input_action_button("review_blurt_btn", "Submit, Review & Log Time", class_="btn-success w-100"),
                ui.input_action_button("reset_blurt_btn", "Reset Session", class_="btn-danger w-100 mt-2")
            ),
            ui.card(ui.output_ui("blurt_main_area_ui"))
        )
    ),
    
    title="OptiSystem v6.40",
)

# --- SERVER ---
def server(input, output, session):
    refresh_trigger = reactive.Value(0)
    
    read_state = reactive.Value({"mode": None, "data": None})
    sl_active = reactive.Value(False)
    sl_start_time = reactive.Value(0.0)

    # Revision Hub Session States (Locked to prevent UI jump bugs)
    rev_phase = reactive.Value("setup") 
    rev_slides = reactive.Value([])
    rev_current_idx = reactive.Value(0)
    rev_start_time = reactive.Value(0.0)
    rev_mcq_options = reactive.Value([])
    rev_streak = reactive.Value(0)
    rev_show_ans = reactive.Value(False)
    rev_active_mod = reactive.Value("") 
    rev_active_map = reactive.Value("") 
    
    # Blurt Studio Session States
    blurt_state = reactive.Value("setup") 
    blurt_original = reactive.Value("")
    blurt_template = reactive.Value("")
    blurt_start_time = reactive.Value(0.0)
    blurt_active_mod = reactive.Value("")
    blurt_active_map = reactive.Value("")

    # ==========================
    # DASHBOARD LOGIC 
    # ==========================
    def get_processed_rev_df():
        df = load_revisions()
        if not df.empty:
            df['Date_Obj'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Date_Only'] = df['Date_Obj'].dt.date
            df['YearWeek'] = df['Date_Obj'].dt.isocalendar().year.astype(str) + "-W" + df['Date_Obj'].dt.isocalendar().week.astype(str).str.zfill(2)
        return df

    @output
    @render.ui
    def kpi_encoding_ui():
        refresh_trigger()
        df = get_processed_rev_df()
        val = 0.0
        if not df.empty:
            today = datetime.now().date()
            val = df[(df['Date_Only'] == today) & (df['Activity'] == "Study Lab")]['Duration (min)'].sum()
        return ui.HTML(f"<div class='kpi-title'>Encoding Today (Notes)</div><div class='kpi-val encoding'>{val:.1f} <span style='font-size:0.5em'>min</span></div>")

    @output
    @render.ui
    def kpi_retrieval_ui():
        refresh_trigger()
        df = get_processed_rev_df()
        val = 0.0
        if not df.empty:
            today = datetime.now().date()
            val = df[(df['Date_Only'] == today) & (df['Activity'].isin(["Revision", "Blurt"]))] ['Duration (min)'].sum()
        return ui.HTML(f"<div class='kpi-title'>Retrieval Today (Recall)</div><div class='kpi-val retrieval'>{val:.1f} <span style='font-size:0.5em'>min</span></div>")

    @output
    @render.ui
    def kpi_ratio_ui():
        refresh_trigger()
        df = get_processed_rev_df()
        if df.empty: return ui.HTML(f"<div class='kpi-title'>Weekly Recall Ratio</div><div class='kpi-val'>0%</div>")
        
        current_yw = f"{datetime.now().isocalendar()[0]}-W{str(datetime.now().isocalendar()[1]).zfill(2)}"
        week_df = df[df['YearWeek'] == current_yw]
        enc = week_df[week_df['Activity'] == "Study Lab"]['Duration (min)'].sum()
        ret = week_df[week_df['Activity'].isin(["Revision", "Blurt"])]['Duration (min)'].sum()
        
        total = enc + ret
        ratio = (ret / total * 100) if total > 0 else 0
        color = "#198754" if ratio >= 80 else "#fd7e14" if ratio >= 50 else "#dc3545"
        
        return ui.HTML(f"<div class='kpi-title'>Weekly Recall Ratio (Goal: 80%)</div><div class='kpi-val' style='color:{color}'>{ratio:.1f}%</div>")

    @reactive.Effect
    async def update_line_charts():
        refresh_trigger()
        df = get_processed_rev_df()
        if df.empty: return
        
        daily = df.groupby(['Date_Only', 'Activity'])['Duration (min)'].sum().unstack(fill_value=0)
        for col in ['Study Lab', 'Revision', 'Blurt']:
            if col not in daily: daily[col] = 0
        daily_retrieval = daily['Revision'] + daily['Blurt']
        
        weekly = df.groupby(['YearWeek', 'Activity'])['Duration (min)'].sum().unstack(fill_value=0)
        for col in ['Study Lab', 'Revision', 'Blurt']:
            if col not in weekly: weekly[col] = 0
        weekly_retrieval = weekly['Revision'] + weekly['Blurt']
        
        payload = {
            "d_labels": [d.strftime("%b %d") for d in daily.index],
            "d_encoding": daily['Study Lab'].tolist(),
            "d_retrieval": daily_retrieval.tolist(),
            "w_labels": list(weekly.index),
            "w_encoding": weekly['Study Lab'].tolist(),
            "w_retrieval": weekly_retrieval.tolist()
        }
        await session.send_custom_message("update_dashboard_charts", payload)

    # ==========================
    # COMMAND CENTER & TASKS 
    # ==========================
    @reactive.Effect
    @reactive.event(input.purge_completed)
    def _purge_tasks():
        df = load_tasks()
        if df.empty: return
        df = df[df["Progress"] < 100].reset_index(drop=True)
        df['ID'] = df.index
        df.to_csv(TASK_LOG, index=False)
        refresh_trigger.set(refresh_trigger() + 1)

    @output
    @render.ui
    def task_selector_ui():
        if input.mode() == "edit": return ui.input_select("task_to_edit", "Select Task", {str(i): row['Objective'] for i, row in load_tasks().iterrows()})

    @output
    @render.ui
    def action_button_ui():
        if input.mode() == "edit": return ui.div(ui.input_action_button("save_edit", "Update", class_="btn-warning w-100 mb-2"), ui.input_action_button("delete_task", "Delete", class_="btn-danger w-100"))
        return ui.input_action_button("add_task", "Sync", class_="btn-primary w-100")

    @reactive.Effect
    @reactive.event(input.task_to_edit)
    def _populate_fields():
        if input.mode() == "edit":
            try:
                row = load_tasks().iloc[int(input.task_to_edit())]
                ui.update_text("task_name", value=row['Objective'])
                ui.update_select("mod_select", selected=row['Module'])
                ui.update_slider("progress_val", value=int(row['Progress']))
            except: pass

    @reactive.Effect
    @reactive.event(input.add_task)
    def _add():
        df = load_tasks()
        pd.concat([df, pd.DataFrame({"ID": [len(df)], "Objective": [input.task_name()], "Module": [input.mod_select()], "Deadline": [str(input.due_date())], "Progress": [input.progress_val()]})], ignore_index=True).to_csv(TASK_LOG, index=False)
        refresh_trigger.set(refresh_trigger() + 1)

    @reactive.Effect
    @reactive.event(input.save_edit)
    def _edit():
        df = load_tasks()
        df.loc[int(input.task_to_edit()), ["Objective", "Module", "Deadline", "Progress"]] = [input.task_name(), input.mod_select(), str(input.due_date()), input.progress_val()]
        df.to_csv(TASK_LOG, index=False)
        refresh_trigger.set(refresh_trigger() + 1)

    @reactive.Effect
    @reactive.event(input.delete_task)
    def _delete():
        df = load_tasks().drop(int(input.task_to_edit())).reset_index(drop=True)
        df['ID'] = df.index
        df.to_csv(TASK_LOG, index=False)
        refresh_trigger.set(refresh_trigger() + 1)

    @reactive.Effect
    @reactive.event(input.create_mod)
    def _create_folder():
        name = input.new_mod().strip().replace(" ", "_")
        if name:
            os.makedirs(os.path.join(BASE_PATH, name), exist_ok=True)
            refresh_trigger.set(refresh_trigger() + 1)
            mods = get_module_names()
            for select_id in ["mod_select", "read_mod", "map_mod", "rev_mod_select", "blurt_mod_select"]: 
                ui.update_select(select_id, choices=mods)

    @output
    @render.ui
    def progress_bars_list():
        refresh_trigger()
        df = load_tasks()
        if df.empty: return ui.markdown("No active objectives.")
        df['Deadline_dt'] = pd.to_datetime(df['Deadline'], errors='coerce').fillna(pd.Timestamp("2099-12-31"))
        df = df.sort_values(by='Deadline_dt').reset_index(drop=True)
        ui_list = []
        for _, row in df.iterrows():
            days_left = (row['Deadline_dt'] - datetime.now()).days + 1
            bar_color = "bg-success" if row['Progress'] == 100 else "bg-dark" if days_left < 0 else "bg-danger" if days_left <= 3 else "bg-info"
            status_text = "DONE" if row['Progress'] == 100 else f"OVERDUE ({abs(days_left)}d)" if days_left < 0 else f"{days_left}d left"
            ui_list.append(ui.div(
                ui.div(ui.tags.b(row['Objective']), ui.span(f" ({row['Module']})", style="color: gray;"), ui.span(status_text, style="float:right; font-weight: bold;")),
                ui.div(ui.div(f"{row['Progress']}%", class_=f"progress-bar {bar_color}", style=f"width:{row['Progress']}%"), class_="progress", style="height:22px; margin-bottom:18px")
            ))
        return ui.div(*ui_list)

    @output
    @render.table
    def summary_table():
        refresh_trigger()
        return load_tasks()

    # ==========================
    # READING ROOM LOGIC
    # ==========================
    @reactive.Effect
    @reactive.event(input.process_read_btn)
    def _process_reading():
        pdf_info = input.upload_pdf()
        text_source = input.read_source()

        if pdf_info:
            try:
                pdf_path = pdf_info[0]["datapath"]
                
                with open(pdf_path, "rb") as f:
                    pdf_b64 = base64.b64encode(f.read()).decode('utf-8')
                
                data_uri = f"data:application/pdf;base64,{pdf_b64}"
                
                read_state.set({
                    "mode": "pdf", 
                    "data": data_uri
                })
                ui.notification_show("PDF loaded via memory Blob! No files saved locally.", type="message")
            except Exception as e:
                ui.notification_show(f"Failed to load PDF: {str(e)}", type="error")
                
        elif text_source and text_source.strip():
            read_state.set({"mode": "text", "data": text_source})
            ui.notification_show("Loaded text for aligned reading.", type="message")
            
        else:
            ui.notification_show("Please upload a PDF or paste text/LaTeX first.", type="warning")

    @output
    @render.ui
    async def aligned_reading_ui():
        state = read_state()
        if not state["mode"]:
            return ui.div(ui.h4("Paste your source material or upload a PDF, then click 'Load Reading View'", class_="text-muted text-center mt-4"))
        
        await session.send_custom_message("render_katex", None)
        
        if state["mode"] == "pdf":
            await session.send_custom_message("load_pdf_blob", state["data"])
            
            return ui.div(
                ui.layout_columns(
                    ui.div(
                        ui.tags.iframe(id="pdf-viewer-iframe", src="", width="100%", height="800px", style="border: none; border-radius: 5px;"),
                        class_="reading-source-pane", style="padding: 0; overflow: hidden;"
                    ),
                    ui.div(
                        ui.div(ui.span("Flashcards Captured: 0 💎", id="loot-counter", **{"data-count": "0"}), style="margin-bottom: 10px; display: flex; justify-content: flex-end;"),
                        ui.input_text_area(
                            "read_note_main", 
                            label=None, 
                            placeholder="Draft your notes here while reading the PDF on the left...\n\nUse empty lines (Enter) to push your notes down so they physically align with the pages of the PDF on the left!\n\nTip: You can paste images directly here!", 
                            width="100%", 
                            height="760px"
                        ),
                        class_="reading-notes-pane sync-scroll-right"
                    ),
                    col_widths=(6, 6)
                ),
                class_="aligned-row"
            )
            
        else:
            safe_source = protect_math(state["data"])
            return ui.div(
                ui.layout_columns(
                    ui.div(
                        ui.markdown(safe_source), 
                        class_="reading-source-pane sync-scroll-left", 
                        style="height: 800px; overflow-y: auto;"
                    ),
                    ui.div(
                        ui.div(ui.span("Flashcards Captured: 0 💎", id="loot-counter", **{"data-count": "0"}), style="margin-bottom: 10px; display: flex; justify-content: flex-end;"),
                        ui.input_text_area(
                            "read_note_main", 
                            label=None, 
                            placeholder="Draft your notes here...\n\nUse empty lines (Enter) to push your notes down so they physically map and align with the text on the left!\n\nTip: You can paste images directly here!", 
                            width="100%", 
                            height="760px"
                        ),
                        class_="reading-notes-pane sync-scroll-right"
                    ),
                    col_widths=(6, 6)
                ),
                class_="aligned-row"
            )

    @reactive.Effect
    @reactive.event(input.pasted_read_image_trigger)
    async def _handle_read_paste():
        data_url = input.pasted_read_image_data()
        target_id = input.pasted_read_image_target()
        
        if not data_url or not target_id: return
        
        header, encoded = data_url.split(",", 1)
        filename = f"img_{int(time.time() * 1000)}.png"
        mod_dir = os.path.join(BASE_PATH, input.read_mod())
        os.makedirs(mod_dir, exist_ok=True)
        
        with open(os.path.join(mod_dir, filename), "wb") as f: 
            f.write(base64.b64decode(encoded))
            
        img_md = f"\n![{filename}](/files/{input.read_mod()}/{filename})\n"
        await session.send_custom_message("insert_at_cursor", {"target": target_id, "text": img_md})

    @reactive.Effect
    @reactive.event(input.save_read_btn)
    def _save_reading():
        if not input.read_save_name():
            ui.notification_show("Please provide a file name to save your notes.", type="error")
            return
            
        state = read_state()
        if not state["mode"]:
            return
            
        final_content = []
        
        try:
            note_val = input.read_note_main()
            if note_val and note_val.strip():
                if state["mode"] == "text" and input.include_source():
                    quoted_source = "\n".join([f"> {line}" for line in state["data"].split("\n")])
                    final_content.append(f"{quoted_source}\n\n---\n\n{note_val}\n")
                else:
                    final_content.append(f"{note_val}\n")
        except Exception:
            pass
                    
        if not final_content:
            ui.notification_show("No notes written. Nothing to save!", type="warning")
            return
            
        filename = input.read_save_name().strip().replace(" ", "_")
        if not filename.endswith(".md"):
            filename += ".md"
            
        with open(os.path.join(BASE_PATH, input.read_mod(), filename), "w") as f:
            f.write("".join(final_content))
            
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show(f"Successfully exported {filename} to {input.read_mod()}! Go to Study Lab to view it.", type="message")

    # ==========================
    # STUDY LAB LOGIC
    # ==========================
    @reactive.Effect
    @reactive.event(input.start_sl_btn)
    def _start_sl():
        sl_start_time.set(time.time())
        sl_active.set(True)
        ui.notification_show("Note-taking session started.", type="message")

    @reactive.Effect
    @reactive.event(input.end_sl_btn)
    def _end_sl():
        if not sl_active(): return
        duration = round((time.time() - sl_start_time()) / 60, 2)
        df = load_revisions()
        new_row = pd.DataFrame({"Module": [input.map_mod()], "Map": [input.save_name() if input.save_name() else "Drafting"], "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], "Duration (min)": [duration], "Activity": ["Study Lab"]})
        pd.concat([df, new_row], ignore_index=True).to_csv(REV_LOG, index=False)
        sl_active.set(False)
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show(f"Logged {duration} minutes.", type="message")

    @reactive.Effect
    @reactive.event(input.save_btn)
    def _save_map():
        if not input.save_name(): return
        filename = input.save_name().strip().replace(" ", "_") + (".md" if not input.save_name().endswith(".md") else "")
        with open(os.path.join(BASE_PATH, input.map_mod(), filename), "w") as f: f.write(input.map_content())
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show(f"Saved: {filename}", type="message")

    @output
    @render.ui
    def map_loader_ui():
        refresh_trigger() 
        maps = get_saved_maps(input.map_mod())
        sel = None
        if maps:
            with reactive.isolate():
                try:
                    current = input.selected_map()
                    if current in maps: sel = current
                except Exception: pass
            if not sel: sel = maps[0]
            return ui.input_select("selected_map", "Load Saved Map", choices=maps, selected=sel)
        return ui.markdown("_No saved maps_")

    @reactive.Effect
    @reactive.event(input.load_btn)
    async def _load_map():
        try:
            with open(os.path.join(BASE_PATH, input.map_mod(), input.selected_map()), "r") as f: content = f.read()
            ui.update_text("save_name", value=input.selected_map().replace(".md", ""))
            await session.send_custom_message("update_editor", content) 
        except Exception as e: ui.notification_show(f"Error: {str(e)}", type="error")

    @reactive.Effect
    @reactive.event(input.map_content_for_map)
    async def _update_map_visual():
        raw_md = input.map_content_for_map()
        map_name = input.save_name() if input.save_name() else input.selected_map()
        if map_name:
            map_name = map_name.strip().replace(" ", "_")
            if not map_name.endswith(".md"): map_name += ".md"
        colored_md = inject_mastery_colors(input.map_mod(), map_name, raw_md)
        await session.send_custom_message("render_colored_map", colored_md)

    @output
    @render.ui
    def target_gaps_ui():
        refresh_trigger()
        map_name = input.save_name() if input.save_name() else input.selected_map()
        if not map_name: return ui.div()
        map_name = map_name.strip().replace(" ", "_")
        if not map_name.endswith(".md"): map_name += ".md"

        df = load_node_mastery()
        mask = (df["Module"] == input.map_mod()) & (df["Map"] == map_name) & (df["Attempts"] > 0)
        map_df = df[mask].copy()

        if map_df.empty: return ui.div(ui.p("Start revising to reveal knowledge gaps!", class_="text-muted text-center", style="font-size: 0.85em;"))

        map_df["Score"] = map_df["Correct"] / map_df["Attempts"]
        # Sort by worst score first, breaking ties by most attempts (highest friction)
        gaps = map_df.sort_values(by=["Score", "Attempts"], ascending=[True, False]).head(3)

        items = []
        for _, row in gaps.iterrows():
            score_pct = int(row["Score"] * 100)
            color = "danger" if score_pct < 60 else "warning" if score_pct < 80 else "success"
            display_text = row["Node_Raw"][:40] + "..." if len(row["Node_Raw"]) > 40 else row["Node_Raw"]
            
            items.append(
                ui.div(
                    ui.span(f"{score_pct}%", class_=f"badge bg-{color} me-2"),
                    ui.span(display_text, style="font-size: 0.9em; font-weight: 500;"),
                    class_="d-flex align-items-center mb-2 p-2 border rounded shadow-sm bg-white"
                )
            )

        if not items: return ui.div()
        return ui.div(
            ui.markdown("#### **🎯 Target Gaps**"),
            ui.p("Nodes requiring active recall:", style="font-size: 0.85em; color: gray;"),
            ui.div(*items)
        )

    @reactive.Effect
    @reactive.event(input.pasted_image_trigger)
    async def _handle_paste():
        data_url = input.pasted_image_data()
        if not data_url: return
        header, encoded = data_url.split(",", 1)
        filename = f"img_{int(time.time())}.png"
        mod_dir = os.path.join(BASE_PATH, input.map_mod())
        os.makedirs(mod_dir, exist_ok=True)
        with open(os.path.join(mod_dir, filename), "wb") as f: f.write(base64.b64decode(encoded))
        full_content = input.map_content() + f"\n- ![{filename}](/files/{input.map_mod()}/{filename})"
        await session.send_custom_message("update_editor", full_content) 

    # ==========================
    # REVISION HUB LOGIC 
    # ==========================
    def generate_mcq_opts(idx, slides):
        if not slides: return []
        correct = slides[idx]["raw"]
        # Extract distractors from other flashcards in the same deck
        distractors = list(set([s["raw"] for i, s in enumerate(slides) if i != idx and s["raw"] != correct]))
        random.shuffle(distractors)
        opts = [correct] + distractors[:3]
        
        # Pad with placeholders if the deck is too small to have 3 distinct distractors
        while len(opts) < 4: 
            opts.append(f"Conceptual Distractor (Deck too small)")
            
        random.shuffle(opts)
        return opts

    @output
    @render.ui
    def rev_map_loader_ui():
        refresh_trigger()
        maps = get_saved_maps(input.rev_mod_select())
        sel = None
        if maps:
            with reactive.isolate():
                try:
                    current = input.rev_selected_map()
                    if current in maps: sel = current
                except Exception: pass
            if not sel: sel = maps[0]
            return ui.input_select("rev_selected_map", "Select Map to Revise", choices=maps, selected=sel)
        return ui.markdown("_No saved maps_")

    @reactive.Effect
    @reactive.event(input.start_rev_btn)
    def _start_revision():
        if not input.rev_selected_map(): return
        
        # --- LOCK THE SESSION STATE ---
        mod_locked = input.rev_mod_select()
        map_locked = input.rev_selected_map()
        rev_active_mod.set(mod_locked)
        rev_active_map.set(map_locked)
        # ------------------------------
        
        path = os.path.join(BASE_PATH, mod_locked, map_locked)
        if not os.path.exists(path): return
        
        with open(path, "r") as f: lines = f.readlines()
        
        slides = []
        current_heading = "General Concept"
        current_answer = []
        in_math, in_code = False, False
        
        def save_card():
            ans_text = "\n".join(current_answer).strip()
            if ans_text:
                slides.append({"breadcrumb": current_heading, "raw": ans_text})
            current_answer.clear()

        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith("`" * 3): in_code = not in_code
            if stripped.count("$$") % 2 != 0: in_math = not in_math
            
            if not in_math and not in_code:
                # If we hit a new heading, save the previous card and grab the new question
                if re.match(r'^\s*#{1,6}\s', line):
                    save_card()
                    current_heading = line.lstrip(' #').strip()
                elif stripped: # Group all bullets/text into the answer
                    current_answer.append(line.rstrip('\n'))
            else:
                if stripped or current_answer:
                    current_answer.append(line.rstrip('\n'))
            
        save_card() 
        
        if not slides:
            slides = [{"breadcrumb": "Empty", "raw": "No content found."}]
            
        rev_slides.set(slides)
        rev_current_idx.set(0)
        rev_streak.set(0)
        rev_mcq_options.set(generate_mcq_opts(0, slides))
        rev_start_time.set(time.time())
        rev_phase.set("easy") # Start in the low-friction warm-up phase

    @reactive.Effect
    @reactive.event(input.mcq_answer)
    def _handle_mcq():
        try:
            ans = base64.b64decode(input.mcq_answer()).decode()
        except:
            ans = input.mcq_answer()
            
        slides, idx = rev_slides(), rev_current_idx()
        correct = slides[idx]["raw"]
        
        is_correct = (ans == correct)
        
        # Dopamine Hook: Streaks
        if is_correct:
            rev_streak.set(rev_streak() + 1)
            ui.notification_show("Correct! +1 Streak 🔥" if rev_streak() >=3 else "Correct!", type="message", duration=2)
        else:
            rev_streak.set(0)
            ui.notification_show("Incorrect, but keep going!", type="warning", duration=2)
            
        # Auto-advance
        if idx < len(slides) - 1:
            rev_current_idx.set(idx + 1)
            rev_mcq_options.set(generate_mcq_opts(idx + 1, slides))
        else:
            rev_phase.set("transition")

    @reactive.Effect
    @reactive.event(input.start_hard_mode_btn)
    def _start_hard_mode():
        rev_current_idx.set(0)
        rev_show_ans.set(False)
        rev_phase.set("hard")

    @reactive.Effect
    @reactive.event(input.reveal_ans_btn)
    def _reveal_ans():
        rev_show_ans.set(True)

    @reactive.Effect
    @reactive.event(input.hard_answer)
    def _handle_hard():
        direction = input.hard_answer() # left or right
        slides, idx = rev_slides(), rev_current_idx()
        
        # --- MASTERY TRACKING ---
        node_question = slides[idx]["breadcrumb"]
        is_correct = (direction == 'right')
        
        # Track directly to the locked session state to prevent UI jump bugs!
        update_node_mastery(rev_active_mod(), rev_active_map(), node_question, is_correct)
        refresh_trigger.set(refresh_trigger() + 1)
        # ------------------------
        
        if idx < len(slides) - 1:
            rev_current_idx.set(idx + 1)
            rev_show_ans.set(False)
        else:
            # Complete Revision Session
            duration = round((time.time() - rev_start_time()) / 60, 2)
            df = load_revisions()
            new_row = pd.DataFrame({
                "Module": [rev_active_mod()], 
                "Map": [rev_active_map()], 
                "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], 
                "Duration (min)": [duration], 
                "Activity": ["Revision"]
            })
            pd.concat([df, new_row], ignore_index=True).to_csv(REV_LOG, index=False)
            rev_phase.set("setup")
            refresh_trigger.set(refresh_trigger() + 1)
            ui.notification_show(f"Session Complete! Logged {duration} mins.", type="message")

    @output
    @render.ui
    async def revision_display_ui():
        phase = rev_phase()
        
        if phase == "setup": 
            return ui.div(ui.h4("Ready to Review?", class_="text-center mt-4 text-muted"), style="min-height: 250px; display: flex; flex-direction: column; justify-content: center;")
            
        slides, idx, streak = rev_slides(), rev_current_idx(), rev_streak()
        await session.send_custom_message("render_katex", None)
        
        if phase == "easy":
            card_class = "card p-4 shadow-sm slide-container"
            if streak >= 3: card_class += " streak-glow" 
            
            opts = rev_mcq_options()
            btn_html = "".join([f'<button class="btn btn-outline-secondary w-100 mb-3 mcq-btn" onclick="Shiny.setInputValue(\'mcq_answer\', \'{base64.b64encode(o.encode()).decode()}\', {{priority: \'event\'}})">{ui.markdown(protect_math(o))}</button>' for o in opts])
            
            streak_badge = f'<span class="badge bg-warning text-dark" style="font-size: 1.1em; float:right;">🔥 Streak: {streak}</span>' if streak > 0 else ""
            
            return ui.div(
                ui.HTML(streak_badge),
                ui.p("WARM-UP: IDENTIFY THE CONCEPT", class_="text-muted", style="font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px;"),
                ui.h4(slides[idx]["breadcrumb"], class_="text-primary mb-4", style="font-weight: bold;"),
                ui.HTML(btn_html),
                ui.hr(),
                ui.div(ui.span(f" Progress: {idx + 1} / {len(slides)} ", style="font-weight: bold; text-align: center; display: block;")),
                class_=card_class
            )
            
        elif phase == "transition":
            return ui.div(
                ui.h2("🎉 Warm-up Complete!"),
                ui.p("Your brain is primed. You've easily identified the concepts.", class_="text-muted mb-4"),
                ui.div(
                    ui.h5("Now for the real challenge: Active Recall."),
                    ui.p("In this phase, you must retrieve the answer entirely from memory *before* revealing it."),
                    class_="p-3 mb-4", style="background: #f8f9fa; border-radius: 8px; border-left: 4px solid #dc3545;"
                ),
                ui.input_action_button("start_hard_mode_btn", "Enter Flashcard Mode 🔥", class_="btn-danger btn-lg w-100"),
                class_="card p-4 shadow-sm text-center slide-container", style="min-height: 300px; display: flex; flex-direction: column; justify-content: center;"
            )
            
        elif phase == "hard":
            display_raw = protect_math(slides[idx]["raw"])
            
            if not rev_show_ans():
                return ui.div(
                    ui.p("ACTIVE RECALL", class_="text-muted", style="font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px;"),
                    ui.hr(),
                    ui.div(ui.h3(slides[idx]["breadcrumb"], class_="text-center"), class_="flashcard-box"),
                    ui.hr(),
                    ui.input_action_button("reveal_ans_btn", "Reveal Answer 👁️", class_="btn-primary w-100 btn-lg"),
                    ui.p(f" Card {idx + 1} of {len(slides)} ", class_="text-center mt-3 text-muted"),
                    class_="card p-4 shadow-sm slide-container"
                )
            else:
                return ui.div(
                    ui.p(slides[idx]["breadcrumb"], class_="text-muted", style="font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px;"),
                    ui.hr(style="margin-top: 5px;"),
                    ui.div(ui.markdown(display_raw), class_="slide-content flashcard-box", style="font-size: 1.6em; text-align: center;"),
                    ui.hr(),
                    ui.layout_columns(
                        ui.HTML('<button class="btn btn-outline-danger btn-lg w-100" onclick="Shiny.setInputValue(\'hard_answer\', \'left\', {priority: \'event\'})">⬅️ Needs Review</button>'),
                        ui.HTML('<button class="btn btn-outline-success btn-lg w-100" onclick="Shiny.setInputValue(\'hard_answer\', \'right\', {priority: \'event\'})">Got it ➡️</button>'),
                        col_widths=(6, 6)
                    ),
                    class_="card p-4 shadow-sm slide-container"
                )

    @output
    @render.table
    def revision_history_table():
        refresh_trigger()
        df = load_revisions()
        return df.sort_index(ascending=False).head(10) if not df.empty else pd.DataFrame(columns=["Module", "Map", "Date", "Duration (min)", "Activity"])

    @output
    @render.ui
    def rev_quick_stats_ui():
        refresh_trigger()
        df = load_revisions()
        if df.empty: return ui.markdown("_No stats yet._")
        return ui.div(ui.p(ui.tags.b("Total Time Studied: "), f"{round(df['Duration (min)'].sum(), 1)} mins"))

    # ==========================
    # BLURT STUDIO LOGIC 
    # ==========================
    @output
    @render.ui
    def blurt_map_loader_ui():
        refresh_trigger()
        maps = get_saved_maps(input.blurt_mod_select())
        sel = None
        if maps:
            with reactive.isolate():
                try:
                    current = input.blurt_selected_map()
                    if current in maps: sel = current
                except Exception: pass
            if not sel: sel = maps[0]
            return ui.input_select("blurt_selected_map", "Select Map to Blurt", choices=maps, selected=sel)
        return ui.markdown("_No saved maps_")

    @reactive.Effect
    @reactive.event(input.start_blurt_btn)
    def _start_blurt():
        if not input.blurt_selected_map(): return
        
        # --- LOCK THE SESSION STATE ---
        blurt_active_mod.set(input.blurt_mod_select())
        blurt_active_map.set(input.blurt_selected_map())
        # ------------------------------
        
        path = os.path.join(BASE_PATH, input.blurt_mod_select(), input.blurt_selected_map())
        with open(path, "r") as f: content = f.read()
        blurt_original.set(content)
        template = "".join([f"{line}\n\n\n" for line in content.split('\n') if line.strip().startswith('#')])
        blurt_template.set(template)
        blurt_state.set("blurting")
        blurt_start_time.set(time.time())

    @reactive.Effect
    @reactive.event(input.review_blurt_btn)
    def _review_blurt():
        if blurt_state() == "blurting":
            blurt_state.set("review")
            duration = round((time.time() - blurt_start_time()) / 60, 2)
            df = load_revisions()
            new_row = pd.DataFrame({
                "Module": [blurt_active_mod()], 
                "Map": [blurt_active_map()], 
                "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], 
                "Duration (min)": [duration], 
                "Activity": ["Blurt"]
            })
            pd.concat([df, new_row], ignore_index=True).to_csv(REV_LOG, index=False)
            refresh_trigger.set(refresh_trigger() + 1)

    @reactive.Effect
    @reactive.event(input.reset_blurt_btn)
    def _reset_blurt():
        blurt_state.set("setup")

    @output
    @render.ui
    async def blurt_main_area_ui():
        state = blurt_state()
        if state == "setup": return ui.div(ui.h4("Active Recall Sandbox", class_="text-center mt-4 text-muted"), style="min-height: 400px;")
        elif state == "blurting": return ui.div(ui.input_text_area("blurt_input", label="Recall everything:", value=blurt_template(), width="100%", height="600px"))
        elif state == "review":
            await session.send_custom_message("render_katex", None)
            
            blurt_in_val = protect_math(input.blurt_input())
            blurt_orig_val = protect_math(blurt_original())
            
            return ui.layout_columns(
                ui.card(ui.card_header("✍️ Your Blurt"), ui.div(ui.markdown(blurt_in_val), class_="blurt-review-panel")),
                ui.card(ui.card_header("📚 Original"), ui.div(ui.markdown(blurt_orig_val), class_="blurt-review-panel")),
                col_widths=(6, 6)
            )

app = App(app_ui, server, static_assets={"/files": BASE_PATH})