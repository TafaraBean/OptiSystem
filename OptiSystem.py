import os
import pandas as pd
import base64
import time
import re
from datetime import datetime
from shiny import App, render, ui, reactive

# --- CONFIGURATION ---
BASE_PATH = os.path.join(os.getcwd(), "OptiSystem_Data")
TASK_LOG = os.path.join(BASE_PATH, "master_tasks.csv")
REV_LOG = os.path.join(BASE_PATH, "revision_log.csv")

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
    
    .blurt-review-panel { max-height: 600px; overflow-y: auto; overflow-x: auto; padding: 15px; background: #fff; border-radius: 5px; border: 1px solid #eee; word-wrap: break-word; overflow-wrap: break-word; }
    .blurt-review-panel > * { max-width: 100%; }
    
    .reading-source-pane { padding: 15px; border-right: 2px solid #e9ecef; font-size: 1.1em; background-color: #f8f9fa; border-radius: 5px 0 0 5px; }
    .reading-notes-pane { padding: 15px; background-color: #fff; border-radius: 0 5px 5px 0; }
    .aligned-row { border: 1px solid #dee2e6; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    .katex-display { overflow-x: auto; overflow-y: hidden; max-width: 100%; padding-bottom: 5px; }
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
                        updateMindMap(content); 
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

                updateMindMap(easymde.value());
            }
            
            // --- APPLE PENCIL SCRATCHPAD LOGIC ---
            const canvas = document.getElementById('scratchpad-canvas');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                // Fill background with white so it saves properly as a PNG
                ctx.fillStyle = "white";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                let drawing = false;
                
                function getPos(e) {
                    const rect = canvas.getBoundingClientRect();
                    const scaleX = canvas.width / rect.width;
                    const scaleY = canvas.height / rect.height;
                    let clientX = e.clientX;
                    let clientY = e.clientY;
                    
                    if(e.touches && e.touches.length > 0) {
                        clientX = e.touches[0].clientX;
                        clientY = e.touches[0].clientY;
                    }
                    
                    return {
                        x: (clientX - rect.left) * scaleX,
                        y: (clientY - rect.top) * scaleY
                    };
                }

                function startDraw(e) {
                    // Prevent page scrolling while drawing
                    if(e.type !== 'mousedown') e.preventDefault(); 
                    drawing = true;
                    const pos = getPos(e);
                    ctx.beginPath();
                    ctx.moveTo(pos.x, pos.y);
                    
                    // Apple Pencil Pressure sensitivity
                    let pressure = e.pressure !== undefined ? e.pressure : 0.5;
                    ctx.lineWidth = (pressure * 6) + 1; 
                    ctx.lineCap = 'round';
                    ctx.lineJoin = 'round';
                    ctx.strokeStyle = '#2c3e50';
                }

                function draw(e) {
                    if (!drawing) return;
                    if(e.type !== 'mousemove') e.preventDefault();
                    const pos = getPos(e);
                    
                    if (e.pressure !== undefined && e.pointerType === 'pen') {
                        ctx.lineWidth = (e.pressure * 8) + 1; 
                    }
                    
                    ctx.lineTo(pos.x, pos.y);
                    ctx.stroke();
                }

                function endDraw(e) {
                    if(!drawing) return;
                    drawing = false;
                }

                // Native Pointer Events (Perfect for iPad/Apple Pencil)
                canvas.addEventListener('pointerdown', startDraw);
                canvas.addEventListener('pointermove', draw);
                canvas.addEventListener('pointerup', endDraw);
                canvas.addEventListener('pointercancel', endDraw);
                
                // Fallbacks
                canvas.addEventListener('touchstart', startDraw, {passive: false});
                canvas.addEventListener('touchmove', draw, {passive: false});
                canvas.addEventListener('touchend', endDraw);
                
                window.saveScratchpad = function() {
                    const dataURL = canvas.toDataURL('image/png');
                    Shiny.setInputValue('scratchpad_img_data', dataURL);
                    Shiny.setInputValue('scratchpad_save_trigger', Math.random());
                };
                
                window.clearScratchpad = function() {
                    ctx.fillStyle = "white";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                };
            }
            
        }, 1000); 
        
        const observer = new MutationObserver((mutations) => {
            attachSyncScroll();
        });
        observer.observe(document.body, { childList: true, subtree: true });
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
        updateMindMap(markdown);
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
                ui.markdown("### **Session Timer**"),
                ui.input_action_button("start_sl_btn", "Start Note-taking", class_="btn-info w-100 mb-2"),
                ui.input_action_button("end_sl_btn", "End Session & Log", class_="btn-danger w-100"),
                ui.hr(),
                ui.input_text_area("map_content", None, height="200px", 
                    value="# Central Concept\n## Branch 1\n- Detail A\n\n- Example Math: $y_i$"),
            ),
            ui.card(
                ui.card_header("Interactive Mind Map"),
                ui.HTML('<svg id="mindmap"></svg>')
            )
        )
    ),

    # ---> NEW SCRATCHPAD TAB <---
    ui.nav_panel("Scratchpad",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### **Apple Pencil Canvas**"),
                ui.input_select("scratch_mod", "Select Module", get_module_names()),
                ui.input_text("scratch_name", "Image Name", placeholder="e.g., cell_diagram"),
                ui.input_action_button("save_scratch_btn", "Save & Sync PNG 💾", class_="btn-success w-100 mb-2", onclick="saveScratchpad()"),
                ui.input_action_button("clear_scratch_btn", "Clear Canvas 🗑️", class_="btn-danger w-100", onclick="clearScratchpad()"),
                ui.hr(),
                ui.markdown("*Draw freehand graphs, equations, or diagrams. Saving exports it straight to your module folder!*")
            ),
            ui.card(
                ui.card_header("Digital Whiteboard"),
                ui.div(
                    ui.HTML('<canvas id="scratchpad-canvas" width="800" height="600" style="border: 1px solid #dee2e6; border-radius: 8px; cursor: crosshair; touch-action: none; background-color: white; max-width: 100%;"></canvas>'),
                    style="display: flex; justify-content: center; align-items: center; background-color: #f8f9fa; padding: 20px; border-radius: 8px;"
                )
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
    
    title="OptiSystem v6.29",
)

