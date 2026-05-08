import os
import shutil
import pandas as pd
import base64
import time
import re
import random
import asyncio
import threading
from datetime import datetime
from shiny import App, render, ui, reactive

# --- ML DEPENDENCIES ---
try:
    import fitz
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    fitz = None
    SentenceTransformer = None
    util = None

# Preload Semantic Model asynchronously to prevent blocking the UI
SEMANTIC_MODEL = None

def _preload_model():
    global SEMANTIC_MODEL
    
    if SentenceTransformer is not None:
        try:
            print("Loading Semantic Model (BAAI/bge-small-en-v1.5)...")
            SEMANTIC_MODEL = SentenceTransformer('BAAI/bge-small-en-v1.5')
            print("Semantic Model loaded successfully.")
        except Exception as e:
            print(f"Error loading Semantic model: {e}")

threading.Thread(target=_preload_model, daemon=True).start()

# --- CONFIGURATION ---
BASE_PATH = os.path.join(os.getcwd(), "OptiSystem_Data")
REV_LOG = os.path.join(BASE_PATH, "revision_log.csv")
STATS_LOG = os.path.join(BASE_PATH, "user_stats.csv") 

if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

# --- GAMIFICATION QUEST POOL ---
QUEST_POOL = [
    {"id": "q_read_15",  "desc": "Read & Annotate for 15+ mins", "xp": 300, "type": "duration", "target": 15, "activity": "Reading"},
    {"id": "q_blurt_1",  "desc": "Complete a Blurt session",     "xp": 250, "type": "activity", "target": 1,  "activity": "Blurt"},
    {"id": "q_blurt_80", "desc": "Achieve 80%+ coverage in Blurt","xp": 400, "type": "accuracy", "target": 0.80,"activity": "Blurt"}
]

def get_daily_quests():
    """Seeds RNG with today's date so quests remain consistent all day."""
    today_seed = int(datetime.now().strftime("%Y%m%d"))
    rng = random.Random(today_seed)
    return rng.sample(QUEST_POOL, 3)

# --- JAVASCRIPT & CSS ---
custom_js = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">

<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>

<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github.min.css">
<script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>

