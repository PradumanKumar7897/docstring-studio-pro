import os
import sys
import ast
import json
import subprocess
import traceback
import streamlit as st
from streamlit_ace import st_ace
from dotenv import load_dotenv

# ---------------- FIX PROJECT PATH ----------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

load_dotenv()

# ---------------- DOCGEN IMPORTS ----------------
from docgen.ai.service import generate_docstring_ai
from docgen.ai.config import AIConfig

from docgen.parser import parse_code
from docgen.generator import generate_docstring
from docgen.writer import add_docstrings_to_code

from docgen.validator.service import validate_project_code
from docgen.validator.config import ValidationConfig

st.set_page_config(layout="wide", page_title="Docstring Studio Pro V3")

# ================= RESET FUNCTION =================
def reset_app():
    keys_to_clear = [
        "editor_code",
        "updated_code",
        "parsed_items",
        "validation",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    st.success("Application reset successfully!")


# ================= SIDEBAR =================
with st.sidebar:
    st.title("⚙️ Settings")

    dark = st.toggle("🌙 Dark Mode", True)

    style = st.selectbox("Docstring Style", ["google", "numpy", "rest"])

    provider = st.selectbox(
        "AI Provider",
        ["local", "auto", "openai", "groq", "gemini"],
        index=1,
    )

    # -------- Model Selection --------
    if provider == "openai":
        model = st.selectbox(
            "Model",
            ["gpt-5.2", "gpt-4.1-mini"],
        )
    elif provider == "groq":
        model = st.selectbox(
            "Model",
            ["llama-3.1-70b-versatile", "llama-3.1-8b-instant"],
        )
    elif provider == "gemini":
        model = st.selectbox(
            "Model",
            ["gemini-1.5-pro", "gemini-1.5-flash"],
        )
    else:
        model = st.text_input("Model Name (optional)", "")

    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    overwrite = st.toggle("♻️ Overwrite existing docstrings", False)

    st.divider()

    if st.button("🔄 Reset App"):
        reset_app()
        st.rerun()

    # -------- Run Tests from Sidebar --------
    st.divider()
    st.markdown("### 🧪 Test Suite")
    if st.button("▶️ Run All Tests"):
        with st.spinner("Running pytest..."):
            result = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    "--json-report",
                    f"--json-report-file={ROOT_DIR}/test-results.json",
                    f"{ROOT_DIR}/tests/",
                    "-q",
                    "--tb=short",
                ],
                capture_output=True,
                text=True,
                cwd=ROOT_DIR,
            )
        if result.returncode == 0:
            st.success("✅ All tests passed!")
        else:
            st.error("❌ Some tests failed.")
        st.session_state["test_stdout"] = result.stdout
        st.session_state["test_stderr"] = result.stderr
        st.rerun()


# ================= THEME =================
bg = "#0f172a" if dark else "#f9fafb"
text = "#e5e7eb" if dark else "#111827"

st.markdown(
    f"""
<style>
body {{ background-color: {bg}; color: {text}; }}

/* ── Test dashboard custom styles ── */
.test-pass  {{ color: #22c55e; font-weight: 600; }}
.test-fail  {{ color: #ef4444; font-weight: 600; }}
.test-skip  {{ color: #eab308; font-weight: 600; }}
.test-error {{ color: #f97316; font-weight: 600; }}

div[data-testid="metric-container"] {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 12px 16px;
}}
</style>
""",
    unsafe_allow_html=True,
)

st.title("🧠 Docstring Studio Pro V3")
st.caption("Multi-Provider AI | Smart Routing | Clean Architecture")

# ================= HELPERS =================
def side_diff(a: str, b: str):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original")
        st.code(a, language="python")

    with col2:
        st.subheader("Updated")
        st.code(b, language="python")