# --- SERVER ---
def server(input, output, session):
    refresh_trigger = reactive.Value(0)
    
    read_state = reactive.Value({"mode": None, "data": None})
    sl_active = reactive.Value(False)
    sl_start_time = reactive.Value(0.0)

    rev_active = reactive.Value(False)
    rev_slides = reactive.Value([])
    rev_current_idx = reactive.Value(0)
    rev_start_time = reactive.Value(0.0)
    
    blurt_state = reactive.Value("setup") 
    blurt_original = reactive.Value("")
    blurt_template = reactive.Value("")
    blurt_start_time = reactive.Value(0.0)

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
            for select_id in ["mod_select", "read_mod", "map_mod", "rev_mod_select", "blurt_mod_select", "scratch_mod"]: 
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
    # READING ROOM LOGIC (NO SAVING PDF)
    # ==========================
    @reactive.Effect
    @reactive.event(input.process_read_btn)
    def _process_reading():
        pdf_info = input.upload_pdf()
        text_source = input.read_source()

        if pdf_info:
            try:
                pdf_path = pdf_info[0]["datapath"]
                
                # Convert PDF straight to Base64 in memory! No hard drive saving.
                with open(pdf_path, "rb") as f:
                    pdf_b64 = base64.b64encode(f.read()).decode('utf-8')
                
                # Create a data URI to inject directly into the browser
                data_uri = f"data:application/pdf;base64,{pdf_b64}"
                
                read_state.set({
                    "mode": "pdf", 
                    "data": data_uri
                })
                ui.notification_show("PDF loaded straight to memory! No files saved locally.", type="message")
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
            return ui.div(
                ui.layout_columns(
                    ui.div(
                        ui.tags.iframe(src=state["data"], width="100%", height="800px", style="border: none; border-radius: 5px;"),
                        class_="reading-source-pane", style="padding: 0; overflow: hidden;"
                    ),
                    ui.div(
                        ui.input_text_area(
                            "read_note_main", 
                            label=None, 
                            placeholder="Draft your notes here while reading the PDF on the left...\n\nUse empty lines (Enter) to push your notes down so they physically align with the pages of the PDF on the left!\n\nTip: You can paste images directly here!", 
                            width="100%", 
                            height="800px"
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
                        ui.input_text_area(
                            "read_note_main", 
                            label=None, 
                            placeholder="Draft your notes here...\n\nUse empty lines (Enter) to push your notes down so they physically map and align with the text on the left!\n\nTip: You can paste images directly here!", 
                            width="100%", 
                            height="800px"
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
        return ui.input_select("selected_map", "Load Saved Map", maps) if maps else ui.markdown("_No saved maps_")

    @reactive.Effect
    @reactive.event(input.load_btn)
    async def _load_map():
        try:
            with open(os.path.join(BASE_PATH, input.map_mod(), input.selected_map()), "r") as f: content = f.read()
            ui.update_text("save_name", value=input.selected_map().replace(".md", ""))
            await session.send_custom_message("update_editor", content) 
        except Exception as e: ui.notification_show(f"Error: {str(e)}", type="error")

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
    # SCRATCHPAD LOGIC 
    # ==========================
    @reactive.Effect
    @reactive.event(input.scratchpad_save_trigger)
    def _save_scratchpad():
        data_url = input.scratchpad_img_data()
        filename = input.scratch_name().strip()
        
        if not filename:
            ui.notification_show("Please provide an Image Name to save your drawing!", type="warning")
            return
            
        if not data_url: return
        
        if not filename.endswith('.png'):
            filename += '.png'
            
        header, encoded = data_url.split(",", 1)
        mod_dir = os.path.join(BASE_PATH, input.scratch_mod())
        os.makedirs(mod_dir, exist_ok=True)
        
        with open(os.path.join(mod_dir, filename), "wb") as f: 
            f.write(base64.b64decode(encoded))
            
        ui.notification_show(f"Saved {filename} to {input.scratch_mod()}!", type="message")
        refresh_trigger.set(refresh_trigger() + 1)

    # ==========================
    # REVISION HUB LOGIC 
    # ==========================
    @output
    @render.ui
    def rev_map_loader_ui():
        refresh_trigger()
        maps = get_saved_maps(input.rev_mod_select())
        return ui.input_select("rev_selected_map", "Select Map to Revise", maps) if maps else ui.markdown("_No saved maps_")

    @reactive.Effect
    @reactive.event(input.start_rev_btn)
    def _start_revision():
        if not input.rev_selected_map(): return
        path = os.path.join(BASE_PATH, input.rev_mod_select(), input.rev_selected_map())
        if not os.path.exists(path): return
        
        with open(path, "r") as f: lines = f.readlines()
        
        slides = []
        path_stack = []
        current_raw = []
        
        in_math = False
        in_code = False
        
        def save_node():
            if current_raw:
                raw_text = "\n".join(current_raw).strip()
                if raw_text:
                    breadcrumb = " ➔ ".join([p[1] for p in path_stack]) if path_stack else "Root Node"
                    slides.append({"breadcrumb": breadcrumb, "raw": raw_text})
                current_raw.clear()

        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith("`" * 3): in_code = not in_code
            if stripped.count("$$") % 2 != 0: in_math = not in_math
                
            is_new_node = False
            level = 0
            content = ""
            
            if not in_math and not in_code:
                if re.match(r'^#{1,6}\s', line):
                    is_new_node = True
                    level = len(line) - len(line.lstrip('#'))
                    content = line.lstrip('#').strip()
                elif re.match(r'^\s*[-*+]\s', line):
                    is_new_node = True
                    level = 10 + len(line) - len(line.lstrip())
                    content = line.strip().lstrip('-*+').strip()
                elif re.match(r'^\s*\d+\.\s', line):
                    is_new_node = True
                    level = 10 + len(line) - len(line.lstrip())
                    content = re.sub(r'^\s*\d+\.\s*', '', line).strip()

            if is_new_node:
                save_node() 
                while path_stack and path_stack[-1][0] >= level: 
                    path_stack.pop()
                path_stack.append((level, content))
                
            current_raw.append(line.rstrip("\n"))
            
        save_node() 
        
        if not slides:
            slides = [{"breadcrumb": "Empty", "raw": "No content found."}]
            
        rev_slides.set(slides)
        rev_current_idx.set(0)
        rev_start_time.set(time.time())
        rev_active.set(True)

    @reactive.Effect
    @reactive.event(input.next_slide)
    def _next_slide():
        if rev_current_idx() < len(rev_slides()) - 1: rev_current_idx.set(rev_current_idx() + 1)

    @reactive.Effect
    @reactive.event(input.prev_slide)
    def _prev_slide():
        if rev_current_idx() > 0: rev_current_idx.set(rev_current_idx() - 1)

    @reactive.Effect
    @reactive.event(input.finish_slide)
    def _finish_revision():
        duration = round((time.time() - rev_start_time()) / 60, 2)
        df = load_revisions()
        new_row = pd.DataFrame({"Module": [input.rev_mod_select()], "Map": [input.rev_selected_map()], "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], "Duration (min)": [duration], "Activity": ["Revision"]})
        pd.concat([df, new_row], ignore_index=True).to_csv(REV_LOG, index=False)
        rev_active.set(False)
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show(f"Session Complete! Logged {duration} mins.", type="message")

    @output
    @render.ui
    async def revision_display_ui():
        if not rev_active(): return ui.div(ui.h4("Ready to Review?", class_="text-center mt-4 text-muted"), style="min-height: 250px; display: flex; flex-direction: column; justify-content: center;")
        slides, idx = rev_slides(), rev_current_idx()
        await session.send_custom_message("render_katex", None)
        
        display_raw = protect_math(slides[idx]["raw"])
        
        return ui.div(
            ui.p(slides[idx]["breadcrumb"], class_="text-muted", style="font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px;"),
            ui.hr(style="margin-top: 5px;"),
            ui.div(
                ui.markdown(display_raw), 
                class_="slide-content", 
                style="font-size: 1.6em; padding: 20px 10px; min-height: 250px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;"
            ),
            ui.hr(),
            ui.div(
                ui.input_action_button("prev_slide", "⬅️ Prev", class_="btn-light"),
                ui.span(f" Node {idx + 1} of {len(slides)} ", style="margin: 0 15px; font-weight: bold; font-size: 1.1em;"),
                ui.input_action_button("next_slide", "Next ➡️", class_="btn-primary"),
                ui.input_action_button("finish_slide", "End Session", class_="btn-danger", style="float:right;"),
                style="margin-top: 15px; text-align: center;"
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
        return ui.input_select("blurt_selected_map", "Select Map to Blurt", maps) if maps else ui.markdown("_No saved maps_")

    @reactive.Effect
    @reactive.event(input.start_blurt_btn)
    def _start_blurt():
        if not input.blurt_selected_map(): return
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
            new_row = pd.DataFrame({"Module": [input.blurt_mod_select()], "Map": [input.blurt_selected_map()], "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], "Duration (min)": [duration], "Activity": ["Blurt"]})
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