<script src="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
    .CodeMirror { max-height: 400px !important; }
    .CodeMirror-scroll { min-height: 200px !important; max-height: 400px !important; overflow-y: auto !important; overflow-x: hidden !important; }
    img { max-width: 350px; max-height: 350px; border: 2px solid #555; border-radius: 6px; display: block; }
    .katex-mathml { display: none !important; }
    
    /* Hide raw textarea under EasyMDE */
    #read_note_main { display: none !important; }
    
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
    
    #loot-counter { font-weight: 800; color: #198754; background: #e8f5e9; padding: 8px 15px; border-radius: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.3s ease; display: inline-block; font-size: 1.1em; }
    .loot-pop { transform: scale(1.15); background: #d4edda; box-shadow: 0 0 15px rgba(25, 135, 84, 0.5); }
    
    /* Gamification HUD Styles */
    .gamification-hud {
        position: fixed;
        top: 8px;
        right: 20px;
        z-index: 1050;
        display: flex;
        gap: 15px;
        background: rgba(255, 255, 255, 0.90);
        padding: 6px 15px;
        border-radius: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #dee2e6;
        backdrop-filter: blur(5px);
        pointer-events: none; 
    }
    .hud-item { display: flex; align-items: center; font-weight: bold; font-size: 1.05em; }
    .hud-streak { color: #ff8c00; }
    .hud-level { color: #6f42c1; }
    .hud-xp { color: #198754; font-size: 0.85em; background: #e8f5e9; padding: 2px 8px; border-radius: 12px; margin-left: 8px; border: 1px solid #c3e6cb;}
    
    /* Fog of War Exploration Mechanics */
    .fog-text {
        color: var(--text-muted) !important;
        background-color: rgba(10, 10, 15, 0.4);
        border-radius: 3px;
        filter: blur(1.5px);
        transition: all 0.3s ease;
        cursor: help;
    }
    .fog-text:hover {
        filter: blur(0px);
        color: var(--accent-danger) !important;
        background-color: rgba(255, 77, 109, 0.15);
    }
    .explored-text {
        color: var(--text-primary) !important;
        background-color: rgba(0, 217, 126, 0.15);
        border-radius: 3px;
        padding: 0 2px;
        transition: all 0.4s ease;
        box-shadow: 0 0 8px rgba(0, 217, 126, 0.1);
    }
    
    /* Focus Depletion Bar */
    #focus-bar-track {
        position: fixed; top: 0; left: 0; width: 100%; height: 7px;
        background: rgba(0,0,0,0.08); z-index: 10002; pointer-events: none;
    }
    #focus-bar-fill {
        height: 100%; width: 100%;
        background: #2d9e6b;
        transition: width 0.9s linear, background-color 0.7s ease;
        border-radius: 0 0 4px 0;
    }
    @keyframes pulseBar {
        0%   { opacity: 1; }
        50%  { opacity: 0.45; }
        100% { opacity: 1; }
    }
    .bar-critical { animation: pulseBar 0.8s ease-in-out infinite; }
</style>

<script>
    // ============================================================
    // SESSION TIMER & IDLE ANCHOR SYSTEM
    // ============================================================
    window.sessionLoginTime = Date.now();
    window.lastActivityTime  = Date.now();
    window.idleWarningActive = false;
    window.idleTriggers = 0; // Tracks Engagement Score
    const IDLE_THRESHOLD_MS  = 3 * 60 * 1000; // 3 minutes

    function ensureOverlaysExist() {
        if (!document.body) return;
        
        if (!document.getElementById('focus-bar-track')) {
            const track = document.createElement('div');
            track.id = 'focus-bar-track';
            track.innerHTML = '<div id="focus-bar-fill"></div>';
            document.body.appendChild(track);
        }

        if (!document.getElementById('idle-overlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'idle-overlay';
            overlay.innerHTML = `
                <div style="
                    background: white;
                    padding: 45px 40px;
                    border-radius: 16px;
                    text-align: center;
                    max-width: 500px;
                    width: 90%;
                    box-shadow: 0 25px 70px rgba(0,0,0,0.55);
                    border-top: 6px solid #dc3545;
                ">
                    <div style="font-size:3.5em; margin-bottom:12px; line-height:1;">🧭</div>
                    <h2 style="color:#dc3545; font-weight:900; margin-bottom:8px; font-size:1.9em; letter-spacing:-0.5px;">You're Drifting.</h2>
                    <p style="color:#6c757d; font-size:1.05em; margin-bottom:8px; line-height:1.6;">
                        3 minutes passed with no activity detected.<br>
                        Your future self needs you focused — right now.
                    </p>
                    <div id="idle-elapsed-display" style="
                        font-size: 2.4em;
                        font-weight: 900;
                        color: #dc3545;
                        margin: 18px 0;
                        letter-spacing: 2px;
                        font-variant-numeric: tabular-nums;
                    ">00:00</div>
                    <p style="color:#adb5bd; font-size: 0.85em; margin-bottom: 25px;">time you've been away</p>
                    <button
                        id="dismiss-idle-btn"
                        style="
                            background: #dc3545;
                            color: white;
                            border: none;
                            padding: 15px 40px;
                            border-radius: 10px;
                            font-size: 1.15em;
                            font-weight: 800;
                            cursor: pointer;
                            width: 100%;
                            letter-spacing: 0.5px;
                            transition: transform 0.1s, filter 0.2s;
                        "
                        onmouseover="this.style.filter='brightness(1.15)'"
                        onmouseout="this.style.filter='brightness(1)'"
                        onmousedown="this.style.transform='scale(0.97)'"
                        onmouseup="this.style.transform='scale(1)'"
                        onclick="dismissIdle()"
                    >
                        I'm Back — Resume Focus 🔥
                    </button>
                </div>`;
            overlay.style.cssText = `
                display: none;
                position: fixed;
                top: 0; left: 0;
                width: 100vw; height: 100vh;
                background: rgba(10, 10, 20, 0.82);
                backdrop-filter: blur(4px);
                z-index: 10000;
                justify-content: center;
                align-items: center;
                flex-direction: column;
            `;
            document.body.appendChild(overlay);
        }
    }

    function resetIdleTimer() {
        window.lastActivityTime = Date.now();
        if (window.idleWarningActive) { dismissIdle(); }
    }

    function dismissIdle() {
        window.idleWarningActive  = false;
        window.lastActivityTime   = Date.now();
        const overlay = document.getElementById('idle-overlay');
        if (overlay) overlay.style.display = 'none';
        const fill = document.getElementById('focus-bar-fill');
        if (fill) { fill.classList.remove('bar-critical'); fill.style.width = '100%'; fill.style.backgroundColor = '#2d9e6b'; }
    }

    function showIdleOverlay() {
        if (window.idleWarningActive) return;
        window.idleWarningActive = true;
        window.idleTriggers = (window.idleTriggers || 0) + 1;
        Shiny.setInputValue('current_idle_triggers', window.idleTriggers);
        
        const overlay = document.getElementById('idle-overlay');
        if (overlay) overlay.style.display = 'flex';
    }

    Shiny.addCustomMessageHandler('reset_session_metrics', function(_) {
        window.idleTriggers = 0;
        window.sessionStartTime = Date.now();
        resetIdleTimer();
        Shiny.setInputValue('current_idle_triggers', 0);
    });

    function formatSessionTime(ms) {
        const totalSecs = Math.floor(ms / 1000);
        const hrs  = Math.floor(totalSecs / 3600);
        const mins = Math.floor((totalSecs % 3600) / 60);
        const secs = totalSecs % 60;
        if (hrs > 0) return `${hrs}h ${String(mins).padStart(2,'0')}m`;
        return `${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;
    }

    const BAR_STOPS = [
        { threshold: 0.65, color: '#2d9e6b' },  // green  — 0–35% idle
        { threshold: 0.40, color: '#84cc16' },  // lime   — 35–60% idle
        { threshold: 0.18, color: '#f59e0b' },  // amber  — 60–82% idle
        { threshold: 0.00, color: '#ef4444' },  // red    — 82–100% idle
    ];

    function getBarColor(pct) {
        for (const stop of BAR_STOPS) {
            if (pct >= stop.threshold) return stop.color;
        }
        return '#b91c1c'; // fully drained
    }

    // Master heartbeat: updates timer display + checks idle every second
    setInterval(function() {
        ensureOverlaysExist();

        const now    = Date.now();
        const idleMs = now - window.lastActivityTime;
        const pct    = Math.max(0, 1 - idleMs / IDLE_THRESHOLD_MS);

        // 1. Drive the focus depletion bar
        const fill = document.getElementById('focus-bar-fill');
        if (fill) {
            fill.style.width = (pct * 100).toFixed(1) + '%';
            fill.style.backgroundColor = getBarColor(pct);
            if (pct < 0.18 && pct > 0) {
                fill.classList.add('bar-critical');
            } else {
                fill.classList.remove('bar-critical');
            }
        }

        // 2. Session timer in HUD
        const timerEl = document.getElementById('session-timer-display');
        if (timerEl) timerEl.textContent = formatSessionTime(now - window.sessionLoginTime);

        // 3. Idle elapsed counter inside the overlay
        if (window.idleWarningActive) {
            const idleEl = document.getElementById('idle-elapsed-display');
            if (idleEl) idleEl.textContent = formatSessionTime(idleMs);
        }

        // 4. Trigger overlay at full depletion
        if (pct === 0) { showIdleOverlay(); }

    }, 1000);

    // --- ACTIVITY HOOKS: reset idle on any relevant user interaction ---
    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'TEXTAREA' || (e.target.closest && e.target.closest('.CodeMirror'))) { resetIdleTimer(); }
    }, true);

    document.addEventListener('click', function(e) {
        resetIdleTimer();
    }, true);

    // --- FOG OF WAR: SOFT-MARGIN CONCEPT HIGHLIGHTER ---
    window.originalSourceHTML = null;

    function updateFogOfWar(notesText) {
        const sourceMap = document.getElementById('fog-of-war-container');
        if (!sourceMap) return;

        if (!window.originalSourceHTML) {
            window.originalSourceHTML = sourceMap.innerHTML; // Cache pure HTML on first run
        }

        const stopwords = new Set(["with", "from", "this", "that", "were", "been", "being", "have", "does", "could", "will", "would", "should", "might", "must", "what", "when", "where", "which", "then", "than", "because", "since", "until", "only", "also", "very", "just", "about", "into", "through", "after", "before", "over", "under", "between", "some", "such", "same", "every", "other", "another", "their", "there", "they"]);
        
        // Extract 4+ letter stems from user notes
        const noteWords = notesText.toLowerCase().match(/\\b[a-z]{4,}\\b/g) || [];
        const noteStems = new Set();
        noteWords.forEach(w => {
            if (!stopwords.has(w)) noteStems.add(w.substring(0, 5));
        });

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = window.originalSourceHTML;
        
        let totalConcepts = 0;
        let capturedConcepts = 0;

        // Safely walk text nodes to avoid destroying HTML attributes
        function walk(node) {
            if (node.nodeType === 3) { // Text node
                const text = node.nodeValue;
                const replaced = text.replace(/\\b[a-zA-Z]{4,}\\b/g, function(match) {
                    const lower = match.toLowerCase();
                    if (stopwords.has(lower)) return match;
                    
                    totalConcepts++;
                    if (noteStems.has(lower.substring(0, 5))) {
                        capturedConcepts++;
                        return `|EXPLORED|${match}|/EXPLORED|`;
                    } else {
                        return `|FOG|${match}|/FOG|`;
                    }
                });
                
                if (replaced !== text) {
                    const span = document.createElement('span');
                    span.innerHTML = replaced
                        .replace(/\\|EXPLORED\\|/g, '<span class="explored-text">')
                        .replace(/\\|\\/EXPLORED\\|/g, '</span>')
                        .replace(/\\|FOG\\|/g, '<span class="fog-text">')
                        .replace(/\\|\\/FOG\\|/g, '</span>');
                    node.parentNode.replaceChild(span, node);
                }
            } else if (node.nodeType === 1 && node.nodeName !== 'SCRIPT' && node.nodeName !== 'STYLE') {
                Array.from(node.childNodes).forEach(walk);
            }
        }
        
        Array.from(tempDiv.childNodes).forEach(walk);
        sourceMap.innerHTML = tempDiv.innerHTML; // Update DOM
        
        // Update Exploration HUD
        const pct = totalConcepts > 0 ? Math.round((capturedConcepts / totalConcepts) * 100) : 0;
        const pctEl = document.getElementById('exploration-pct');
        if (pctEl) {
            pctEl.innerText = `🗺️ Map Explored: ${pct}%`;
            if (pct >= 80) pctEl.style.borderColor = '#198754';
            else if (pct >= 50) pctEl.style.borderColor = '#fd7e14';
            else pctEl.style.borderColor = 'rgba(111, 66, 193, 0.25)';
        }
    }
    
    function attachSyncScroll() {
        const leftPane = document.querySelector('.sync-scroll-left');
        let rightPane = document.querySelector('.sync-scroll-right .CodeMirror-scroll');
        if (!rightPane) rightPane = document.querySelector('.sync-scroll-right textarea');

        if (!leftPane || !rightPane) return;
        if (leftPane.dataset.syncAttached === 'true' && rightPane.dataset.syncAttached === 'true') return; 
        
        leftPane.dataset.syncAttached = 'true';
        rightPane.dataset.syncAttached = 'true';

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
        // --- MUTATION OBSERVER FOR DYNAMIC UI ---
        const observer = new MutationObserver((mutations) => {
            attachSyncScroll();
            
            const readTextArea = document.getElementById('read_note_main');
            if (readTextArea && (!window.easymde_read_editor || !document.body.contains(window.easymde_read_editor.element))) {
                
                window.originalSourceHTML = null; // Clear cached DOM on fresh load
                
                window.easymde_read_editor = new EasyMDE({ 
                    element: readTextArea, spellChecker: false, status: false,
                    renderingConfig: { codeSyntaxHighlighting: true },
                    toolbar: ["bold", "italic", "heading", "|", "quote", "code", "unordered-list", "ordered-list", "|", "link", "image", "|", "preview", "guide"]
                });
                
                let readTimeout = null;
                window.easymde_read_editor.codemirror.on("change", function() {
                    const content = window.easymde_read_editor.value();
                    clearTimeout(readTimeout);
                    readTimeout = setTimeout(function() {
                        Shiny.setInputValue('read_note_main', content); 
                    }, 300); 
                    
                    updateFogOfWar(content); // Run Semantic Mapping Live
                    
                    const counterEl = document.getElementById('loot-counter');
                    if (counterEl) {
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
                });

                window.easymde_read_editor.codemirror.on("paste", function(editor, e) {
                    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
                    for (let index in items) {
                        const item = items[index];
                        if (item.kind === 'file') {
                            const blob = item.getAsFile();
                            const reader = new FileReader();
                            reader.onload = function(event) {
                                Shiny.setInputValue('pasted_read_image_data', event.target.result);
                                Shiny.setInputValue('pasted_read_image_target', 'read_note_main');
                                Shiny.setInputValue('pasted_read_image_trigger', Math.random());
                            };
                            reader.readAsDataURL(blob);
                            e.preventDefault(); 
                        }
                    }
                });
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    });

    Shiny.addCustomMessageHandler('insert_at_cursor', function(payload) {
        let cm = null;
        let editor = null;
        if (payload.target === 'read_note_main' && window.easymde_read_editor) {
            editor = window.easymde_read_editor; cm = editor.codemirror;
        }
        if (cm) {
            const doc = cm.getDoc();
            const cursor = doc.getCursor();
            doc.replaceRange(payload.text, cursor);
            if (payload.text.includes('![') && editor && !editor.isPreviewActive()) {
                editor.togglePreview();
            }
            return;
        }
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
                        { label: 'Retrieval (Blurt)', data: payload.d_retrieval, backgroundColor: '#198754' },
                        { label: 'Encoding (Reading)', data: payload.d_encoding, backgroundColor: '#0dcaf0' }
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
                        { label: 'Retrieval (Blurt)', data: payload.w_retrieval, backgroundColor: '#198754' },
                        { label: 'Encoding (Reading)', data: payload.w_encoding, backgroundColor: '#0dcaf0' }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { x: { stacked: true }, y: { stacked: true, title: { display: true, text: 'Minutes' } } } }
            });
        }
    });
</script>
"""

# --- NLP DEPENDENCIES ---
def extract_source_chunks(text: str, sentences_per_chunk: int = 2) -> list[dict]:
    """Split source into overlapping semantic chunks with metadata."""
    raw = re.split(r'(?<=[.!?\n])\s+', text)
    sentences = [s.strip() for s in raw if len(s.strip()) > 15]
    
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        window = sentences[i : i + sentences_per_chunk + 1]  # +1 overlap
        chunk_text = '\n'.join(window)
        chunks.append({
            "text": chunk_text,
            "start_sentence": i,
            "idx": len(chunks)
        })
    return chunks

def extract_qa_blocks(markdown_text: str) -> dict:
    """Isolates specific Question & Answer blocks based on markdown headers."""
    blocks = {}
    current_q = "General Concepts"
    current_a = []
    has_headers = False
    
    for line in markdown_text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('#'):
            has_headers = True
            if current_a:
                blocks[current_q] = '\n'.join(current_a).strip()
            current_q = stripped.lstrip('#').strip()
            current_a = []
        else:
            current_a.append(line)
            
    if current_a:
        blocks[current_q] = '\n'.join(current_a).strip()
        
    # Remove dummy header if explicit # headers were used
    if has_headers and "General Concepts" in blocks and not blocks["General Concepts"].strip():
        del blocks["General Concepts"]
        
    return blocks

def extract_pdf_chunks(pdf_path: str) -> list[dict]:
    """Extract semantic chunks from PDF, retaining page number."""
    if fitz is None: return []
    doc = fitz.open(pdf_path)
    all_chunks = []
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")
        for block in blocks:
            text = block[4].strip()
            if len(text) < 40 or block[6] != 0: 
                continue
            all_chunks.append({
                "text": text,
                "page": page_num + 1,        
                "bbox": block[:4],           
                "idx": len(all_chunks)
            })
    
    doc.close()
    return all_chunks

def compute_semantic_coverage(
    source_chunks: list[dict],
    note_text: str,
    covered_threshold: float = 0.78,
    partial_threshold: float = 0.68
) -> tuple[float, list[dict]]:
    """
    Strict Soft-margin semantic coverage with Context Windows.
    Returns (coverage_pct, annotated_chunks)
    """
    if not source_chunks or not note_text.strip() or SEMANTIC_MODEL is None:
        return 0.0, source_chunks
    
    # 1. The Gibberish Gatekeeper
    word_count = len(re.findall(r'\b[a-zA-Z]{3,}\b', note_text))
    if word_count < 5:
        annotated = [{**chunk, "coverage_score": 0.0, "status": "missing"} for chunk in source_chunks]
        return 0.0, annotated
    
    # 2. Encode Source Text
    source_texts = [c["text"] for c in source_chunks]
    source_embs = SEMANTIC_MODEL.encode(source_texts, convert_to_tensor=True, normalize_embeddings=True)
    
    # 3. Contextual Note Chunking
    raw_note_sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', note_text) if len(s.split()) > 3]
    if not raw_note_sentences:
        raw_note_sentences = [note_text]
        
    note_chunks = []
    for i in range(len(raw_note_sentences)):
        window = raw_note_sentences[i : i + 2] 
        note_chunks.append(' '.join(window))
        
    note_embs = SEMANTIC_MODEL.encode(note_chunks, convert_to_tensor=True, normalize_embeddings=True)
    
    # 4. Compare and Score
    sim_matrix = util.cos_sim(source_embs, note_embs)
    best_scores = sim_matrix.max(dim=1).values.tolist()
    
    annotated = []
    covered_weight = 0.0
    total_weight = len(source_chunks)
    
    for chunk, score in zip(source_chunks, best_scores):
        if score >= covered_threshold:
            status = 'covered'
            covered_weight += 1.0
        elif score >= partial_threshold:
            status = 'partial'
            covered_weight += 0.4   # Nerfed to heavily penalize weak matches
        else:
            status = 'missing'
        
        annotated.append({**chunk, "coverage_score": round(score, 3), "status": status})
    
    pct = (covered_weight / total_weight) if total_weight > 0 else 0.0
    return round(pct, 3), annotated

def compute_blurt_coverage(
    orig_text: str,
    blurt_text: str,
    covered_threshold: float = 0.82,  # Ultra-strict threshold for active recall
    partial_threshold: float = 0.72
) -> tuple[float, list[dict]]:
    """
    Direct Answer-to-Answer comparison. Isolates each question block to prevent semantic cross-pollination.
    """
    if not orig_text.strip() or SEMANTIC_MODEL is None:
        return 0.0, []

    orig_qa = extract_qa_blocks(orig_text)
    blurt_qa = extract_qa_blocks(blurt_text)

    all_annotated = []
    total_weight = 0.0
    covered_weight = 0.0

    for q, orig_ans in orig_qa.items():
        # Inject the header explicitly for UI rendering
        all_annotated.append({"text": f"### {q}", "status": "header", "coverage_score": 1.0})

        user_ans = blurt_qa.get(q, "")
        
        source_chunks = extract_source_chunks(orig_ans)
        if not source_chunks:
            continue
            
        word_count = len(re.findall(r'\b[a-zA-Z]{3,}\b', user_ans))
        is_gibberish = word_count < 3

        if is_gibberish:
            for chunk in source_chunks:
                all_annotated.append({**chunk, "coverage_score": 0.0, "status": "missing"})
                total_weight += 1.0
            continue

        # Encode isolated Source chunks
        source_texts = [c["text"] for c in source_chunks]
        source_embs = SEMANTIC_MODEL.encode(source_texts, convert_to_tensor=True, normalize_embeddings=True)

        # Encode isolated User chunks
        raw_note_sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', user_ans) if len(s.split()) > 3]
        if not raw_note_sentences:
            raw_note_sentences = [user_ans]

        note_chunks = []
        for i in range(len(raw_note_sentences)):
            window = raw_note_sentences[i : i + 2] 
            note_chunks.append(' '.join(window))

        note_embs = SEMANTIC_MODEL.encode(note_chunks, convert_to_tensor=True, normalize_embeddings=True)

        # Strictly compare ONLY within this Q&A block
        sim_matrix = util.cos_sim(source_embs, note_embs)
        best_scores = sim_matrix.max(dim=1).values.tolist()

        for chunk, score in zip(source_chunks, best_scores):
            total_weight += 1.0
            if score >= covered_threshold:
                status = 'covered'
                covered_weight += 1.0
            elif score >= partial_threshold:
                status = 'partial'
                covered_weight += 0.4
            else:
                status = 'missing'

            all_annotated.append({**chunk, "coverage_score": round(score, 3), "status": status})

    pct = (covered_weight / total_weight) if total_weight > 0 else 0.0
    return round(pct, 3), all_annotated

def render_fog_of_war_html(annotated_chunks: list[dict]) -> str:
    """Renders source text with coverage overlays."""
    if not annotated_chunks:
        return ""
    
    parts = []
    for chunk in annotated_chunks:
        text = chunk["text"].replace('\n', '<br>')
        status = chunk.get("status", "missing")
        score = chunk.get("coverage_score", 0)
        
        if status == "header":
            parts.append(f'<div style="margin-top: 20px; margin-bottom: 10px; font-weight: 800; font-size: 1.2em; color: #2c3e50; border-bottom: 2px solid #dee2e6; padding-bottom: 5px;">{chunk["text"]}</div>')
            continue
            
        if status == "covered":
            style = "background: rgba(25,135,84,0.12); border-left: 3px solid #198754; opacity: 1.0;"
            icon = "✅"
        elif status == "partial":
            style = "background: rgba(253,126,20,0.12); border-left: 3px solid #fd7e14; opacity: 0.85;"
            icon = "🟡"
        else:
            style = "background: rgba(108,117,125,0.08); border-left: 3px solid #dee2e6; opacity: 0.55; filter: grayscale(0.3);"
            icon = "⬜"
        
        tooltip = f"Coverage score: {score:.0%}"
        parts.append(
            f'<div style="padding: 8px 12px; margin-bottom: 6px; border-radius: 4px; {style}" '
            f'title="{tooltip}" class="fog-chunk fog-{status}">'
            f'<span style="font-size:0.7em; float:right; opacity:0.6">{icon} {score:.0%}</span>'
            f'{text}'
            f'</div>'
        )
    
    return "".join(parts)


# --- HELPERS ---
def load_revisions():
    if os.path.exists(REV_LOG):
        try: 
            df = pd.read_csv(REV_LOG)
            if "Activity" not in df.columns:
                df["Activity"] = "Reading"
            return df
        except: pass
    return pd.DataFrame(columns=["Module", "Map", "Date", "Duration (min)", "Activity"])

def load_user_stats():
    """Loads gamification profile (XP, Daily Login Streak, Quests)"""
    stats = {"Total_XP": 0, "Daily_Streak": 0, "Last_Active": "", "Completed_Quests": "", "Quest_Date": ""}
    if os.path.exists(STATS_LOG):
        try:
            df = pd.read_csv(STATS_LOG)
            if len(df) > 0: 
                row = df.iloc[0].to_dict()
                for k, v in row.items():
                    if pd.notna(v): stats[k] = v
        except: pass
    return stats

def save_user_stats(stats_dict):
    pd.DataFrame([stats_dict]).to_csv(STATS_LOG, index=False)

def get_module_names():
    if not os.path.exists(BASE_PATH): return ["General"]
    mods = [d for d in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, d))]
    mods = [m for m in mods if m != ".temp_session" and m != "pdf_cache"]
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
            ui.output_ui("scholar_profile_ui"),
            ui.output_ui("quest_board_ui"),
            col_widths=(6, 6)
        ),
        ui.br(),
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

    ui.nav_panel("Reading Room",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### **1. Import Material**"),
                ui.input_select("read_mod", "Select Module", get_module_names()),
                ui.input_action_button("open_add_mod_modal_read", "➕ New Module", class_="btn-outline-secondary btn-sm w-100 mb-2"),
                ui.input_file("upload_pdf", "Upload PDF Textbook", accept=[".pdf"], multiple=False),
                ui.input_text_area("read_source", "Or Paste Textbook/Source Text", height="150px", placeholder="Paste your text or LaTeX here..."),
                ui.input_action_button("process_read_btn", "Load Reading View 📖", class_="btn-primary w-100 mb-2"),
                ui.hr(),
                ui.markdown("### **2. Export Notes**"),
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

    ui.nav_panel("Blurt Studio",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### **Active Recall**"),
                ui.input_select("blurt_mod_select", "Select Module", get_module_names()),
                ui.input_action_button("open_add_mod_modal_blurt", "➕ New Module", class_="btn-outline-secondary btn-sm w-100 mb-2"),
                ui.output_ui("blurt_map_loader_ui"),
                ui.input_action_button("start_blurt_btn", "Generate Template & Start Timer", class_="btn-primary w-100"),
                ui.hr(),
                ui.input_action_button("review_blurt_btn", "Submit, Review & Log Time", class_="btn-success w-100"),
                ui.input_action_button("reset_blurt_btn", "Reset Session", class_="btn-danger w-100 mt-2")
            ),
            ui.card(ui.output_ui("blurt_main_area_ui"))
        )
    ),
    
    title="OptiSystem (Workspace Edition)",
    id="main_nav",
    header=ui.output_ui("gamification_hud") 
)

# --- SERVER ---
def server(input, output, session):
    refresh_trigger = reactive.Value(0)
    user_stats_reactive = reactive.Value(load_user_stats())
    
    read_state = reactive.Value({"mode": None, "data": None, "ts": 0})
    read_source_chunks = reactive.Value([])
    read_coverage_data = reactive.Value([])
    read_coverage_pct = reactive.Value(0.0)
    read_start_time = reactive.Value(0.0)

    # Blurt Studio Session States
    blurt_state = reactive.Value("setup") 
    blurt_original = reactive.Value("")
    blurt_template = reactive.Value("")
    blurt_start_time = reactive.Value(0.0)
    blurt_active_mod = reactive.Value("")
    blurt_active_map = reactive.Value("")
    blurt_coverage_data = reactive.Value([])
    blurt_coverage_pct = reactive.Value(0.0)

    # ==========================
    # MODULE MANAGEMENT MODAL
    # ==========================
    @reactive.Effect
    @reactive.event(input.open_add_mod_modal_read, input.open_add_mod_modal_blurt)
    def _show_add_mod_modal():
        m = ui.modal(
            ui.input_text("new_mod_name", "Enter new module name:", width="100%"),
            title="Create New Module",
            footer=ui.div(
                ui.input_action_button("cancel_add_mod", "Cancel", class_="btn-secondary"),
                ui.input_action_button("confirm_add_mod", "Create", class_="btn-primary")
            )
        )
        ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.cancel_add_mod)
    def _cancel_mod():
        ui.modal_remove()

    @reactive.Effect
    @reactive.event(input.confirm_add_mod)
    def _create_mod():
        name = input.new_mod_name().strip().replace(" ", "_")
        if name:
            os.makedirs(os.path.join(BASE_PATH, name), exist_ok=True)
            mods = get_module_names()
            # Update all module dropdowns to include the new option and select it
            ui.update_select("read_mod", choices=mods, selected=name)
            ui.update_select("blurt_mod_select", choices=mods, selected=name)
            ui.notification_show(f"Module '{name}' created!", type="message")
            refresh_trigger.set(refresh_trigger() + 1)
        else:
            ui.notification_show("Invalid module name.", type="warning")
        ui.modal_remove()

    # ==========================
    # GAMIFICATION ENGINE (XP, STREAKS, QUESTS)
    # ==========================
    def grant_xp(amount):
        """Grants XP, calculates levels, and maintains the daily login streak"""
        stats = user_stats_reactive()
        today = datetime.now().date()
        last_active = stats.get("Last_Active", "")
        
        current_streak = stats.get("Daily_Streak", 0)
        if last_active:
            last_date = datetime.strptime(last_active, "%Y-%m-%d").date()
            delta = (today - last_date).days
            if delta == 1:
                current_streak += 1
            elif delta > 1:
                current_streak = 1
        else:
            current_streak = 1
            
        old_xp = int(stats.get("Total_XP", 0))
        new_xp = old_xp + amount
        
        old_level = int((old_xp / 100) ** 0.5) + 1
        new_level = int((new_xp / 100) ** 0.5) + 1
        
        stats["Total_XP"] = new_xp
        stats["Daily_Streak"] = current_streak
        stats["Last_Active"] = str(today)
        
        save_user_stats(stats)
        user_stats_reactive.set(stats)
        
        if new_level > old_level:
            ui.notification_show(f"🎉 LEVEL UP! You are now a Level {new_level} Scholar!", type="message", duration=5)
            
        return new_xp, current_streak
        
    def check_quest_completion(activity, duration=0.0, accuracy=0.0, cards=0):
        """Evaluates ongoing activity against the 3 daily quests"""
        stats = user_stats_reactive()
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        if stats.get("Quest_Date") != today_str:
            stats["Completed_Quests"] = ""
            stats["Quest_Date"] = today_str
            
        completed_ids = stats.get("Completed_Quests", "").split(",") if stats.get("Completed_Quests") else []
        daily_quests = get_daily_quests()
        
        newly_completed = False
        for q in daily_quests:
            if q['id'] not in completed_ids:
                is_done = False
                if q['type'] == 'activity' and activity == q['activity']: is_done = True
                elif q['type'] == 'duration' and (activity == q['activity'] or q['activity'] == 'any') and duration >= q['target']: is_done = True
                elif q['type'] == 'accuracy' and activity == q['activity'] and accuracy >= q['target']: is_done = True
                elif q['type'] == 'cards' and activity == q['activity'] and cards >= q['target']: is_done = True
                
                if is_done:
                    completed_ids.append(q['id'])
                    grant_xp(q['xp'])
                    ui.notification_show(f"📋 QUEST COMPLETE: {q['desc']}! +{q['xp']} XP 🌟", type="message", duration=6)
                    newly_completed = True
        
        if newly_completed:
            stats["Completed_Quests"] = ",".join(completed_ids)
            save_user_stats(stats)
            user_stats_reactive.set(stats)

    @output
    @render.ui
    def gamification_hud():
        stats = user_stats_reactive()
        xp = int(stats.get("Total_XP", 0))
        streak = int(stats.get("Daily_Streak", 0))
        level = int((xp / 100) ** 0.5) + 1
        
        return ui.div(
            ui.div(
                "⏱️ Session: ",
                ui.tags.span("00:00", id="session-timer-display", style=(
                    "font-variant-numeric: tabular-nums; font-weight: 900; "
                    "color: #0d6efd; min-width: 52px; display: inline-block;"
                )),
                class_="hud-item",
                style="border-right: 1px solid #dee2e6; padding-right: 12px; font-size: 0.9em;"
            ),
            ui.div(f"🔥 {streak} Day Streak", class_="hud-item hud-streak"),
            ui.div(
                ui.span(f"🌟 Lvl {level}", class_="hud-level"),
                ui.span(f"{xp} XP", class_="hud-xp"),
                class_="hud-item"
            ),
            class_="gamification-hud"
        )

    @output
    @render.ui
    def scholar_profile_ui():
        stats = user_stats_reactive()
        xp = int(stats.get("Total_XP", 0))
        streak = int(stats.get("Daily_Streak", 0))
        level = int((xp / 100) ** 0.5) + 1
        
        current_level_base_xp = (level - 1) ** 2 * 100
        next_level_base_xp = (level) ** 2 * 100
        xp_needed = next_level_base_xp - current_level_base_xp
        xp_gained_this_level = xp - current_level_base_xp
        progress_pct = int((xp_gained_this_level / xp_needed) * 100) if xp_needed > 0 else 0
        
        return ui.card(
            ui.div(
                ui.h2(f"Level {level} Scholar", style="color: #6f42c1; font-weight: 800; margin-bottom: 5px;"),
                ui.p(f"🔥 {streak} Day Active Learning Streak", style="color: #ff8c00; font-size: 1.1em; font-weight: 600; margin-bottom: 15px;"),
                ui.div(
                    ui.div(class_="progress-bar bg-success", style=f"width: {progress_pct}%"), 
                    class_="progress", style="height: 12px; border-radius: 10px; margin-bottom: 8px;"
                ),
                ui.p(f"{xp_gained_this_level} / {xp_needed} XP to Level {level + 1}", style="font-size: 0.85em; color: gray; text-align: right; margin: 0;")
            ),
            style="border-left: 5px solid #6f42c1; background: #faf8fc;"
        )

    @output
    @render.ui
    def quest_board_ui():
        stats = user_stats_reactive()
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        completed = stats.get("Completed_Quests", "").split(",") if stats.get("Quest_Date") == today_str and stats.get("Completed_Quests") else []
        quests = get_daily_quests()
        quest_html = []
        for q in quests:
            is_done = q['id'] in completed
            icon = "✅" if is_done else "⬜"
            color = "text-success text-decoration-line-through" if is_done else "text-dark"
            quest_html.append(
                ui.div(
                    ui.span(icon, class_="me-2"),
                    ui.span(q['desc'], class_=color, style="font-weight: 500;"),
                    ui.span(f"+{q['xp']} XP", class_="badge bg-success" if is_done else "badge bg-secondary", style="float: right;"),
                    class_="mb-2 p-2 border rounded shadow-sm bg-white"
                )
            )
            
        return ui.card(
            ui.card_header(ui.tags.b("📋 Daily Quests")),
            ui.p("Complete these before midnight to earn massive XP bonuses!", class_="text-muted", style="font-size: 0.85em;"),
            ui.div(*quest_html),
            style="background: #f8f9fa;"
        )

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
            val = df[(df['Date_Only'] == today) & (df['Activity'] == "Reading")]['Duration (min)'].sum()
        return ui.HTML(f"<div class='kpi-title'>Encoding Today (Reading)</div><div class='kpi-val encoding'>{val:.1f} <span style='font-size:0.5em'>min</span></div>")

    @output
    @render.ui
    def kpi_retrieval_ui():
        refresh_trigger()
        df = get_processed_rev_df()
        val = 0.0
        if not df.empty:
            today = datetime.now().date()
            val = df[(df['Date_Only'] == today) & (df['Activity'] == "Blurt")]['Duration (min)'].sum()
        return ui.HTML(f"<div class='kpi-title'>Retrieval Today (Blurt)</div><div class='kpi-val retrieval'>{val:.1f} <span style='font-size:0.5em'>min</span></div>")

    @output
    @render.ui
    def kpi_ratio_ui():
        refresh_trigger()
        df = get_processed_rev_df()
        if df.empty: return ui.HTML(f"<div class='kpi-title'>Weekly Recall Ratio</div><div class='kpi-val'>0%</div>")
        
        current_yw = f"{datetime.now().isocalendar()[0]}-W{str(datetime.now().isocalendar()[1]).zfill(2)}"
        week_df = df[df['YearWeek'] == current_yw]
        enc = week_df[week_df['Activity'] == "Reading"]['Duration (min)'].sum()
        ret = week_df[week_df['Activity'] == "Blurt"]['Duration (min)'].sum()
        
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
        for col in ['Reading', 'Blurt']:
            if col not in daily: daily[col] = 0
            
        weekly = df.groupby(['YearWeek', 'Activity'])['Duration (min)'].sum().unstack(fill_value=0)
        for col in ['Reading', 'Blurt']:
            if col not in weekly: weekly[col] = 0
            
        payload = {
            "d_labels": [d.strftime("%b %d") for d in daily.index],
            "d_encoding": daily['Reading'].tolist(),
            "d_retrieval": daily['Blurt'].tolist(),
            "w_labels": list(weekly.index),
            "w_encoding": weekly['Reading'].tolist(),
            "w_retrieval": weekly['Blurt'].tolist()
        }
        await session.send_custom_message("update_dashboard_charts", payload)

    # ==========================
    # READING ROOM LOGIC
    # ==========================
    @reactive.Effect
    @reactive.event(input.process_read_btn)
    def _process_reading():
        pdf_info = input.upload_pdf()
        text_source = input.read_source()
        
        # Reset semantic coverage
        read_source_chunks.set([])
        read_coverage_data.set([])
        read_coverage_pct.set(0.0)
        read_start_time.set(time.time())

        if pdf_info:
            try:
                pdf_path = pdf_info[0]["datapath"]
                original_name = pdf_info[0]["name"]
                
                cache_dir = os.path.join(BASE_PATH, "pdf_cache")
                os.makedirs(cache_dir, exist_ok=True)
                
                safe_name = re.sub(r'[^A-Za-z0-9_.-]', '_', original_name)
                dest_path = os.path.join(cache_dir, safe_name)
                
                shutil.copy(pdf_path, dest_path)
                
                ts = int(time.time())
                pdf_url = f"/files/pdf_cache/{safe_name}?v={ts}"
                
                chunks = extract_pdf_chunks(dest_path)
                read_source_chunks.set(chunks)
                read_coverage_data.set(chunks)
                
                read_state.set({
                    "mode": "pdf", 
                    "data": pdf_url,
                    "ts": ts
                })
                ui.notification_show("PDF loaded successfully!", type="message")
            except Exception as e:
                ui.notification_show(f"Failed to load PDF: {str(e)}", type="error")
                
        elif text_source and text_source.strip():
            chunks = extract_source_chunks(text_source)
            read_source_chunks.set(chunks)
            read_coverage_data.set(chunks)
            
            read_state.set({"mode": "text", "data": text_source, "ts": int(time.time())})
            ui.notification_show("Loaded text for aligned reading.", type="message")
            
        else:
            ui.notification_show("Please upload a PDF or paste text/LaTeX first.", type="warning")

    @reactive.Effect
    @reactive.event(input.read_note_main)
    async def _recompute_coverage():
        note = input.read_note_main()
        chunks = read_source_chunks()
        if not chunks or not note:
            read_coverage_pct.set(0.0)
            return

        def compute():
            if SEMANTIC_MODEL is None:
                return 0.0, chunks
            return compute_semantic_coverage(chunks, note)

        pct, annotated = await asyncio.to_thread(compute)
        read_coverage_data.set(annotated)
        read_coverage_pct.set(pct)

    @output
    @render.ui
    def coverage_hud_ui():
        pct = read_coverage_pct()
        pct_int = int(pct * 100)
        
        color = "#198754" if pct >= 0.80 else "#fd7e14" if pct >= 0.50 else "#dc3545"
        label = "🗺️ Fully Mapped!" if pct >= 0.80 else "🔍 Exploring..." if pct >= 0.50 else "🌫️ Mostly Unexplored"
        
        return ui.div(
            ui.div(
                ui.span(f"{pct_int}%", style=f"font-size:1.5em; font-weight:900; color:{color};"),
                ui.span(" Conceptual Coverage", style="font-size:0.85em; color:gray; margin-left:6px;"),
                style="margin-bottom: 6px;"
            ),
            ui.div(
                ui.div(
                    class_="progress-bar",
                    style=f"width:{pct_int}%; background:{color}; transition: width 0.8s ease;"
                ),
                class_="progress", style="height: 10px; border-radius: 5px; background: rgba(0,0,0,0.05);"
            ),
            ui.p(label, style="font-size:0.8em; color:gray; margin-top:4px; margin-bottom:0; font-weight: bold;"),
            style="padding: 12px; background:#f8f9fa; border-radius:8px; border: 1px solid #dee2e6; margin-bottom:10px; width: 100%;"
        )

    @output
    @render.ui
    def missing_concepts_ui():
        annotated = read_coverage_data()
        if not annotated: return ui.div()
        missing = [c for c in annotated if c.get("status", "missing") == "missing"]
        
        if not missing:
            return ui.div(ui.p("✅ All key concepts captured!", style="color:#198754; font-weight:bold; padding: 15px;"))
        
        items = []
        for chunk in missing[:8]:
            page_info = f"p.{chunk['page']}" if "page" in chunk else ""
            items.append(
                ui.div(
                    ui.span(page_info, class_="badge bg-secondary me-2") if page_info else ui.span(),
                    ui.span(chunk["text"][:120] + "...", style="font-size:0.85em; color:#495057;"),
                    style="padding: 8px; margin-bottom: 6px; background:#fff3cd; border-radius:4px; border-left: 3px solid #ffc107;"
                )
            )
        
        return ui.div(
            ui.p(f"⬜ {len(missing)} concepts not yet captured:", style="font-weight:bold; color:#dc3545; margin-top: 15px; margin-bottom: 10px;"),
            *items,
            style="padding: 15px; border-top: 2px dashed #dee2e6;"
        )

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
                        ui.tags.embed(
                            src=state["data"], 
                            type="application/pdf", 
                            width="100%", 
                            height="800px", 
                            style="border-radius: 5px;"
                        ),
                        ui.output_ui("missing_concepts_ui"),
                        class_="reading-source-pane", style="padding: 0; overflow: hidden; height: 800px; overflow-y: auto;"
                    ),
                    ui.div(
                        ui.output_ui("coverage_hud_ui"),
                        ui.div(
                            ui.span("Flashcards Captured: 0 💎", id="loot-counter", **{"data-count": "0"}), 
                            style="margin-bottom: 10px; display: flex; justify-content: flex-end; gap: 12px; align-items: center; font-weight: bold;"
                        ),
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
            annotated_html = render_fog_of_war_html(read_coverage_data())
            if not annotated_html:
                annotated_html = ui.markdown(protect_math(state["data"]))
            else:
                annotated_html = ui.HTML(annotated_html)
                
            return ui.div(
                ui.layout_columns(
                    ui.div(
                        annotated_html, 
                        class_="reading-source-pane sync-scroll-left", 
                        style="height: 800px; overflow-y: auto;"
                    ),
                    ui.div(
                        ui.output_ui("coverage_hud_ui"),
                        ui.div(
                            ui.span("Flashcards Captured: 0 💎", id="loot-counter", **{"data-count": "0"}), 
                            style="margin-bottom: 10px; display: flex; justify-content: flex-end; gap: 12px; align-items: center; font-weight: bold;"
                        ),
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
            
        # Logging & Quests
        duration = round((time.time() - read_start_time()) / 60, 2) if read_start_time() > 0 else 0
        df = load_revisions()
        new_row = pd.DataFrame({
            "Module": [input.read_mod()], 
            "Map": [filename], 
            "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], 
            "Duration (min)": [duration], 
            "Activity": ["Reading"]
        })
        pd.concat([df, new_row], ignore_index=True).to_csv(REV_LOG, index=False)
            
        grant_xp(50)
        check_quest_completion("Reading", duration=duration)
            
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show(f"Successfully exported {filename}! +50 XP 🌟", type="message")


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
        
        blurt_active_mod.set(input.blurt_mod_select())
        blurt_active_map.set(input.blurt_selected_map())
        
        path = os.path.join(BASE_PATH, input.blurt_mod_select(), input.blurt_selected_map())
        with open(path, "r") as f: content = f.read()
        blurt_original.set(content)
        template = "".join([f"{line}\n\n\n" for line in content.split('\n') if line.strip().startswith('#')])
        blurt_template.set(template)
        blurt_state.set("blurting")
        blurt_start_time.set(time.time())

    @reactive.Effect
    @reactive.event(input.review_blurt_btn)
    async def _review_blurt():
        if blurt_state() == "blurting":
            blurt_state.set("review")
            duration = round((time.time() - blurt_start_time()) / 60, 2)
            
            orig_text = blurt_original()
            blurt_text = input.blurt_input()
            
            def compute():
                if SEMANTIC_MODEL is None:
                    return 0.0, []
                # Pass directly to the new isolated Q&A evaluator
                return compute_blurt_coverage(orig_text, blurt_text)

            pct, annotated = await asyncio.to_thread(compute)
            blurt_coverage_pct.set(pct)
            blurt_coverage_data.set(annotated)
            
            score_pct = int(pct * 100)
            
            df = load_revisions()
            new_row = pd.DataFrame({
                "Module": [blurt_active_mod()], 
                "Map": [blurt_active_map()], 
                "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], 
                "Duration (min)": [duration], 
                "Activity": ["Blurt"]
            })
            pd.concat([df, new_row], ignore_index=True).to_csv(REV_LOG, index=False)
            
            # --- SEMANTIC ANALYSIS & SCALED REWARDS ---
            base_xp = 100

            if score_pct >= 90:
                grant_xp(base_xp + 150)
                ui.notification_show(f"Flawless Synthesis! {score_pct}% Core Concepts Captured. +250 XP 🧠🌟", type="message")
            elif score_pct >= 70:
                grant_xp(base_xp + 50)
                ui.notification_show(f"Great Blurt! {score_pct}% Core Concepts Captured. +150 XP 🧠", type="message")
            else:
                grant_xp(base_xp)
                ui.notification_show(f"Blurt Complete! {score_pct}% Coverage. Keep practicing! +100 XP", type="message")
            
            check_quest_completion("Blurt", duration=duration, accuracy=pct)
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
            
            score_pct = int(blurt_coverage_pct() * 100)
            
            annotated_orig_html = render_fog_of_war_html(blurt_coverage_data())
            if not annotated_orig_html:
                annotated_orig_html = protect_math(blurt_original())
                
            score_color = '#198754' if score_pct >= 80 else '#fd7e14' if score_pct >= 50 else '#dc3545'
            
            return ui.div(
                ui.div(
                    ui.h3("🧠 Semantic Analysis", class_="text-center mb-3", style="font-weight: 800;"),
                    ui.layout_columns(
                        ui.div(ui.tags.b("🎯 Semantic Coverage:"), ui.h3(f"{score_pct}%", style=f"font-weight: 900; color: {score_color}; margin-bottom: 0;"), class_="p-3 border rounded bg-white shadow-sm text-center"),
                        col_widths=(12,)
                    ),
                    class_="mb-4 p-4 card shadow-sm", style="background: #f8f9fa;"
                ),
                ui.layout_columns(
                    ui.card(ui.card_header("✍️ Your Blurt"), ui.div(ui.markdown(blurt_in_val), class_="blurt-review-panel")),
                    ui.card(ui.card_header("🧠 Semantic Evaluation (Original)"), ui.div(ui.HTML(annotated_orig_html), class_="blurt-review-panel")),
                    col_widths=(6, 6)
                )
            )

app = App(app_ui, server, static_assets={"/files": BASE_PATH})