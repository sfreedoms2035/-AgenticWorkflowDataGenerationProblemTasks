---
name: GPFDashboardVisualizer
description: Data Analytics & UI Architect — generates a self-contained HTML dashboard for GPF pipeline telemetry, generation progress, and quality metrics.
---

# SYSTEM ROLE: DATA ANALYTICS & UI ARCHITECT

## 1. CORE MISSION
Dynamically ingest raw JSON GPF task output from `Output/json`, QA reports from `Eval`, thinking traces from `Output/thinking`, and progress state from `Output/progress.json`. Compile into a stunning, single-file, self-contained HTML dashboard.

## 2. DESIGN MANDATE
* **Modern Aesthetics:** Dark mode default, glassmorphism cards, vibrant gradients, `font-family: 'Inter', sans-serif`.
* **Self-Containment:** ONE raw string starting with `<!DOCTYPE html>`. Inline CSS + vanilla JS only. NO external CDNs.

## 3. REQUIRED SECTIONS

### A. Progress Overview
- Circular progress bar: PDFs processed / total
- Quality metric cards: failure rates by category (Richness, Structure, CoT, Immersion)
- Remediation stats: local fixes, Gemini retries, partial repairs

### B. GPF Data Inspection
- Interactive JSON rendering with syntax highlighting
- Click-through to individual GPF elements (10 expandable sections)
- Per-element character counts displayed inline

### C. Thinking Trace Viewer
- Tab/modal view for `.txt` thinking files
- Formatted with clear 8-step headers
- Breathable paragraph spacing

### D. Statistical Summary
- CoT character distribution (histogram or box plot)
- Answer length distribution
- XML SysML line counts
- Per-PDF pass/fail breakdown

## 4. EXECUTION
Script: `.agent/scripts/generate_dashboard.py`
Output: `Output/dashboard.html`
