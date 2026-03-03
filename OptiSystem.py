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

<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>

<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github.min.css">
<script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>

<script src="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/d3@6"></script>
<script src="https://cdn.jsdelivr.net/npm/markmap-view@0.14.4"></script>
<script src="https://cdn.jsdelivr.net/npm/markmap-lib@0.14.4/dist/browser/index.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
    /* BULLETPROOF EASYMDE SCROLLING */
    .CodeMirror { 
        max-height: 400px !important; 
    }
    .CodeMirror-scroll { 
        min-height: 200px !important; 
        max-height: 400px !important; 
        overflow-y: auto !important; 
        overflow-x: hidden !important;
    }
    
    #mindmap { width: 100%; height: 650px; border: 1px solid #ddd; border-radius: 8px; cursor: grab; background-color: #fff; }
    #mindmap:active { cursor: grabbing; }
    
    svg { width: 100%; height: 100%; } 
    foreignObject { overflow: visible; }
    img { max-width: 350px; max-height: 350px; border: 2px solid #555; border-radius: 6px; display: block; }
    
    .katex-mathml { display: none !important; }

    /* Force bold text to actually render bold and strictly not slanted */
    #mindmap strong, #mindmap b { 
        font-weight: 900 !important; 
        font-style: normal !important; 
        color: #000 !important;
    }

    /* FIX FOR OVERFLOW: Force text to stay on a single line so it doesn't wrap and overlap */
    #mindmap foreignObject div { 
        white-space: nowrap !important; 
    }
    
    .slide-content img { margin: 0 auto; }
    .slide-container { transition: all 0.3s ease-in-out; }
    
    .kpi-card { text-align: center; padding: 20px 10px; border-radius: 8px; background: #f8f9fa; border: 1px solid #dee2e6; }
    .kpi-val { font-size: 2em; font-weight: bold; color: #0d6efd; margin: 10px 0; }
    .kpi-title { font-size: 1em; color: #6c757d; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Blurt Studio Review Heights */
    .blurt-review-panel { max-height: 600px; overflow-y: auto; padding: 15px; background: #fff; border-radius: 5px; border: 1px solid #eee; }
</style>

<script>
    // RESTORED: The exact brute-force method that allows you to pan around successfully
    function updateMindMap(markdown) {
        const { Transformer } = window.markmap;
        const transformer = new Transformer();
        const { root } = transformer.transform(markdown);
        
        // Wipe the canvas clean every time to reset the D3 event listeners
        document.getElementById('mindmap').innerHTML = ''; 
        
        const mapOptions = {
            spacingHorizontal: 140, // Pushes branches further apart
            spacingVertical: 15     // Adds vertical breathing room between nodes
        };
        
        const mm = markmap.Markmap.create('#mindmap', mapOptions, root);
        mm.fit(); 
    }

    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            const textArea = document.getElementById('map_content');
            if (textArea) {
                const easymde = new EasyMDE({ 
                    element: textArea,
                    spellChecker: false,
                    status: false,
                    renderingConfig: {
                        codeSyntaxHighlighting: true
                    },
                    toolbar: [
                        "bold", "italic", "heading", "|", 
                        {
                            name: "highlight",
                            action: function customFunction(editor){
                                const cm = editor.codemirror;
                                const text = cm.getSelection();
                                if (text) {
                                    cm.replaceSelection("<mark style='background-color: #ffeb3b; color: black; padding: 0 4px; border-radius: 3px;'>" + text + "</mark>");
                                }
                            },
                            className: "fa fa-paint-brush",
                            title: "Highlight Text",
                        },
                        {
                            name: "textColor",
                            action: function customFunction(editor){
                                const cm = editor.codemirror;
                                const text = cm.getSelection();
                                if (text) {
                                    const color = prompt("Enter a color (e.g., red, blue, #00ff00):", "red");
                                    if(color) {
                                        cm.replaceSelection("<span style='color: " + color + "; font-weight: bold;'>" + text + "</span>");
                                    }
                                }
                            },
                            className: "fa fa-font",
                            title: "Change Text Color",
                        },
                        "|", "quote", "code", "unordered-list", "ordered-list", "|", "link", "image", "|", "guide"
                    ]
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
        }, 1000); 
    });

    Shiny.addCustomMessageHandler('update_editor', function(markdown) {
        if (window.easymde_editor) { window.easymde_editor.value(markdown); }
        updateMindMap(markdown);
    });

    Shiny.addCustomMessageHandler('render_katex', function(msg) {
        setTimeout(function() {
            if (window.renderMathInElement) {
                renderMathInElement(document.body, {
                    delimiters: [
                        {left: '$$', right: '$$', display: true},
                        {left: '$', right: '$', display: false}
                    ]
                });
            }
        }, 50); 
    });

    // Dashboard Charting Engine (Chart.js)
    window.optiCharts = {};
    Shiny.addCustomMessageHandler('update_dashboard_charts', function(payload) {
        const d_ctx = document.getElementById('dailyChart');
        if(d_ctx) {
            if(window.optiCharts.daily) window.optiCharts.daily.destroy();
            window.optiCharts.daily = new Chart(d_ctx, {
                type: 'line',
                data: {
                    labels: payload.d_labels,
                    datasets: [{ label: 'Minutes Studied', data: payload.d_data, borderColor: '#198754', backgroundColor: 'rgba(25, 135, 84, 0.1)', fill: true, tension: 0.3 }]
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    plugins: { legend: { display: false } }, 
                    scales: { 
                        y: { beginAtZero: true, title: { display: true, text: 'Minutes' } },
                        x: { title: { display: true, text: 'Date' } }
                    } 
                }
            });
        }
        
        const w_ctx = document.getElementById('weeklyChart');
        if(w_ctx) {
            if(window.optiCharts.weekly) window.optiCharts.weekly.destroy();
            window.optiCharts.weekly = new Chart(w_ctx, {
                type: 'line',
                data: {
                    labels: payload.w_labels,
                    datasets: [{ label: 'Minutes Studied', data: payload.w_data, borderColor: '#fd7e14', backgroundColor: 'rgba(253, 126, 20, 0.1)', fill: true, tension: 0.3 }]
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    plugins: { legend: { display: false } }, 
                    scales: { 
                        y: { beginAtZero: true, title: { display: true, text: 'Minutes' } },
                        x: { title: { display: true, text: 'Week' } }
                    } 
                }
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
        try: return pd.read_csv(REV_LOG)
        except: pass
    return pd.DataFrame(columns=["Module", "Map", "Date", "Duration (min)"])

def get_module_names():
    if not os.path.exists(BASE_PATH): return ["General"]
    mods = [d for d in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, d))]
    return mods if mods else ["General"]

def get_saved_maps(module):
    mod_path = os.path.join(BASE_PATH, module)
    if not os.path.exists(mod_path): return []
    return [f for f in os.listdir(mod_path) if f.endswith('.md')]

# --- UI ---
app_ui = ui.page_navbar(
    ui.head_content(ui.HTML(custom_js)), 

    # TAB 1: DASHBOARD
    ui.nav_panel("Analytics Dashboard",
        ui.layout_columns(
            ui.div(ui.output_ui("kpi_today_ui"), class_="kpi-card"),
            ui.div(ui.output_ui("kpi_week_ui"), class_="kpi-card"),
            ui.div(ui.output_ui("kpi_avg_ui"), class_="kpi-card"),
            col_widths=(4, 4, 4)
        ),
        ui.br(),
        ui.card(
            ui.card_header(ui.tags.b("Module Time Distribution (All Time)")),
            ui.output_ui("html_module_bars")
        ),
        ui.layout_columns(
            ui.card(
                ui.card_header(ui.tags.b("Daily Study Trend")),
                ui.HTML('<div style="position: relative; height: 300px; width: 100%;"><canvas id="dailyChart"></canvas></div>')
            ),
            ui.card(
                ui.card_header(ui.tags.b("Weekly Study Trend")),
                ui.HTML('<div style="position: relative; height: 300px; width: 100%;"><canvas id="weeklyChart"></canvas></div>')
            ),
            col_widths=(6, 6)
        )
    ),

    # TAB 2: COMMAND CENTER
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

    # TAB 3: PROGRESS TRACKER
    ui.nav_panel("Progress Tracker",
        ui.card(ui.output_ui("progress_bars_list"))
    ),

    # TAB 4: STUDY LAB
    ui.nav_panel("Study Lab",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### **Concept Architect**"),
                ui.input_select("map_mod", "Select Module", get_module_names()),
                ui.markdown("---"),
                ui.output_ui("map_loader_ui"),
                ui.input_action_button("load_btn", "Load Map", class_="btn-light w-100 mb-2"),
                ui.markdown("---"),
                ui.input_text("save_name", "File Name", placeholder="e.g., SAS_Unit_1"),
                ui.input_action_button("save_btn", "Save Map", class_="btn-primary w-100 mb-2"),
                ui.hr(),
                ui.input_text_area("map_content", None, height="300px", 
                    value="# Central Concept\n## Branch 1\n- Detail A\n\n- Example Math: $y_i$"),
            ),
            ui.card(
                ui.card_header("Interactive Mind Map"),
                ui.HTML('<svg id="mindmap"></svg>')
            )
        )
    ),

    # TAB 5: REVISION Hub
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
            ui.card(
                ui.card_header("Slide Viewer"),
                ui.output_ui("revision_display_ui")
            ),
            ui.card(
                ui.card_header("Recent Sessions"),
                ui.output_table("revision_history_table")
            )
        )
    ),
    
    # TAB 6: BLURT STUDIO
    ui.nav_panel("Blurt Studio",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### **Active Recall**"),
                ui.input_select("blurt_mod_select", "Select Module", get_module_names()),
                ui.output_ui("blurt_map_loader_ui"),
                ui.input_action_button("start_blurt_btn", "Generate Template", class_="btn-primary w-100"),
                ui.hr(),
                ui.input_action_button("review_blurt_btn", "Submit & Review", class_="btn-success w-100"),
                ui.input_action_button("reset_blurt_btn", "Reset Session", class_="btn-danger w-100 mt-2")
            ),
            ui.card(
                ui.output_ui("blurt_main_area_ui")
            )
        )
    ),
    
    title="OptiSystem v6.12",
)