def build_items_and_docstrings(code: str):
    items = parse_code(code)

    for item in items:
        item_type = item["type"]
        name = item["name"]
        args = item.get("args", [])
        returns = item.get("returns")

        # ---------- LOCAL ----------
        if provider == "local":
            item["generated_docstring"] = generate_docstring(
                name=name,
                args=args,
                returns=returns,
                style=style,
                item_type=item_type,
            )
            item["engine_used"] = "local"

        # ---------- AI PROVIDERS ----------
        else:
            cfg = AIConfig(
                provider=provider,
                temperature=temperature,
            )

            # Assign correct model
            if provider == "openai":
                cfg.openai_model = model
            elif provider == "groq":
                cfg.groq_model = model
            elif provider == "gemini":
                cfg.gemini_model = model

            prompt = f"""
Generate a {style} style docstring for a {item_type}.

Name: {name}
Args: {args}
Returns: {returns}
"""

            try:
                result = generate_docstring_ai(prompt, cfg)
                item["generated_docstring"] = result
                item["engine_used"] = provider
            except Exception as e:
                item["generated_docstring"] = f"AI Error: {str(e)}"
                item["engine_used"] = "error"

    return items


# ================= TEST DASHBOARD HELPERS =================

SUITE_META = {
    "test_parser":      {"icon": "⚙️",  "color": "#38bdf8", "label": "Parser Tests"},
    "test_generation":  {"icon": "✨",  "color": "#a78bfa", "label": "Generation Tests"},
    "test_validation":  {"icon": "✅",  "color": "#34d399", "label": "Validation Tests"},
    "test_integration": {"icon": "🔗",  "color": "#fb923c", "label": "Integration Tests"},
    "test_ui":          {"icon": "🖥️",  "color": "#f472b6", "label": "UI Tests"},
}

