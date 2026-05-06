import os
import pandas as pd
import base64
import time
import re
import random
import difflib
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
TASK_LOG = os.path.join(BASE_PATH, "master_tasks.csv")
REV_LOG = os.path.join(BASE_PATH, "revision_log.csv")
NODE_LOG = os.path.join(BASE_PATH, "node_mastery.csv") 
STATS_LOG = os.path.join(BASE_PATH, "user_stats.csv") 

if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

# --- GAMIFICATION QUEST POOL ---
QUEST_POOL = [
    {"id": "q_30min_lab",  "desc": "Study for 30 mins in Study Lab", "xp": 300, "type": "duration", "target": 30, "activity": "Study Lab"},
    {"id": "q_blurt",      "desc": "Complete a Blurt session",       "xp": 250, "type": "activity", "target": 1,  "activity": "Blurt"},
    {"id": "q_accuracy80", "desc": "Achieve 80%+ accuracy in Rev.",  "xp": 400, "type": "accuracy", "target": 0.80,"activity": "Revision"},
    {"id": "q_15min_any",  "desc": "Study for 15+ mins in one go",   "xp": 150, "type": "duration", "target": 15, "activity": "any"},
    {"id": "q_rev_cards",  "desc": "Review 10+ flashcards",          "xp": 200, "type": "cards",    "target": 10, "activity": "Revision"},
    {"id": "q_quick_rev",  "desc": "Complete a Revision Session",    "xp": 150, "type": "activity", "target": 1,  "activity": "Revision"}
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
    
    /* Hide raw textarea under EasyMDE */
    #map_content { display: none !important; }
    #read_note_main { display: none !important; }
    
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
    
    /* Wild Encounter RPG Animations */
    @keyframes popInRPG {
        0% { transform: scale(0.8); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
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
    // --- KEYBOARD SHORTCUTS FOR FLASHCARDS ---
    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
            return;
        }
        if (e.code === 'Space') {
            const revealBtn = document.getElementById('reveal_ans_btn');
            if (revealBtn) { e.preventDefault(); revealBtn.click(); }
        } else if (e.code === 'ArrowLeft') {
            const failBtn = document.getElementById('btn_hard_left');
            if (failBtn) { e.preventDefault(); failBtn.click(); }
        } else if (e.code === 'ArrowRight') {
            const passBtn = document.getElementById('btn_hard_right');
            if (passBtn) { e.preventDefault(); passBtn.click(); }
        }
    });

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
                    animation: popInRPG 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
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
                    <button
                        id="escape-valve-btn"
                        style="
                            background: transparent;
                            color: #dc3545;
                            border: 2px solid #dc3545;
                            padding: 12px 20px;
                            border-radius: 10px;
                            font-size: 1em;
                            font-weight: 700;
                            cursor: pointer;
                            width: 100%;
                            margin-top: 12px;
                            transition: all 0.2s;
                        "
                        onmouseover="this.style.background='rgba(220,53,69,0.08)'"
                        onmouseout="this.style.background='transparent'"
                        onclick="triggerEscapeValve()"
                    >
                        Brain Fried? 3-Min Flashcard Cool-Down 🧠
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
    
    function triggerEscapeValve() {
        dismissIdle();
        Shiny.setInputValue('escape_valve_triggered', Math.random(), {priority: 'event'});
    }

    function showIdleOverlay() {
        if (window.idleWarningActive) return;
        window.idleWarningActive = true;
        // Track the drop in engagement
        window.idleTriggers = (window.idleTriggers || 0) + 1;
        Shiny.setInputValue('current_idle_triggers', window.idleTriggers);
        
        const overlay = document.getElementById('idle-overlay');
        if (overlay) overlay.style.display = 'flex';
    }

    // Python hooks in here on new sessions to reset metrics
    Shiny.addCustomMessageHandler('reset_session_metrics', function(_) {
        window.idleTriggers = 0;
        window.sessionStartTime = Date.now();
        window.lastEncounterTime = Date.now();
        window.overtimeEncounters = 0;
        window.currentHazardPeak = window.baseHazardPeak;
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
        const t = e.target;
        if (!t) return;
        if (
            (t.classList && t.classList.contains('mcq-btn')) ||
            t.id === 'reveal_ans_btn'           ||
            t.id === 'btn_hard_left'            ||
            t.id === 'btn_hard_right'           ||
            t.id === 'attack_ambush'            ||
            t.id === 'flee_ambush'              ||
            t.id === 'start_hard_mode_btn'      ||
            t.id === 'return_setup_btn'
        ) { resetIdleTimer(); }
    }, true);

    // --- RPG WILD ENCOUNTER & SURVIVAL ENGINE ---
    window.keysSinceLastEncounter = 0;
    window.baseHazardPeak = 20.0; 
    window.currentHazardPeak = 20.0; 
    window.sessionStartTime = Date.now();
    window.lastEncounterTime = Date.now();
    window.overtimeEncounters = 0;
    window.initialConceptsLab = new Set();
    window.isFirstLoadLab = true;
    window.initialConceptsRead = new Set();
    window.isFirstLoadRead = true;
    window.originalSourceHTML = null; // Stores pristine source code for the Fog of War engine
    
    Shiny.addCustomMessageHandler('init_survival_model', function(peak) {
        if (peak && peak > 5) { 
            window.baseHazardPeak = peak; 
            window.currentHazardPeak = peak;
        }
    });

    // --- FOG OF WAR: SOFT-MARGIN CONCEPT HIGHLIGHTER ---
    function updateFogOfWar(notesText) {
        const sourceMap = document.getElementById('fog-of-war-container');
        if (!sourceMap) return;

        if (!window.originalSourceHTML) {
            window.originalSourceHTML = sourceMap.innerHTML; // Cache pure HTML on first run
        }

        const stopwords = new Set(["with", "from", "this", "that", "were", "been", "being", "have", "does", "could", "will", "would", "should", "might", "must", "what", "when", "where", "which", "then", "than", "because", "since", "until", "only", "also", "very", "just", "about", "into", "through", "after", "before", "over", "under", "between", "some", "such", "same", "every", "other", "another", "their", "there", "they"]);
        
        // Extract 4+ letter stems from user notes (pseudo-stemming for soft-margin matches)
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
    
    function extractConceptsWithAnswers(text) {
        if (!text) return [];
        const lines = text.split('\\n');
        const concepts = [];
        let currentConcept = null;
        let currentAnswer = [];

        for (let i = 0; i < lines.length; i++) {
            const l = lines[i];
            const trimmed = l.trim();
            let isConcept = false;
            let conceptText = "";

            if (trimmed.startsWith('#') && trimmed.length > 5) {
                isConcept = true;
                conceptText = trimmed.replace(/^#+\\s*/, '');
            } else if (trimmed.endsWith('?')) {
                isConcept = true;
                conceptText = trimmed;
            }

            if (isConcept) {
                if (currentConcept) {
                    concepts.push({ question: currentConcept, answer: currentAnswer.join('\\n').trim() });
                }
                currentConcept = conceptText;
                currentAnswer = [];
            } else {
                if (currentConcept && trimmed && !trimmed.startsWith('```') && !trimmed.startsWith('$$')) {
                    currentAnswer.push(trimmed.replace(/^[-*+]\\s*/, '')); 
                }
            }
        }
        if (currentConcept) {
            concepts.push({ question: currentConcept, answer: currentAnswer.join('\\n').trim() });
        }
        return concepts;
    }
    
    function battleFlash() {
        const flash = document.createElement('div');
        flash.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;box-shadow:inset 0 0 100px 30px rgba(220,53,69,0.7);z-index:9999;pointer-events:none;transition:opacity 0.8s;';
        document.body.appendChild(flash);
        setTimeout(() => flash.style.opacity = '0', 200);
        setTimeout(() => flash.remove(), 1000);
    }
    
    function checkEncounter(text, source) {
        resetIdleTimer();
        window.keysSinceLastEncounter++;
        if (window.keysSinceLastEncounter > 150) { 
            let totalSessionTime = (Date.now() - window.sessionStartTime) / 60000;
            let elapsedMinutes = (Date.now() - window.lastEncounterTime) / 60000;
            
            if (totalSessionTime >= window.baseHazardPeak) {
                window.currentHazardPeak = Math.max(3.0, window.baseHazardPeak * Math.pow(0.5, window.overtimeEncounters));
            } else {
                window.currentHazardPeak = window.baseHazardPeak;
            }

            let baseChance = 0.005;
            let hazardRatio = Math.min(elapsedMinutes / window.currentHazardPeak, 2.5);
            let dynamicChance = baseChance + (0.05 * Math.pow(hazardRatio, 2)); 
            
            if (Math.random() < dynamicChance) { 
                const allConcepts = extractConceptsWithAnswers(text);
                let activeConcepts = [];
                if (source === 'lab') {
                    if (window.isFirstLoadLab) {
                        allConcepts.forEach(c => window.initialConceptsLab.add(c.question));
                        window.isFirstLoadLab = false;
                    }
                    activeConcepts = allConcepts.filter(c => !window.initialConceptsLab.has(c.question));
                } else {
                    if (window.isFirstLoadRead) {
                        allConcepts.forEach(c => window.initialConceptsRead.add(c.question));
                        window.isFirstLoadRead = false;
                    }
                    activeConcepts = allConcepts.filter(c => !window.initialConceptsRead.has(c.question));
                }

                const fullyDrafted = activeConcepts.filter(c => c.answer && c.answer.length > 0);
                if (fullyDrafted.length > 0) { 
                    const idx = Math.floor(Math.random() * fullyDrafted.length);
                    battleFlash();
                    Shiny.setInputValue('wild_encounter', fullyDrafted[idx], {priority: 'event'});
                    window.keysSinceLastEncounter = 0; 
                    window.lastEncounterTime = Date.now(); 
                    if (totalSessionTime >= window.baseHazardPeak) { window.overtimeEncounters++; }
                }
            }
        }
    }

    function updateMindMap(markdown) {
        const { Transformer } = window.markmap;
        const transformer = new Transformer();
        const { root } = transformer.transform(markdown);
        const mmEl = document.getElementById('mindmap');
        if (!mmEl) return;
        mmEl.innerHTML = ''; 
        const mapOptions = { spacingHorizontal: 140, spacingVertical: 15 };
        const mm = markmap.Markmap.create('#mindmap', mapOptions, root);
        mm.fit(); 
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
                        Shiny.setInputValue('map_content_for_map', content, {priority: 'event'});
                    }, 300); 
                    checkEncounter(easymde.value(), 'lab');
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
                    
                    checkEncounter(content, 'read');
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

    Shiny.addCustomMessageHandler('render_colored_map', function(colored_md) {
        updateMindMap(colored_md);
    });

    let currentPdfUrl = null;
    Shiny.addCustomMessageHandler('load_pdf_blob', function(dataUri) {
        setTimeout(async function() {
            const iframe = document.getElementById('pdf-viewer-iframe');
            if (iframe) {
                try {
                    const res = await fetch(dataUri);
                    const blob = await res.blob();
                    if (currentPdfUrl) { URL.revokeObjectURL(currentPdfUrl); }
                    currentPdfUrl = URL.createObjectURL(blob);
                    iframe.src = currentPdfUrl;
                } catch (e) { console.error("Failed to load PDF blob:", e); }
            }
        }, 300); 
    });

    Shiny.addCustomMessageHandler('update_editor', function(markdown) {
        window.isFirstLoadLab = true; 
        window.initialConceptsLab.clear();
        window.sessionStartTime = Date.now();
        window.lastEncounterTime = Date.now();
        window.overtimeEncounters = 0;
        window.currentHazardPeak = window.baseHazardPeak;
        if (window.easymde_editor) { window.easymde_editor.value(markdown); }
        Shiny.setInputValue('map_content_for_map', markdown, {priority: 'event'});
    });

    Shiny.addCustomMessageHandler('insert_at_cursor', function(payload) {
        let cm = null;
        let editor = null;
        if (payload.target === 'read_note_main' && window.easymde_read_editor) {
            editor = window.easymde_read_editor; cm = editor.codemirror;
        } else if (payload.target === 'map_content' && window.easymde_editor) {
            editor = window.easymde_editor; cm = editor.codemirror;
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

# --- NLP DEPENDENCIES ---
def extract_source_chunks(text: str, sentences_per_chunk: int = 2) -> list[dict]:
    """Split source into overlapping semantic chunks with metadata."""
    # Breaking on newlines or sentence boundaries ensures headers/bullets are evaluated contextually
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

def render_fog_of_war_html(annotated_chunks: list[dict]) -> str:
    """Renders source text with coverage overlays."""
    if not annotated_chunks:
        return ""
    
    parts = []
    for chunk in annotated_chunks:
        text = chunk["text"].replace('\n', '<br>')
        status = chunk.get("status", "missing")
        score = chunk.get("coverage_score", 0)
        
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

def get_node_health():
    """Calculates forgetting curve decay across all mastered nodes"""
    df = load_node_mastery()
    if df.empty: return {"fading": 0, "forgotten": 0, "healthy": 0}
    
    rev_df = load_revisions()
    today = datetime.now().date()
    health = {"fading": 0, "forgotten": 0, "healthy": 0}
    
    for _, row in df.iterrows():
        score = row['Correct'] / max(row['Attempts'], 1)
        if score >= 0.8: # Only track decay for things you previously mastered
            map_revs = rev_df[rev_df['Map'] == row['Map']]
            if map_revs.empty:
                days_since = 999
            else:
                try:
                    map_revs['Date_Obj'] = pd.to_datetime(map_revs['Date'], errors='coerce')
                    last_date = map_revs['Date_Obj'].max().date()
                    days_since = (today - last_date).days
                except:
                    days_since = 0
            
            if days_since >= 14:   health["forgotten"] += 1
            elif days_since >= 7:  health["fading"] += 1
            else:                  health["healthy"] += 1
            
    return health

def get_survival_peak():
    """Calculates 75th percentile of session durations to find the 'Danger Zone'."""
    df = load_revisions()
    if df.empty or len(df) < 3:
        return 20.0 # Default 20 mins if not enough data
    return float(df['Duration (min)'].quantile(0.75))

def normalize_text(t):
    """Bulletproof string normalizer to fix invisible Markdown/PDF characters"""
    if pd.isna(t): return ""
    text = str(t).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def update_node_mastery(module, map_name, node_raw, is_correct):
    if not map_name: return
    map_name = map_name.strip().replace(" ", "_")
    if not map_name.endswith(".md"): map_name += ".md"
    
    df = load_node_mastery()
    norm_node = normalize_text(node_raw)
    
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
        
    if 'norm_raw' in df.columns:
        df = df.drop(columns=['norm_raw'])
        
    df.to_csv(NODE_LOG, index=False)

def inject_mastery_colors(module, map_name, raw_md):
    if not map_name: return raw_md
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
            header_match = re.match(r'^(\s*#{1,6}\s)(.*)', line)

            if header_match:
                prefix, content = header_match.groups()
                clean_content = content.strip() 
                raw_text = normalize_text(clean_content)
                score = score_dict.get(raw_text, -1)

                if score == -1: color = "#adb5bd" 
                elif score < 0.60: color = "#dc3545" 
                elif score < 0.80: color = "#fd7e14" 
                else: color = "#198754" 

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
                ui.output_ui("sl_live_timer_ui"),
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
    
    title="OptiSystem v6.50",
    id="main_nav",
    header=ui.output_ui("gamification_hud") 
)

# --- SERVER ---
def server(input, output, session):
    refresh_trigger = reactive.Value(0)
    user_stats_reactive = reactive.Value(load_user_stats())
    
    read_state = reactive.Value({"mode": None, "data": None})
    read_source_chunks = reactive.Value([])
    read_coverage_data = reactive.Value([])
    read_coverage_pct = reactive.Value(0.0)

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
    rev_session_correct = reactive.Value(0)
    rev_session_incorrect = reactive.Value(0)
    
    # Blurt Studio Session States
    blurt_state = reactive.Value("setup") 
    blurt_original = reactive.Value("")
    blurt_template = reactive.Value("")
    blurt_start_time = reactive.Value(0.0)
    blurt_active_mod = reactive.Value("")
    blurt_active_map = reactive.Value("")
    blurt_coverage_data = reactive.Value([])
    blurt_coverage_pct = reactive.Value(0.0)
    
    # Wild Encounter Session State
    wild_encounter_state = reactive.Value(None)

    # ==========================
    # SURVIVAL MODEL INIT
    # ==========================
    @reactive.Effect
    async def push_survival_data():
        refresh_trigger() # Update whenever a new session is logged
        peak = get_survival_peak()
        await session.send_custom_message("init_survival_model", peak)

    # ==========================
    # GAMIFICATION ENGINE (XP, STREAKS, QUESTS, ENCOUNTERS)
    # ==========================
    def grant_xp(amount):
        """Grants XP, calculates levels, and perfectly maintains the daily login streak"""
        stats = user_stats_reactive()
        today = datetime.now().date()
        last_active = stats.get("Last_Active", "")
        
        # Determine Daily Login Streak
        current_streak = stats.get("Daily_Streak", 0)
        if last_active:
            last_date = datetime.strptime(last_active, "%Y-%m-%d").date()
            delta = (today - last_date).days
            if delta == 1:
                current_streak += 1  # Streak preserved and increased!
            elif delta > 1:
                current_streak = 1   # Missed a day, streak broken and reset
        else:
            current_streak = 1       # First time using the system
            
        old_xp = int(stats.get("Total_XP", 0))
        new_xp = old_xp + amount
        
        # Leveling Curve Algorithm (Level 1 starts at 0 XP, gets exponentially harder)
        old_level = int((old_xp / 100) ** 0.5) + 1
        new_level = int((new_xp / 100) ** 0.5) + 1
        
        # Update State & DB
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
        
        # Reset quests if it's a new day
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
        fatigue_peak = get_survival_peak()
        
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
            ui.div(f"⏱️ Drop-out Peak: {fatigue_peak:.1f}m", class_="hud-item text-muted", style="font-size: 0.85em; border-right: 1px solid #dee2e6; padding-right: 10px;"),
            ui.div(f"🔥 {streak} Day Streak", class_="hud-item hud-streak"),
            ui.div(
                ui.span(f"🌟 Lvl {level}", class_="hud-level"),
                ui.span(f"{xp} XP", class_="hud-xp"),
                class_="hud-item"
            ),
            class_="gamification-hud"
        )
        
    # --- ESCAPE VALVE LOGIC ---
    @reactive.Effect
    @reactive.event(input.escape_valve_triggered)
    async def _handle_escape_valve():
        ui.update_navs("main_nav", selected="Revision Hub")
        grant_xp(50)
        ui.notification_show("Pivoted to Flashcards. Cool-down lap activated! +50 XP 🧠", type="message", duration=5)
        await session.send_custom_message("reset_session_metrics", None)

    # --- WILD ENCOUNTER LOGIC ---
    @reactive.Effect
    @reactive.event(input.wild_encounter)
    def trigger_ambush():
        encounter = input.wild_encounter() # Returns a dict: {question: ..., answer: ...}
        wild_encounter_state.set(encounter)
        m = ui.modal(
            ui.div(
                ui.h2("👾 WILD ENCOUNTER!", style="color: #dc3545; font-weight: 900; text-align: center; letter-spacing: 2px; margin-bottom: 5px;"),
                ui.p("A concept you just drafted attacks! Defend yourself.", class_="text-muted text-center"),
                ui.hr(style="border-color: #dc3545; opacity: 0.2;"),
                ui.div(
                    ui.h4(encounter['question'], style="text-align: center; margin: 25px 0; font-weight: bold; color: #212529;")
                ),
                ui.input_text_area("ambush_answer", label=None, placeholder="Type your defense here...", width="100%", height="120px"),
                ui.div(
                    ui.input_action_button("flee_ambush", "🏃 Run Away", class_="btn-outline-secondary"),
                    ui.input_action_button("attack_ambush", "⚔️ Attack! (Reveal)", class_="btn-danger", style="float: right; font-weight: bold;"),
                    style="margin-top: 20px;"
                ),
                style="animation: popInRPG 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);"
            ),
            title=None,
            size="l",
            easy_close=False,
            footer=None
        )
        ui.modal_show(m)
        ui.update_text_area("ambush_answer", value="")

    @reactive.Effect
    @reactive.event(input.attack_ambush)
    async def reveal_ambush():
        encounter = wild_encounter_state()
        ui.modal_remove()
        
        ans_html = protect_math(encounter['answer']) if encounter['answer'] else "_No specific bullet points logged yet._"
        
        m = ui.modal(
            ui.div(
                ui.h2("💥 BATTLE RESULTS", style="color: #6f42c1; font-weight: 900; text-align: center;"),
                ui.hr(),
                ui.h5("Your Defense:", class_="text-muted"),
                ui.p(input.ambush_answer() if input.ambush_answer() else "_Blank_"),
                ui.hr(),
                ui.h5("True Notes:", class_="text-muted"),
                ui.markdown(ans_html),
                ui.hr(),
                ui.div(
                    ui.input_action_button("ambush_fail", "❌ Missed it", class_="btn-outline-danger"),
                    ui.input_action_button("ambush_success", "✅ Nailed it! (+35 XP)", class_="btn-success", style="float: right; font-weight: bold;"),
                    style="margin-top: 20px;"
                )
            ),
            title=None, size="l", easy_close=False, footer=None
        )
        ui.modal_show(m)
        await session.send_custom_message("render_katex", None)

    @reactive.Effect
    @reactive.event(input.ambush_success)
    def ambush_win():
        ui.modal_remove()
        grant_xp(35)
        ui.notification_show("⚔️ Critical Hit! Concept defeated. +35 XP", type="message")

    @reactive.Effect
    @reactive.event(input.ambush_fail)
    def ambush_loss():
        ui.modal_remove()
        ui.notification_show("The concept got the better of you. Keep studying!", type="warning")

    @reactive.Effect
    @reactive.event(input.flee_ambush)
    def flee():
        ui.modal_remove()
        ui.notification_show("You fled the battle... no XP gained.", type="warning")

    @output
    @render.ui
    def scholar_profile_ui():
        stats = user_stats_reactive()
        xp = int(stats.get("Total_XP", 0))
        streak = int(stats.get("Daily_Streak", 0))
        level = int((xp / 100) ** 0.5) + 1
        
        # Calculate progress bar percentages
        current_level_base_xp = (level - 1) ** 2 * 100
        next_level_base_xp = (level) ** 2 * 100
        xp_needed = next_level_base_xp - current_level_base_xp
        xp_gained_this_level = xp - current_level_base_xp
        progress_pct = int((xp_gained_this_level / xp_needed) * 100) if xp_needed > 0 else 0
        
        # DOPAMINE HOOK: Forgetting Curve Urgency
        health = get_node_health()
        
        return ui.card(
            ui.div(
                ui.h2(f"Level {level} Scholar", style="color: #6f42c1; font-weight: 800; margin-bottom: 5px;"),
                ui.p(f"🔥 {streak} Day Active Learning Streak", style="color: #ff8c00; font-size: 1.1em; font-weight: 600; margin-bottom: 15px;"),
                ui.div(
                    ui.div(class_="progress-bar bg-success", style=f"width: {progress_pct}%"), 
                    class_="progress", style="height: 12px; border-radius: 10px; margin-bottom: 8px;"
                ),
                ui.p(f"{xp_gained_this_level} / {xp_needed} XP to Level {level + 1}", style="font-size: 0.85em; color: gray; text-align: right; margin: 0;"),
                
                # Retention Hook (Decaying Knowledge)
                ui.div(
                    ui.p(f"🔴 {health['forgotten']} Forgotten | 🟡 {health['fading']} Fading | 🟢 {health['healthy']} Healthy", 
                         style="font-size: 0.9em; font-weight: bold; margin-top: 15px; margin-bottom: 0; background: #fff; padding: 6px 12px; border-radius: 8px; border: 1px solid #dee2e6; display: inline-block;")
                )
            ),
            style="border-left: 5px solid #6f42c1; background: #faf8fc;"
        )

    @output
    @render.ui
    def quest_board_ui():
        stats = user_stats_reactive()
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Load completed list if it matches today's date
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
    def _request_purge():
        m = ui.modal(
            "Are you sure you want to delete all completed tasks? This cannot be undone.",
            title="Confirm Purge",
            footer=ui.div(
                ui.input_action_button("cancel_purge", "Cancel", class_="btn-secondary"),
                ui.input_action_button("confirm_purge", "Yes, Purge", class_="btn-danger")
            )
        )
        ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.cancel_purge)
    def _cancel_p():
        ui.modal_remove()

    @reactive.Effect
    @reactive.event(input.confirm_purge)
    def _execute_purge():
        ui.modal_remove()
        df = load_tasks()
        if df.empty: return
        df = df[df["Progress"] < 100].reset_index(drop=True)
        df['ID'] = df.index
        df.to_csv(TASK_LOG, index=False)
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show("Completed tasks purged.", type="message")

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
    def _request_delete():
        m = ui.modal(
            "Are you sure you want to delete this task?",
            title="Confirm Delete",
            footer=ui.div(
                ui.input_action_button("cancel_delete", "Cancel", class_="btn-secondary"),
                ui.input_action_button("confirm_delete", "Yes, Delete", class_="btn-danger")
            )
        )
        ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.cancel_delete)
    def _cancel_d():
        ui.modal_remove()

    @reactive.Effect
    @reactive.event(input.confirm_delete)
    def _execute_delete():
        ui.modal_remove()
        df = load_tasks().drop(int(input.task_to_edit())).reset_index(drop=True)
        df['ID'] = df.index
        df.to_csv(TASK_LOG, index=False)
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show("Task deleted.", type="message")

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
        
        # Reset semantic coverage
        read_source_chunks.set([])
        read_coverage_data.set([])
        read_coverage_pct.set(0.0)

        if pdf_info:
            try:
                pdf_path = pdf_info[0]["datapath"]
                
                with open(pdf_path, "rb") as f:
                    pdf_b64 = base64.b64encode(f.read()).decode('utf-8')
                
                data_uri = f"data:application/pdf;base64,{pdf_b64}"
                
                chunks = extract_pdf_chunks(pdf_path)
                read_source_chunks.set(chunks)
                read_coverage_data.set(chunks)
                
                read_state.set({
                    "mode": "pdf", 
                    "data": data_uri
                })
                ui.notification_show("PDF loaded via memory Blob! No files saved locally.", type="message")
            except Exception as e:
                ui.notification_show(f"Failed to load PDF: {str(e)}", type="error")
                
        elif text_source and text_source.strip():
            chunks = extract_source_chunks(text_source)
            read_source_chunks.set(chunks)
            read_coverage_data.set(chunks)
            
            read_state.set({"mode": "text", "data": text_source})
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
            await session.send_custom_message("load_pdf_blob", state["data"])
            
            return ui.div(
                ui.layout_columns(
                    ui.div(
                        ui.tags.iframe(id="pdf-viewer-iframe", src="", width="100%", height="800px", style="border: none; border-radius: 5px;"),
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
            
        # Dopamine Hook: Harvesting Notes grants XP
        grant_xp(50)
        check_quest_completion("Reading")
            
        refresh_trigger.set(refresh_trigger() + 1)
        ui.notification_show(f"Successfully exported {filename}! +50 XP 🌟", type="message")

    # ==========================
    # STUDY LAB LOGIC
    # ==========================
    @reactive.calc
    def current_time_tick():
        reactive.invalidate_later(1)
        return time.time()

    @output
    @render.ui
    def sl_live_timer_ui():
        if sl_active():
            elapsed = int(current_time_tick() - sl_start_time())
            mins, secs = divmod(elapsed, 60)
            return ui.h3(f"⏱️ {mins:02d}:{secs:02d}", style="color: #dc3545; text-align: center; margin-top: 10px; font-weight: bold;")
        return ui.div()

    @reactive.Effect
    @reactive.event(input.start_sl_btn)
    async def _start_sl():
        sl_start_time.set(time.time())
        sl_active.set(True)
        await session.send_custom_message("reset_session_metrics", None)
        ui.notification_show("Note-taking session started. Deep Work Index active.", type="message")

    @reactive.Effect
    @reactive.event(input.end_sl_btn)
    def _end_sl():
        if not sl_active(): return
        duration = round((time.time() - sl_start_time()) / 60, 2)
        df = load_revisions()
        new_row = pd.DataFrame({"Module": [input.map_mod()], "Map": [input.save_name() if input.save_name() else "Drafting"], "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], "Duration (min)": [duration], "Activity": ["Study Lab"]})
        pd.concat([df, new_row], ignore_index=True).to_csv(REV_LOG, index=False)
        sl_active.set(False)
        
        # Calculate DWI
        triggers = input.current_idle_triggers() if 'current_idle_triggers' in input else 0
        dwi = max(0, 100 - (triggers * 15))
        
        if dwi >= 90: grade, gcolor = "S-Tier", "#198754"
        elif dwi >= 70: grade, gcolor = "A-Grade", "#0dcaf0"
        elif dwi >= 50: grade, gcolor = "B-Grade", "#fd7e14"
        else: grade, gcolor = "C-Grade", "#dc3545"

        base_xp = 50
        bonus = 50 if grade == "S-Tier" else 0
        grant_xp(base_xp + bonus)
        check_quest_completion("Study Lab", duration=duration)
        refresh_trigger.set(refresh_trigger() + 1)
        
        # Show Summary Modal
        m = ui.modal(
            ui.div(
                ui.h2("📝 Encoding Complete!", style="text-align: center; color: #333; font-weight: 800;"),
                ui.h1(grade, style=f"color: {gcolor}; text-align: center; font-size: 3.5em; font-weight: 900; margin: 10px 0;"),
                ui.p("Deep Work Index (DWI)", style="text-align: center; color: gray; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; margin-bottom: 0;"),
                ui.h3(f"{dwi}%", style="text-align: center; font-weight: 900; margin-top: 5px;"),
                ui.p(f"⏱️ Session Length: {duration} mins | 📉 Idle warnings: {triggers}", style="text-align: center; color: #6c757d; font-size: 0.9em;"),
                ui.hr(),
                ui.h4(f"🌟 +{base_xp + bonus} XP Earned", style="text-align: center; color: #198754; font-weight: bold;")
            ),
            easy_close=True, footer=ui.input_action_button("close_sl_summary", "Close", class_="btn-primary w-100")
        )
        ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.close_sl_summary)
    def _close_sl_summary():
        ui.modal_remove()

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
        
        # Insert image accurately at cursor position instead of appending to end
        img_md = f"\n![{filename}](/files/{input.map_mod()}/{filename})\n"
        await session.send_custom_message("insert_at_cursor", {"target": "map_content", "text": img_md})

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
    async def _start_revision():
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
        path_stack = []
        
        def save_node():
            ans_text = "\n".join(current_answer).strip()
            if ans_text and current_heading:
                # Combine breadcrumbs for context
                breadcrumb = " > ".join([p[1] for p in path_stack]) if path_stack else current_heading
                slides.append({"breadcrumb": breadcrumb, "raw": ans_text})
            current_answer.clear()

        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith("`" * 3):
                in_code = not in_code
            elif stripped == "$$": 
                in_math = not in_math
                
            is_new_node = False
            level = 0
            content = ""
            
            # Only detect new nodes if we are outside of a code/math block
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
                save_node() # Wrap up the previous slide
                
                # Manage hierarchy
                while path_stack and path_stack[-1][0] >= level: 
                    path_stack.pop()
                path_stack.append((level, content))
                
            current_answer.append(line.rstrip("\n"))
            
        save_node() # Catch the last slide
        
        if not slides:
            slides = [{"breadcrumb": "Empty", "raw": "No content found."}]
            
        rev_slides.set(slides)
        rev_current_idx.set(0)
        rev_streak.set(0)
        rev_session_correct.set(0)
        rev_session_incorrect.set(0)
        rev_mcq_options.set(generate_mcq_opts(0, slides))
        rev_start_time.set(time.time())
        rev_phase.set("easy") # Start in the low-friction warm-up phase
        await session.send_custom_message("reset_session_metrics", None)

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
        
        # DOPAMINE HOOK: Primer Streaks build XP multipliers!
        if is_correct:
            rev_streak.set(rev_streak() + 1)
            grant_xp(5) # Small micro-reward to reinforce the click
            ui.notification_show("Correct! +5 XP (+1 Combo) 🔥" if rev_streak() >=3 else "Correct! +5 XP", type="message", duration=2)
        else:
            rev_streak.set(0)
            ui.notification_show("Incorrect, combo lost!", type="warning", duration=2)
            
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
        
        node_question = slides[idx]["breadcrumb"]
        is_correct = (direction == 'right')
        
        # --- DOPAMINE HOOK: THE COMBO MULTIPLIER ---
        if is_correct:
            current_combo = rev_streak()
            multiplier = min(current_combo + 1, 5) # Caps at a massive 5x XP boost
            xp_gain = 15 * multiplier
            grant_xp(xp_gain)
            
            rev_session_correct.set(rev_session_correct() + 1)
            rev_streak.set(current_combo + 1)
            update_node_mastery(rev_active_mod(), rev_active_map(), node_question, True)
            
            ui.notification_show(f"Epic Recall! +{xp_gain} XP (x{multiplier} Combo!) 🚀", type="message", duration=2)
        else:
            rev_streak.set(0)
            rev_session_incorrect.set(rev_session_incorrect() + 1)
            update_node_mastery(rev_active_mod(), rev_active_map(), node_question, False)
            
            ui.notification_show("Combo broken. Keep going!", type="warning", duration=2)
        
        refresh_trigger.set(refresh_trigger() + 1)
        
        if idx < len(slides) - 1:
            rev_current_idx.set(idx + 1)
            rev_show_ans.set(False)
        else:
            # Complete Revision Session and move to Summary Screen
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
            
            # Check for Quests
            total_cards = len(slides)
            acc = rev_session_correct() / max(total_cards, 1)
            check_quest_completion("Revision", duration=duration, accuracy=acc, cards=total_cards)
            
            rev_phase.set("summary")
            refresh_trigger.set(refresh_trigger() + 1)
            
    @reactive.Effect
    @reactive.event(input.return_setup_btn)
    def _return_setup():
        rev_phase.set("setup")
        rev_slides.set([])

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
            streak_badge = f'<span class="badge bg-warning text-dark" style="font-size: 1.1em; float:right;">🔥 Combo: {min(streak+1, 5)}x</span>' if streak > 0 else ""
            
            if not rev_show_ans():
                return ui.div(
                    ui.HTML(streak_badge),
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
                    ui.HTML(streak_badge),
                    ui.p(slides[idx]["breadcrumb"], class_="text-muted", style="font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px;"),
                    ui.hr(style="margin-top: 5px;"),
                    ui.div(ui.markdown(display_raw), class_="slide-content flashcard-box", style="font-size: 1.6em; text-align: center;"),
                    ui.hr(),
                    ui.layout_columns(
                        ui.HTML('<button id="btn_hard_left" class="btn btn-outline-danger btn-lg w-100" onclick="Shiny.setInputValue(\'hard_answer\', \'left\', {priority: \'event\'})">⬅️ Needs Review</button>'),
                        ui.HTML('<button id="btn_hard_right" class="btn btn-outline-success btn-lg w-100" onclick="Shiny.setInputValue(\'hard_answer\', \'right\', {priority: \'event\'})">Got it ➡️</button>'),
                        col_widths=(6, 6)
                    ),
                    class_="card p-4 shadow-sm slide-container"
                )
                
        elif phase == "summary":
            correct = rev_session_correct()
            incorrect = rev_session_incorrect()
            total = correct + incorrect
            acc = int((correct / total * 100)) if total > 0 else 0
            duration = round((time.time() - rev_start_time()) / 60, 2)

            triggers = input.current_idle_triggers() if 'current_idle_triggers' in input else 0
            dwi = max(0, 100 - (triggers * 15))

            if acc >= 90 and dwi >= 85: grade, gcolor = "S-Tier", "#198754"
            elif acc >= 75 and dwi >= 70: grade, gcolor = "A-Grade", "#0dcaf0"
            elif acc >= 60 and dwi >= 50: grade, gcolor = "B-Grade", "#fd7e14"
            else: grade, gcolor = "C-Grade", "#dc3545"

            acc_color = "#198754" if acc >= 80 else "#fd7e14" if acc >= 50 else "#dc3545"
            msg = f"Outstanding Mastery! You earned an {grade}." if grade in ["S-Tier", "A-Grade"] else "Solid Effort! Focus on your pacing."

            return ui.div(
                ui.h2("🎉 Session Complete!"),
                ui.p(msg, class_="text-muted mb-4", style="font-size: 1.1em;"),
                ui.layout_columns(
                    ui.div(
                        ui.h1(f"{acc}%", style=f"color: {acc_color}; font-weight: 900; margin: 0; font-size: 2.5em;"),
                        ui.p("Accuracy", class_="text-muted", style="text-transform: uppercase; font-size: 0.8em; letter-spacing: 1px; margin-top: 5px;"),
                        class_="p-3 text-center", style="background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;"
                    ),
                    ui.div(
                        ui.h1(f"{dwi}%", style=f"color: {gcolor}; font-weight: 900; margin: 0; font-size: 2.5em;"),
                        ui.p("Engagement (DWI)", class_="text-muted", style="text-transform: uppercase; font-size: 0.8em; letter-spacing: 1px; margin-top: 5px;"),
                        class_="p-3 text-center", style="background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;"
                    ),
                    ui.div(
                        ui.h1(grade, style=f"color: {gcolor}; font-weight: 900; margin: 0; font-size: 2.5em;"),
                        ui.p("Session Rank", class_="text-muted", style="text-transform: uppercase; font-size: 0.8em; letter-spacing: 1px; margin-top: 5px;"),
                        class_="p-3 text-center", style=f"background: {gcolor}15; border-radius: 8px; border: 1px solid {gcolor}44;"
                    ),
                    col_widths=(4, 4, 4)
                ),
                ui.p(f"⏱️ Time logged: {duration} mins | 📉 Idle warnings: {triggers}", class_="text-center mt-4 text-muted", style="font-size: 0.9em; font-weight: bold;"),
                ui.hr(),
                ui.input_action_button("return_setup_btn", "Finish & Return to Hub", class_="btn-primary btn-lg w-100"),
                class_="card p-4 shadow-sm slide-container", style="display: flex; flex-direction: column; justify-content: center; min-height: 350px;"
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
    async def _start_blurt():
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
        await session.send_custom_message("reset_session_metrics", None)

    @reactive.Effect
    @reactive.event(input.review_blurt_btn)
    async def _review_blurt():
        if blurt_state() == "blurting":
            blurt_state.set("review")
            duration = round((time.time() - blurt_start_time()) / 60, 2)
            
            orig_text = blurt_original()
            blurt_text = input.blurt_input()
            
            chunks = extract_source_chunks(orig_text)
            
            def compute():
                if SEMANTIC_MODEL is None:
                    return 0.0, chunks
                return compute_semantic_coverage(chunks, blurt_text)

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
            triggers = input.current_idle_triggers() if 'current_idle_triggers' in input else 0
            dwi = max(0, 100 - (triggers * 15))
            if dwi >= 85: 
                base_xp += 50
                ui.notification_show(f"Laser Focus Bonus! +50 XP", type="message")

            if score_pct >= 90:
                grant_xp(base_xp + 150)
                ui.notification_show(f"Flawless Synthesis! {score_pct}% Core Concepts Captured. +250 XP 🧠🌟", type="message")
            elif score_pct >= 70:
                grant_xp(base_xp + 50)
                ui.notification_show(f"Great Blurt! {score_pct}% Core Concepts Captured. +150 XP 🧠", type="message")
            else:
                grant_xp(base_xp)
                ui.notification_show(f"Blurt Complete! {score_pct}% Coverage. Keep practicing! +100 XP", type="message")
            
            check_quest_completion("Blurt", duration=duration)
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
            
            # Retrieve the pre-computed semantic results
            score_pct = int(blurt_coverage_pct() * 100)
            
            triggers = input.current_idle_triggers() if 'current_idle_triggers' in input else 0
            dwi = max(0, 100 - (triggers * 15))
            
            annotated_orig_html = render_fog_of_war_html(blurt_coverage_data())
            if not annotated_orig_html:
                annotated_orig_html = protect_math(blurt_original())
                
            score_color = '#198754' if score_pct >= 80 else '#fd7e14' if score_pct >= 50 else '#dc3545'
            
            return ui.div(
                ui.div(
                    ui.h3("🧠 Semantic Analysis", class_="text-center mb-3", style="font-weight: 800;"),
                    ui.layout_columns(
                        ui.div(ui.tags.b("🎯 Semantic Coverage:"), ui.h3(f"{score_pct}%", style=f"font-weight: 900; color: {score_color}; margin-bottom: 0;"), class_="p-3 border rounded bg-white shadow-sm text-center"),
                        ui.div(ui.tags.b("⚡ Engagement (DWI):"), ui.h3(f"{dwi}%", style="font-weight: 900; color: #0d6efd; margin-bottom: 0;"), ui.p(f"{triggers} idle breaks", style="font-size: 0.8em; color: gray; margin-bottom: 0;"), class_="p-3 border rounded bg-white shadow-sm text-center"),
                        col_widths=(6, 6)
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