# --- SERVER ---
def server(input, output, session):
    refresh_trigger = reactive.Value(0)
    
    rev_active = reactive.Value(False)
    rev_slides = reactive.Value([])
    rev_current_idx = reactive.Value(0)
    rev_start_time = reactive.Value(0.0)
    
    # Blurt Studio State
    blurt_state = reactive.Value("setup") 
    blurt_original = reactive.Value("")
    blurt_template = reactive.Value("")

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
    def kpi_today_ui():
        refresh_trigger()
        df = get_processed_rev_df()
        today_val = 0.0
        if not df.empty:
            today = datetime.now().date()
            today_val = df[df['Date_Only'] == today]['Duration (min)'].sum()
        return ui.HTML(f"<div class='kpi-title'>Studied Today</div><div class='kpi-val'>{today_val:.1f} <span style='font-size:0.5em'>min</span></div>")

    @output
    @render.ui
    def kpi_week_ui():
        refresh_trigger()
        df = get_processed_rev_df()
        week_val = 0.0
        if not df.empty:
            current_yw = f"{datetime.now().isocalendar()[0]}-W{str(datetime.now().isocalendar()[1]).zfill(2)}"
            week_val = df[df['YearWeek'] == current_yw]['Duration (min)'].sum()
        return ui.HTML(f"<div class='kpi-title'>Studied This Week</div><div class='kpi-val'>{week_val:.1f} <span style='font-size:0.5em'>min</span></div>")

    @output
    @render.ui
    def kpi_avg_ui():
        refresh_trigger()
        df = get_processed_rev_df()
        avg_val = df['Duration (min)'].mean() if not df.empty else 0.0
        return ui.HTML(f"<div class='kpi-title'>Avg Session Length</div><div class='kpi-val'>{avg_val:.1f} <span style='font-size:0.5em'>min</span></div>")

    @output
    @render.ui
    def html_module_bars():
        refresh_trigger()
        df = load_revisions()
        if df.empty: return ui.markdown("_No revision data available yet._")
        
        mod_sum = df.groupby('Module')['Duration (min)'].sum().sort_values(ascending=False)
        max_val = mod_sum.max()
        if max_val == 0: max_val = 1 
        
        bars = []
        for mod, val in mod_sum.items():
            pct = (val / max_val) * 100
            bars.append(ui.HTML(f"""
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-weight: 500; font-size: 0.9em; color: #333;">
                    <span>{mod}</span>
                    <span>{val:.1f} min</span>
                </div>
                <div style="width: 100%; background: #e9ecef; border-radius: 4px; height: 24px; overflow: hidden;">
                    <div style="width: {pct}%; background: #0d6efd; height: 100%; border-radius: 4px; transition: width 0.5s ease-in-out;"></div>
                </div>
            </div>
            """))
        return ui.div(*bars, style="padding: 10px; min-height: 250px;")

    @reactive.Effect
    async def update_line_charts():
        refresh_trigger()
        df = get_processed_rev_df()
        if df.empty: return
        
        daily = df.groupby('Date_Only')['Duration (min)'].sum().sort_index()
        daily_labels = [d.strftime("%b %d") for d in daily.index]
        daily_data = list(daily.values)
        
        weekly = df.groupby('YearWeek')['Duration (min)'].sum().sort_index()
        weekly_labels = list(weekly.index)
        weekly_data = list(weekly.values)
        
        payload = {
            "d_labels": daily_labels, "d_data": daily_data,
            "w_labels": weekly_labels, "w_data": weekly_data
        }
        await session.send_custom_message("update_dashboard_charts", payload)

    # ==========================
    # COMMAND CENTER LOGIC
    # ==========================
    @reactive.Effect
    @reactive.event(input.purge_completed)
    def _purge_tasks():
        df = load_tasks()
        if df.empty: return
        initial_count = len(df)
        df = df[df["Progress"] < 100].reset_index(drop=True)
        df['ID'] = df.index
        df.to_csv(TASK_LOG, index=False)
        refresh_trigger.set(refresh_trigger() + 1)
        deleted_count = initial_count - len(df)
        if deleted_count > 0: ui.notification_show(f"Cleared {deleted_count} tasks!")

    @output
    @render.ui
    def task_selector_ui():
        if input.mode() == "edit":
            df = load_tasks()
            return ui.input_select("task_to_edit", "Select Task", {str(i): row['Objective'] for i, row in df.iterrows()})
        return None

    @output
    @render.ui
    def action_button_ui():
        if input.mode() == "edit":
            return ui.div(
                ui.input_action_button("save_edit", "Update Objective", class_="btn-warning w-100 mb-2"),
                ui.input_action_button("delete_task", "Delete Objective", class_="btn-danger w-100")
            )
        return ui.input_action_button("add_task", "Sync New Objective", class_="btn-primary w-100")

    @reactive.Effect
    @reactive.event(input.task_to_edit)
    def _populate_fields():
        if input.mode() == "edit":
            df = load_tasks()
            try:
                row = df.iloc[int(input.task_to_edit())]
                ui.update_text("task_name", value=row['Objective'])
                ui.update_select("mod_select", selected=row['Module'])
                ui.update_slider("progress_val", value=int(row['Progress']))
                try:
                    ui.update_date("due_date", value=pd.to_datetime(row['Deadline'], errors='coerce').date())
                except: pass 
            except: pass

    @reactive.Effect
    @reactive.event(input.add_task)
    def _add():
        df = load_tasks()
        new_row = pd.DataFrame({"ID": [len(df)], "Objective": [input.task_name()], "Module": [input.mod_select()], "Deadline": [str(input.due_date())], "Progress": [input.progress_val()]})
        pd.concat([df, new_row], ignore_index=True).to_csv(TASK_LOG, index=False)
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show("Objective Added")

    @reactive.Effect
    @reactive.event(input.save_edit)
    def _edit():
        df = load_tasks()
        idx = int(input.task_to_edit())
        df.loc[idx, ["Objective", "Module", "Deadline", "Progress"]] = [input.task_name(), input.mod_select(), str(input.due_date()), input.progress_val()]
        df.to_csv(TASK_LOG, index=False)
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show("Updated Successfully", type="warning")

    @reactive.Effect
    @reactive.event(input.delete_task)
    def _delete():
        df = load_tasks()
        df = df.drop(int(input.task_to_edit())).reset_index(drop=True)
        df['ID'] = df.index
        df.to_csv(TASK_LOG, index=False)
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show("Objective Deleted", type="error")

    @reactive.Effect
    @reactive.event(input.create_mod)
    def _create_folder():
        name = input.new_mod().strip().replace(" ", "_")
        if name:
            os.makedirs(os.path.join(BASE_PATH, name), exist_ok=True)
            refresh_trigger.set(refresh_trigger() + 1)
            mods = get_module_names()
            ui.update_select("mod_select", choices=mods)
            ui.update_select("map_mod", choices=mods)
            ui.update_select("rev_mod_select", choices=mods)
            ui.update_select("blurt_mod_select", choices=mods)

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
            if row['Deadline_dt'].year == 2099: bar_color, status_text = "bg-secondary", "⚠️ DATE ERROR"
            else:
                days_left = (row['Deadline_dt'] - datetime.now()).days + 1
                if row['Progress'] == 100: bar_color, status_text = "bg-success", "DONE"
                elif days_left < 0: bar_color, status_text = "bg-dark", f"OVERDUE ({abs(days_left)}d)"
                elif days_left <= 3: bar_color, status_text = "bg-danger", f"URGENT: {days_left}d left"
                else: bar_color, status_text = "bg-info", f"{days_left}d left"
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
    # STUDY LAB LOGIC
    # ==========================
    @reactive.Effect
    @reactive.event(input.save_btn)
    def _save_map():
        if not input.save_name():
            ui.notification_show("Please name your file first!", type="error")
            return
        filename = input.save_name().strip().replace(" ", "_")
        if not filename.endswith(".md"): filename += ".md"
        with open(os.path.join(BASE_PATH, input.map_mod(), filename), "w") as f:
            f.write(input.map_content())
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show(f"Saved: {filename}", type="message")

    @output
    @render.ui
    def map_loader_ui():
        refresh_trigger() 
        maps = get_saved_maps(input.map_mod())
        if not maps: return ui.markdown("_No saved maps_")
        return ui.input_select("selected_map", "Load Saved Map", maps)

    @reactive.Effect
    @reactive.event(input.load_btn)
    async def _load_map():
        try:
            filename = input.selected_map()
            with open(os.path.join(BASE_PATH, input.map_mod(), filename), "r") as f: content = f.read()
            ui.update_text("save_name", value=filename.replace(".md", ""))
            await session.send_custom_message("update_editor", content) 
            ui.notification_show(f"Loaded: {filename}")
        except Exception as e: ui.notification_show(f"Error: {str(e)}", type="error")

    @reactive.Effect
    @reactive.event(input.pasted_image_trigger)
    async def _handle_paste():
        data_url = input.pasted_image_data()
        if not data_url: return
        header, encoded = data_url.split(",", 1)
        filename = f"img_{int(time.time())}.png"
        mod_dir = os.path.join(BASE_PATH, input.map_mod())
        if not os.path.exists(mod_dir): os.makedirs(mod_dir)
        with open(os.path.join(mod_dir, filename), "wb") as f: f.write(base64.b64decode(encoded))
        full_content = input.map_content() + f"\n- ![{filename}](/files/{input.map_mod()}/{filename})"
        await session.send_custom_message("update_editor", full_content) 
        ui.notification_show(f"Image saved to {input.map_mod()}")

    # ==========================
    # REVISION HUB LOGIC 
    # ==========================
    @output
    @render.ui
    def rev_map_loader_ui():
        refresh_trigger()
        maps = get_saved_maps(input.rev_mod_select())
        if not maps: return ui.markdown("_No saved maps_")
        return ui.input_select("rev_selected_map", "Select Map to Revise", maps)

    @reactive.Effect
    @reactive.event(input.start_rev_btn)
    def _start_revision():
        mod = input.rev_mod_select()
        map_name = input.rev_selected_map()
        if not map_name: return ui.notification_show("No map selected.", type="error")
        
        path = os.path.join(BASE_PATH, mod, map_name)
        if not os.path.exists(path): return
            
        with open(path, "r") as f: lines = f.readlines()
        
        slides = []
        path_stack = []
        for line in lines:
            if not line.strip(): continue
            raw = line.rstrip()
            
            if raw.startswith('#'):
                level = len(raw) - len(raw.lstrip('#'))
                content = raw.lstrip('#').strip()
            else:
                indent = len(raw) - len(raw.lstrip())
                level = 10 + indent 
                content = raw.strip()
                for char in ['-', '*', '+']:
                    if content.startswith(char):
                        content = content.lstrip(char).strip()
                        break
                        
            while path_stack and path_stack[-1][0] >= level: path_stack.pop()
                
            breadcrumb = " ➔ ".join([p[1] for p in path_stack]) if path_stack else "Root Node"
            slides.append({"breadcrumb": breadcrumb, "raw": raw})
            path_stack.append((level, content))
            
        if not slides: return ui.notification_show("Map is empty!", type="warning")
            
        rev_slides.set(slides)
        rev_current_idx.set(0)
        rev_start_time.set(time.time())
        rev_active.set(True)

    @reactive.Effect
    @reactive.event(input.next_slide)
    def _next_slide():
        idx = rev_current_idx()
        if idx < len(rev_slides()) - 1: rev_current_idx.set(idx + 1)

    @reactive.Effect
    @reactive.event(input.prev_slide)
    def _prev_slide():
        idx = rev_current_idx()
        if idx > 0: rev_current_idx.set(idx - 1)

    @reactive.Effect
    @reactive.event(input.finish_slide)
    def _finish_revision():
        duration = round((time.time() - rev_start_time()) / 60, 2)
        df = load_revisions()
        new_row = pd.DataFrame({
            "Module": [input.rev_mod_select()],
            "Map": [input.rev_selected_map()],
            "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")],
            "Duration (min)": [duration]
        })
        pd.concat([df, new_row], ignore_index=True).to_csv(REV_LOG, index=False)
        rev_active.set(False)
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show(f"Session Complete! Tracked {duration} minutes.", type="message")

    @output
    @render.ui
    async def revision_display_ui():
        if not rev_active():
            return ui.div(
                ui.h4("Ready to Review?", class_="text-center mt-4 text-muted"),
                ui.p("Select a module and map from the sidebar to begin navigating your notes step-by-step.", class_="text-center text-muted"),
                style="min-height: 250px; display: flex; flex-direction: column; justify-content: center;"
            )
            
        slides = rev_slides()
        idx = rev_current_idx()
        slide = slides[idx]
        
        await session.send_custom_message("render_katex", None)
        
        return ui.div(
            ui.p(slide["breadcrumb"], class_="text-muted", style="font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px;"),
            ui.hr(style="margin-top: 5px;"),
            ui.div(
                ui.markdown(slide["raw"]), 
                class_="slide-content",
                style="font-size: 1.6em; padding: 20px 10px; min-height: 250px; display: flex; align-items: center; justify-content: center; text-align: center;"
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
        if df.empty: return pd.DataFrame(columns=["Module", "Map", "Date", "Duration (min)"])
        return df.sort_index(ascending=False).head(10) 

    @output
    @render.ui
    def rev_quick_stats_ui():
        refresh_trigger()
        df = load_revisions()
        if df.empty: return ui.markdown("_No stats yet. Complete a session!_")
        
        total_time = df['Duration (min)'].sum()
        last_mod = df.iloc[-1]['Module'] if not df.empty else "N/A"
        
        return ui.div(
            ui.p(ui.tags.b("Total Time Studied: "), f"{round(total_time, 1)} mins"),
            ui.p(ui.tags.b("Last Revised: "), f"{last_mod}")
        )

    # ==========================
    # BLURT STUDIO LOGIC 
    # ==========================
    @output
    @render.ui
    def blurt_map_loader_ui():
        refresh_trigger()
        maps = get_saved_maps(input.blurt_mod_select())
        if not maps: return ui.markdown("_No saved maps_")
        return ui.input_select("blurt_selected_map", "Select Map to Blurt", maps)

    @reactive.Effect
    @reactive.event(input.start_blurt_btn)
    def _start_blurt():
        mod = input.blurt_mod_select()
        map_name = input.blurt_selected_map()
        if not map_name:
            ui.notification_show("No map selected.", type="error")
            return

        path = os.path.join(BASE_PATH, mod, map_name)
        if not os.path.exists(path): return

        with open(path, "r") as f:
            content = f.read()

        blurt_original.set(content)

        # Generate template by extracting headers and handling images
        lines = content.split('\n')
        template_lines = []
        for line in lines:
            if line.strip().startswith('#'):
                # Replace markdown images with a text prompt to recall what the image was
                clean_line = re.sub(r'!\[.*?\]\(.*?\)', '[Image Reference]', line).strip()
                
                # Check if there is still content left (ignores headers that were somehow reduced to just '#')
                if clean_line.replace('#', '').strip():
                    template_lines.append(clean_line)
                    template_lines.append("\n\n\n")

        blurt_template.set("".join(template_lines))
        blurt_state.set("blurting")
        ui.notification_show("Template Generated! Start recalling.", type="message")

    @reactive.Effect
    @reactive.event(input.review_blurt_btn)
    def _review_blurt():
        if blurt_state() == "blurting":
            blurt_state.set("review")
            ui.notification_show("Review Mode Activated", type="warning")
        else:
            ui.notification_show("Generate a template first.", type="error")

    @reactive.Effect
    @reactive.event(input.reset_blurt_btn)
    def _reset_blurt():
        blurt_state.set("setup")
        blurt_original.set("")
        blurt_template.set("")
        ui.notification_show("Session Reset", type="message")

    @output
    @render.ui
    async def blurt_main_area_ui():
        state = blurt_state()

        if state == "setup":
            return ui.div(
                ui.h4("Active Recall Sandbox", class_="text-center mt-4 text-muted"),
                ui.p("Select a map and click 'Generate Template' to extract headers and start your blurt session.", class_="text-center text-muted"),
                style="min-height: 400px; display: flex; flex-direction: column; justify-content: center;"
            )
            
        elif state == "blurting":
            return ui.div(
                ui.card_header("🧠 Active Recall: Type what you remember under each heading"),
                ui.input_text_area(
                    "blurt_input", 
                    label=None, 
                    value=blurt_template(), 
                    width="100%", 
                    height="600px"
                )
            )
            
        elif state == "review":
            await session.send_custom_message("render_katex", None)
            return ui.layout_columns(
                ui.card(
                    ui.card_header(ui.tags.b("✍️ Your Blurt")),
                    ui.div(
                        ui.markdown(input.blurt_input()),
                        class_="blurt-review-panel"
                    )
                ),
                ui.card(
                    ui.card_header(ui.tags.b("📚 Original Source")),
                    ui.div(
                        ui.markdown(blurt_original()),
                        class_="blurt-review-panel"
                    )
                ),
                col_widths=(6, 6)
            )

app = App(app_ui, server, static_assets={"/files": BASE_PATH})