def _load_test_results():
    """Load test-results.json from project root. Returns dict or None."""
    path = os.path.join(ROOT_DIR, "test-results.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def _group_tests_by_suite(data: dict) -> dict:
    """
    Group pytest JSON report tests by suite file name.
    Returns dict: suite_key -> { meta, tests, passed, failed, skipped, duration }
    """
    groups = {}
    for t in data.get("tests", []):
        # nodeid example: tests/test_parser.py::TestBasicExtraction::test_foo
        parts = t["nodeid"].replace("\\", "/").split("/")
        filename = parts[-1].split("::")[0]          # test_parser.py
        suite_key = filename.replace(".py", "")      # test_parser

        if suite_key not in groups:
            meta = SUITE_META.get(suite_key, {
                "icon": "📦",
                "color": "#94a3b8",
                "label": suite_key.replace("test_", "").title() + " Tests",
            })
            groups[suite_key] = {
                "meta": meta,
                "tests": [],
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration_ms": 0,
            }

        outcome = t.get("outcome", "unknown")
        duration_ms = round(t.get("call", {}).get("duration", 0) * 1000)
        test_name = t["nodeid"].split("::")[-1]

        groups[suite_key]["tests"].append({
            "name": test_name,
            "nodeid": t["nodeid"],
            "outcome": outcome,
            "duration_ms": duration_ms,
            "longrepr": t.get("call", {}).get("longrepr", "") or
                        t.get("setup", {}).get("longrepr", ""),
        })

        groups[suite_key]["duration_ms"] += duration_ms
        if outcome == "passed":
            groups[suite_key]["passed"] += 1
        elif outcome == "failed":
            groups[suite_key]["failed"] += 1
        else:
            groups[suite_key]["skipped"] += 1

    return groups


def _render_donut_svg(pass_count: int, total: int, color: str, size: int = 56) -> str:
    """Return an inline SVG donut chart as HTML string."""
    import math
    if total == 0:
        return ""
    r = (size - 8) / 2
    circ = 2 * math.pi * r
    arc = (pass_count / total) * circ
    cx = cy = size / 2
    pct = round((pass_count / total) * 100)
    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}"
         style="transform:rotate(-90deg);display:block;">
      <circle cx="{cx}" cy="{cy}" r="{r}"
              fill="none" stroke="#1e293b" stroke-width="6"/>
      <circle cx="{cx}" cy="{cy}" r="{r}"
              fill="none" stroke="{color}" stroke-width="6"
              stroke-dasharray="{arc:.1f} {circ - arc:.1f}"
              stroke-linecap="round"/>
    </svg>
    <div style="font-size:11px;font-weight:700;color:{color};
                text-align:center;margin-top:2px;">{pct}%</div>
    """
    return svg


def render_test_dashboard():
    """Render the full test results dashboard inside a Streamlit tab."""

    # ── Header row ──────────────────────────────────────────────────
    run_col, spacer = st.columns([1, 3])
    with run_col:
        if st.button("▶️ Run Tests Now", key="run_tests_tab"):
            with st.spinner("Running pytest..."):
                result = subprocess.run(
                    [
                        sys.executable, "-m", "pytest",
                        "--json-report",
                        f"--json-report-file={ROOT_DIR}/test-results.json",
                        f"{ROOT_DIR}/tests/",
                        "-q", "--tb=short",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=ROOT_DIR,
                )
            st.session_state["test_stdout"] = result.stdout
            st.session_state["test_stderr"] = result.stderr
            st.rerun()

    data = _load_test_results()

    if data is None:
        st.info(
            "No test results yet. Click **▶️ Run Tests Now** above "
            "or use the **▶️ Run All Tests** button in the sidebar."
        )
        return

    # ── Global summary metrics ───────────────────────────────────────
    summary  = data.get("summary", {})
    total    = summary.get("total",   0)
    passed   = summary.get("passed",  0)
    failed   = summary.get("failed",  0)
    skipped  = summary.get("skipped", 0)
    duration = round(data.get("duration", 0), 2)
    pass_pct = round((passed / total * 100) if total else 0, 1)

    st.markdown("---")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("🧪 Total Tests",  total)
    m2.metric("✅ Passed",       passed)
    m3.metric("❌ Failed",       failed,   delta=f"-{failed}"  if failed  else None, delta_color="inverse")
    m4.metric("⏭️ Skipped",      skipped,  delta=f"-{skipped}" if skipped else None, delta_color="off")
    m5.metric("⏱️ Duration",     f"{duration}s")

    # Global pass-rate progress bar
    bar_color = "#22c55e" if pass_pct == 100 else ("#eab308" if pass_pct >= 80 else "#ef4444")
    st.markdown(f"""
    <div style="margin:12px 0 4px;font-size:12px;color:#94a3b8;">
        Overall Pass Rate &nbsp;<strong style="color:{bar_color}">{pass_pct}%</strong>
    </div>
    <div style="background:#1e293b;border-radius:6px;height:10px;overflow:hidden;">
        <div style="width:{pass_pct}%;height:100%;background:{bar_color};
                    border-radius:6px;transition:width 0.8s ease;"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Per-suite section ────────────────────────────────────────────
    groups = _group_tests_by_suite(data)

    if not groups:
        st.warning("No test groups found in results file.")
        return

    # Suite summary cards (one row)
    cols = st.columns(len(groups))
    for col, (suite_key, grp) in zip(cols, groups.items()):
        meta   = grp["meta"]
        s_tot  = grp["passed"] + grp["failed"] + grp["skipped"]
        s_pct  = round((grp["passed"] / s_tot * 100) if s_tot else 0)
        c_val  = "#22c55e" if s_pct == 100 else ("#eab308" if s_pct >= 80 else "#ef4444")
        with col:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                        border-top:3px solid {meta['color']};border-radius:12px;
                        padding:14px 12px;text-align:center;">
                <div style="font-size:20px;">{meta['icon']}</div>
                <div style="font-size:11px;font-weight:600;color:{meta['color']};
                            letter-spacing:1px;margin:4px 0;">{suite_key.replace('test_','').upper()}</div>
                <div style="font-size:22px;font-weight:700;color:{c_val};">{grp['passed']}<span style="font-size:13px;color:#64748b;">/{s_tot}</span></div>
                <div style="font-size:11px;color:{c_val};font-weight:600;">{s_pct}% pass</div>
                <div style="font-size:10px;color:#475569;margin-top:4px;">{grp['duration_ms']}ms</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Detail expanders per suite ───────────────────────────────────
    view_tab1, view_tab2, view_tab3 = st.tabs(
        ["📋 All Tests", "📊 Duration Chart", "🖥️ Raw Output"]
    )

    # ── Tab 1: All tests list ────────────────────────────────────────
    with view_tab1:
        for suite_key, grp in groups.items():
            meta  = grp["meta"]
            s_tot = grp["passed"] + grp["failed"] + grp["skipped"]
            label = f"{meta['icon']} {meta['label']}  —  {grp['passed']}/{s_tot} passed  ({grp['duration_ms']}ms)"

            with st.expander(label, expanded=(grp["failed"] > 0)):
                for t in grp["tests"]:
                    outcome = t["outcome"]
                    icon    = {"passed": "✅", "failed": "❌", "skipped": "⏭️"}.get(outcome, "❓")
                    badge_color = {"passed": "#22c55e", "failed": "#ef4444", "skipped": "#eab308"}.get(outcome, "#94a3b8")

                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:10px;
                                padding:7px 10px;margin-bottom:4px;
                                background:rgba(255,255,255,0.02);border-radius:7px;
                                border-left:3px solid {badge_color};">
                        <span style="font-size:14px;">{icon}</span>
                        <code style="font-size:12px;color:#cbd5e1;flex:1;">{t['name']}</code>
                        <span style="font-size:11px;color:#475569;font-family:monospace;">{t['duration_ms']}ms</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Show failure traceback inline
                    if outcome == "failed" and t.get("longrepr"):
                        with st.expander("🔍 Traceback", expanded=False):
                            st.code(t["longrepr"], language="python")

    # ── Tab 2: Duration bar chart ────────────────────────────────────
    with view_tab2:
        # Collect all tests with suite info
        all_tests = []
        for suite_key, grp in groups.items():
            for t in grp["tests"]:
                all_tests.append({
                    "name": t["name"][:55] + ("…" if len(t["name"]) > 55 else ""),
                    "suite": suite_key.replace("test_", ""),
                    "duration_ms": t["duration_ms"],
                    "outcome": t["outcome"],
                    "color": grp["meta"]["color"],
                })

        # Top 20 slowest
        slowest = sorted(all_tests, key=lambda x: x["duration_ms"], reverse=True)[:20]
        max_dur = slowest[0]["duration_ms"] if slowest else 1

        st.markdown("#### ⏱️ Top 20 Slowest Tests")
        for t in slowest:
            bar_w = max(2, round((t["duration_ms"] / max_dur) * 100))
            outcome_color = {"passed": t["color"], "failed": "#ef4444", "skipped": "#eab308"}.get(t["outcome"], "#94a3b8")
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <div style="font-size:10px;color:#475569;font-family:monospace;
                            width:80px;text-align:right;flex-shrink:0;">{t['suite']}</div>
                <div style="flex:1;background:#1e293b;border-radius:4px;height:18px;overflow:hidden;">
                    <div style="width:{bar_w}%;height:100%;background:{outcome_color};
                                border-radius:4px;opacity:0.85;"></div>
                </div>
                <div style="font-size:11px;color:#64748b;font-family:monospace;
                            width:44px;text-align:right;flex-shrink:0;">{t['duration_ms']}ms</div>
                <div style="font-size:11px;color:#94a3b8;flex:2;
                            overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{t['name']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Suite duration comparison
        st.markdown("#### 📊 Suite Duration Comparison")
        suite_dur_max = max((grp["duration_ms"] for grp in groups.values()), default=1)
        for suite_key, grp in groups.items():
            meta  = grp["meta"]
            bar_w = max(2, round((grp["duration_ms"] / suite_dur_max) * 100))
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                <div style="font-size:12px;color:{meta['color']};
                            width:110px;flex-shrink:0;">{meta['icon']} {suite_key.replace('test_','')}</div>
                <div style="flex:1;background:#1e293b;border-radius:5px;height:20px;overflow:hidden;">
                    <div style="width:{bar_w}%;height:100%;
                                background:linear-gradient(90deg,{meta['color']}88,{meta['color']});
                                border-radius:5px;"></div>
                </div>
                <div style="font-size:12px;color:#64748b;font-family:monospace;
                            width:55px;text-align:right;flex-shrink:0;">{grp['duration_ms']}ms</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 3: Raw pytest output ─────────────────────────────────────
    with view_tab3:
        stdout = st.session_state.get("test_stdout", "")
        stderr = st.session_state.get("test_stderr", "")

        if stdout:
            st.markdown("**stdout**")
            st.code(stdout, language="bash")
        if stderr:
            st.markdown("**stderr**")
            st.code(stderr, language="bash")
        if not stdout and not stderr:
            st.info("Run tests to see raw output here.")


# ================= FILE UPLOAD =================
uploaded = st.file_uploader("Upload Python file", type=["py"])

if uploaded:
    filename = uploaded.name
    original_code = uploaded.read().decode("utf-8")

    if "editor_code" not in st.session_state:
        st.session_state.editor_code = original_code


    tab_editor, tab_items, tab_diff, tab_validate, tab_tests = st.tabs(
        ["📝 Editor", "📌 Items", "🔍 Diff", "✅ Validate", "🧪 Tests"]
    )

    # ================= EDITOR =================
    with tab_editor:
        st.subheader("Editable Code")

        st.session_state.editor_code = st_ace(
            value=st.session_state.editor_code,
            language="python",
            theme="monokai" if dark else "github",
            height=450,
            auto_update=True,
        )

        if st.button("✨ Generate Docstrings"):
            try:
                items = build_items_and_docstrings(
                    st.session_state.editor_code
                )

                updated = add_docstrings_to_code(
                    st.session_state.editor_code,
                    items,
                    overwrite=overwrite,
                )

                st.session_state.updated_code = updated
                st.session_state.parsed_items = items

                cfg = ValidationConfig(ignore_codes=["D203", "D213"])
                issues = validate_project_code(updated, cfg)
                st.session_state.validation = issues

                st.success("Docstrings generated successfully!")

            except Exception:
                st.error("Generation failed:")
                st.code(traceback.format_exc())

        if "updated_code" in st.session_state:
            st.divider()
            st.subheader("Updated Code")
            st.code(st.session_state.updated_code, language="python")

            st.download_button(
                "⬇️ Download Updated File",
                st.session_state.updated_code.encode(),
                filename.replace(".py", "_docstrings.py"),
            )

    # ================= ITEMS =================
    with tab_items:
        if "parsed_items" not in st.session_state:
            st.info("Generate docstrings first.")
        else:
            for item in st.session_state.parsed_items:
                with st.expander(f"{item['type']} • {item['name']}"):
                    st.code(item.get("generated_docstring", ""))

    # ================= DIFF =================
    with tab_diff:
        if "updated_code" in st.session_state:
            side_diff(original_code, st.session_state.updated_code)
        else:
            st.info("Generate docstrings first.")

    # ================= VALIDATION =================
    with tab_validate:
        if "validation" not in st.session_state:
            st.info("Generate docstrings first.")
        else:
            issues = st.session_state.validation

            if not issues:
                st.success("✅ No validation issues.")
            else:
                for symbol, items in issues.items():
                    st.markdown(f"### 🔎 {symbol}")
                    for it in items:
                        st.write(f"- **{it.code}** (line {it.line}): {it.message}")

    # ================= TESTS =================
    with tab_tests:
        render_test_dashboard()

else:
    st.info("Upload a Python file to start.")