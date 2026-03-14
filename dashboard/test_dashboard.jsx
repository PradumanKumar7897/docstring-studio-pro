import { useState, useEffect, useRef } from "react";

// ── Mock test data (replace with pytest --json-report output) ──
const TEST_SUITES = [
  {
    id: "parser",
    label: "Parser Tests",
    icon: "⚙",
    color: "#38bdf8",
    tests: [
      { name: "test_single_function_found", status: "pass", duration: 12 },
      { name: "test_function_name_extracted", status: "pass", duration: 8 },
      { name: "test_function_type_label", status: "pass", duration: 7 },
      { name: "test_class_detected", status: "pass", duration: 9 },
      { name: "test_class_name_extracted", status: "pass", duration: 8 },
      { name: "test_multiple_items_in_complex_code", status: "pass", duration: 14 },
      { name: "test_empty_code_returns_empty_list", status: "pass", duration: 5 },
      { name: "test_args_list_present", status: "pass", duration: 9 },
      { name: "test_arg_names_correct", status: "pass", duration: 10 },
      { name: "test_arg_type_annotations", status: "pass", duration: 11 },
      { name: "test_no_args_function", status: "pass", duration: 7 },
      { name: "test_self_excluded_from_method_args", status: "pass", duration: 8 },
      { name: "test_return_type_present", status: "pass", duration: 7 },
      { name: "test_return_type_correct", status: "pass", duration: 8 },
      { name: "test_no_return_annotation", status: "pass", duration: 6 },
      { name: "test_no_docstring_is_none_or_empty", status: "pass", duration: 8 },
      { name: "test_existing_docstring_detected", status: "pass", duration: 9 },
      { name: "test_async_function_detected", status: "pass", duration: 10 },
      { name: "test_async_function_args", status: "pass", duration: 9 },
      { name: "test_invalid_python_raises_or_returns_empty", status: "pass", duration: 6 },
      { name: "test_returns_list_type", status: "pass", duration: 5 },
      { name: "test_each_item_is_dict", status: "pass", duration: 7 },
    ],
  },
  {
    id: "generation",
    label: "Generation Tests",
    icon: "✦",
    color: "#a78bfa",
    tests: [
      { name: "test_returns_string", status: "pass", duration: 6 },
      { name: "test_not_empty", status: "pass", duration: 7 },
      { name: "test_triple_quoted_or_clean_string", status: "pass", duration: 8 },
      { name: "test_google_has_args_section", status: "pass", duration: 9 },
      { name: "test_google_has_returns_section", status: "pass", duration: 8 },
      { name: "test_google_arg_name_present", status: "pass", duration: 9 },
      { name: "test_google_no_args_no_args_section", status: "pass", duration: 7 },
      { name: "test_numpy_has_parameters_section", status: "pass", duration: 10 },
      { name: "test_numpy_has_returns_section", status: "pass", duration: 9 },
      { name: "test_numpy_dashes_under_section", status: "pass", duration: 8 },
      { name: "test_rest_param_tag", status: "pass", duration: 9 },
      { name: "test_rest_return_tag", status: "pass", duration: 8 },
      { name: "test_rest_type_tag", status: "pass", duration: 8 },
      { name: "test_class_docstring_generated", status: "pass", duration: 7 },
      { name: "test_class_name_in_output", status: "pass", duration: 6 },
      { name: "test_output_is_valid_python", status: "pass", duration: 18 },
      { name: "test_docstring_inserted", status: "pass", duration: 15 },
      { name: "test_overwrite_false_preserves_existing", status: "pass", duration: 14 },
      { name: "test_overwrite_true_replaces_existing", status: "pass", duration: 16 },
      { name: "test_complex_code_all_items_documented", status: "pass", duration: 22 },
      { name: "test_google_template_exists", status: "pass", duration: 5 },
      { name: "test_numpy_template_exists", status: "pass", duration: 5 },
      { name: "test_rest_template_exists", status: "pass", duration: 5 },
      { name: "test_unknown_style_raises_or_defaults", status: "pass", duration: 6 },
    ],
  },
  {
    id: "validation",
    label: "Validation Tests",
    icon: "✔",
    color: "#34d399",
    tests: [
      { name: "test_default_ignore_codes_is_list", status: "pass", duration: 5 },
      { name: "test_custom_ignore_codes_stored", status: "pass", duration: 5 },
      { name: "test_config_is_instantiable", status: "pass", duration: 4 },
      { name: "test_returns_dict", status: "pass", duration: 18 },
      { name: "test_clean_code_no_issues", status: "pass", duration: 22 },
      { name: "test_missing_docstring_produces_issues", status: "pass", duration: 19 },
      { name: "test_keys_are_strings", status: "pass", duration: 17 },
      { name: "test_issue_has_code_attr", status: "pass", duration: 20 },
      { name: "test_issue_has_message_attr", status: "pass", duration: 19 },
      { name: "test_issue_has_line_attr", status: "pass", duration: 18 },
      { name: "test_issue_code_is_string", status: "pass", duration: 18 },
      { name: "test_issue_line_is_int", status: "pass", duration: 19 },
      { name: "test_ignored_code_not_in_results", status: "pass", duration: 25 },
      { name: "test_missing_docstring_detected", status: "pass", duration: 20 },
      { name: "test_empty_docstring_flagged", status: "pass", duration: 18 },
      { name: "test_multiline_function_validated", status: "pass", duration: 19 },
    ],
  },
  {
    id: "integration",
    label: "Integration Tests",
    icon: "⬡",
    color: "#fb923c",
    tests: [
      { name: "test_pipeline_returns_all_keys", status: "pass", duration: 35 },
      { name: "test_updated_code_is_valid_python", status: "pass", duration: 38 },
      { name: "test_items_list_not_empty", status: "pass", duration: 34 },
      { name: "test_docstring_in_updated_code", status: "pass", duration: 36 },
      { name: "test_all_styles_produce_valid_python", status: "pass", duration: 88 },
      { name: "test_multiple_items_all_documented", status: "pass", duration: 52 },
      { name: "test_issues_dict_returned", status: "pass", duration: 49 },
      { name: "test_overwrite_false_no_duplicate_docstrings", status: "pass", duration: 40 },
      { name: "test_overwrite_true_valid_python", status: "pass", duration: 41 },
      { name: "test_generate_docstring_ai_called", status: "pass", duration: 12 },
      { name: "test_ai_config_provider_stored", status: "pass", duration: 6 },
      { name: "test_ai_config_temperature_stored", status: "pass", duration: 6 },
      { name: "test_ai_error_handled_gracefully", status: "pass", duration: 14 },
      { name: "test_router_imports", status: "pass", duration: 8 },
      { name: "test_router_returns_callable_or_result", status: "pass", duration: 7 },
      { name: "test_cli_importable", status: "pass", duration: 9 },
      { name: "test_cli_is_callable", status: "pass", duration: 8 },
      { name: "test_cli_invocation_with_runner", status: "pass", duration: 28 },
      { name: "test_infer_importable", status: "pass", duration: 7 },
      { name: "test_utils_importable", status: "pass", duration: 6 },
    ],
  },
  {
    id: "ui",
    label: "UI Tests",
    icon: "◈",
    color: "#f472b6",
    tests: [
      { name: "test_reset_clears_editor_code", status: "pass", duration: 10 },
      { name: "test_reset_preserves_unrelated_keys", status: "pass", duration: 9 },
      { name: "test_side_diff_creates_two_columns", status: "pass", duration: 8 },
      { name: "test_side_diff_accepts_two_strings", status: "pass", duration: 5 },
      { name: "test_local_provider_sets_engine_used", status: "pass", duration: 12 },
      { name: "test_local_provider_docstring_not_empty", status: "pass", duration: 13 },
      { name: "test_ai_provider_result_stored", status: "pass", duration: 11 },
      { name: "test_ai_error_stored_in_item", status: "pass", duration: 10 },
      { name: "test_editor_code_initialized_on_first_upload", status: "pass", duration: 6 },
      { name: "test_updated_code_stored_after_generation", status: "pass", duration: 6 },
      { name: "test_parsed_items_stored_after_generation", status: "pass", duration: 6 },
      { name: "test_validation_results_stored", status: "pass", duration: 6 },
      { name: "test_valid_docstring_style[google]", status: "pass", duration: 4 },
      { name: "test_valid_docstring_style[numpy]", status: "pass", duration: 4 },
      { name: "test_valid_docstring_style[rest]", status: "pass", duration: 4 },
      { name: "test_valid_ai_provider[local]", status: "pass", duration: 4 },
      { name: "test_valid_ai_provider[openai]", status: "pass", duration: 4 },
      { name: "test_valid_ai_provider[groq]", status: "pass", duration: 4 },
      { name: "test_valid_ai_provider[gemini]", status: "pass", duration: 4 },
      { name: "test_temperature_in_range[0.0]", status: "pass", duration: 3 },
      { name: "test_temperature_in_range[0.5]", status: "pass", duration: 3 },
      { name: "test_download_filename_transformation", status: "pass", duration: 5 },
      { name: "test_download_content_is_bytes", status: "pass", duration: 5 },
    ],
  },
];

const STATUS_COLOR = { pass: "#22c55e", fail: "#ef4444", skip: "#eab308", error: "#f97316" };
const STATUS_BG = { pass: "rgba(34,197,94,0.12)", fail: "rgba(239,68,68,0.12)", skip: "rgba(234,179,8,0.12)", error: "rgba(249,115,22,0.12)" };
const STATUS_LABEL = { pass: "PASS", fail: "FAIL", skip: "SKIP", error: "ERR" };

// Animated counter hook
function useCounter(target, duration = 1200, active = false) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!active) return;
    let start = null;
    const step = (ts) => {
      if (!start) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      setVal(Math.floor(p * target));
      if (p < 1) requestAnimationFrame(step);
      else setVal(target);
    };
    requestAnimationFrame(step);
  }, [target, duration, active]);
  return val;
}

// Donut chart SVG
function Donut({ pass, total, color, size = 64 }) {
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const arc = total > 0 ? (pass / total) * circ : 0;
  return (
    <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#1e293b" strokeWidth={6} />
      <circle
        cx={size / 2} cy={size / 2} r={r} fill="none"
        stroke={color} strokeWidth={6}
        strokeDasharray={`${arc} ${circ - arc}`}
        strokeLinecap="round"
        style={{ transition: "stroke-dasharray 1.2s cubic-bezier(.4,0,.2,1)" }}
      />
    </svg>
  );
}

// Sparkline bar
function Sparkbar({ tests, color }) {
  const max = Math.max(...tests.map((t) => t.duration), 1);
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 2, height: 28 }}>
      {tests.slice(-20).map((t, i) => (
        <div
          key={i}
          title={`${t.name}: ${t.duration}ms`}
          style={{
            width: 6, borderRadius: 2,
            height: `${Math.max(4, (t.duration / max) * 28)}px`,
            background: t.status === "pass" ? color : STATUS_COLOR[t.status],
            opacity: 0.85,
            transition: "height 0.6s ease",
          }}
        />
      ))}
    </div>
  );
}

// ── Suite Card ────────────────────────────────────────
function SuiteCard({ suite, selected, onClick, animated }) {
  const pass = suite.tests.filter((t) => t.status === "pass").length;
  const fail = suite.tests.filter((t) => t.status === "fail").length;
  const total = suite.tests.length;
  const pct = total > 0 ? Math.round((pass / total) * 100) : 0;
  const cntPass = useCounter(pass, 900, animated);
  const cntTotal = useCounter(total, 900, animated);

  return (
    <div
      onClick={onClick}
      style={{
        background: selected ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.025)",
        border: `1px solid ${selected ? suite.color : "rgba(255,255,255,0.08)"}`,
        borderRadius: 16,
        padding: "18px 20px",
        cursor: "pointer",
        transition: "all 0.22s ease",
        boxShadow: selected ? `0 0 24px ${suite.color}33` : "none",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Glow accent */}
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0, height: 2,
        background: selected ? `linear-gradient(90deg, transparent, ${suite.color}, transparent)` : "transparent",
        transition: "all 0.3s",
      }} />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
        <div>
          <div style={{ fontSize: 11, letterSpacing: 2, color: suite.color, fontFamily: "monospace", marginBottom: 4 }}>
            {suite.icon} {suite.id.toUpperCase()}
          </div>
          <div style={{ fontSize: 14, fontWeight: 600, color: "#e2e8f0", lineHeight: 1.2 }}>{suite.label}</div>
        </div>
        <Donut pass={pass} total={total} color={suite.color} size={52} />
      </div>

      <Sparkbar tests={suite.tests} color={suite.color} />

      <div style={{ display: "flex", gap: 12, marginTop: 12, alignItems: "center" }}>
        <div style={{ fontSize: 24, fontWeight: 700, color: suite.color, fontFamily: "monospace" }}>
          {animated ? cntPass : pass}
          <span style={{ fontSize: 13, color: "#64748b", fontWeight: 400 }}>/{animated ? cntTotal : total}</span>
        </div>
        <div style={{
          fontSize: 11, fontWeight: 700, letterSpacing: 1,
          color: pct === 100 ? "#22c55e" : pct > 80 ? "#eab308" : "#ef4444",
          background: pct === 100 ? "rgba(34,197,94,0.12)" : "rgba(239,68,68,0.1)",
          padding: "3px 8px", borderRadius: 20,
        }}>
          {pct}%
        </div>
        {fail > 0 && (
          <div style={{ fontSize: 11, color: "#ef4444", background: "rgba(239,68,68,0.1)", padding: "3px 8px", borderRadius: 20 }}>
            {fail} failed
          </div>
        )}
      </div>
    </div>
  );
}

// ── Test Row ─────────────────────────────────────────
function TestRow({ test, color, idx }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), idx * 25);
    return () => clearTimeout(t);
  }, [idx]);

  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 12,
      padding: "9px 14px", borderRadius: 8,
      background: "rgba(255,255,255,0.022)",
      border: "1px solid rgba(255,255,255,0.05)",
      opacity: visible ? 1 : 0,
      transform: visible ? "translateX(0)" : "translateX(-12px)",
      transition: "all 0.3s ease",
      marginBottom: 4,
    }}>
      <div style={{
        width: 7, height: 7, borderRadius: "50%",
        background: STATUS_COLOR[test.status],
        boxShadow: `0 0 6px ${STATUS_COLOR[test.status]}88`,
        flexShrink: 0,
      }} />
      <div style={{
        fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
        color: STATUS_COLOR[test.status],
        background: STATUS_BG[test.status],
        padding: "2px 7px", borderRadius: 6, flexShrink: 0,
      }}>
        {STATUS_LABEL[test.status]}
      </div>
      <div style={{ fontSize: 12, color: "#94a3b8", fontFamily: "monospace", flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {test.name}
      </div>
      <div style={{ fontSize: 11, color: "#475569", fontFamily: "monospace", flexShrink: 0 }}>
        {test.duration}ms
      </div>
    </div>
  );
}

// ── Timeline / Duration Chart ─────────────────────────
function DurationChart({ suites }) {
  const allTests = suites.flatMap((s) => s.tests.map((t) => ({ ...t, suiteColor: s.color, suiteId: s.id })));
  const sorted = [...allTests].sort((a, b) => b.duration - a.duration).slice(0, 15);
  const max = sorted[0]?.duration || 1;

  return (
    <div>
      {sorted.map((t, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
          <div style={{ fontSize: 10, color: "#475569", fontFamily: "monospace", width: 60, textAlign: "right", flexShrink: 0 }}>
            {t.suiteId}
          </div>
          <div style={{ flex: 1, background: "rgba(255,255,255,0.05)", borderRadius: 4, height: 14, overflow: "hidden" }}>
            <div style={{
              height: "100%", borderRadius: 4,
              width: `${(t.duration / max) * 100}%`,
              background: `linear-gradient(90deg, ${t.suiteColor}99, ${t.suiteColor})`,
              transition: "width 1.2s cubic-bezier(.4,0,.2,1)",
            }} />
          </div>
          <div style={{ fontSize: 10, color: "#64748b", fontFamily: "monospace", width: 36, flexShrink: 0 }}>
            {t.duration}ms
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Coverage Radar ────────────────────────────────────
function RadarChart({ suites }) {
  const cx = 80, cy = 80, r = 58;
  const n = suites.length;
  const pts = suites.map((s, i) => {
    const angle = (i / n) * Math.PI * 2 - Math.PI / 2;
    const pass = s.tests.filter((t) => t.status === "pass").length;
    const pct = s.tests.length > 0 ? pass / s.tests.length : 0;
    return {
      x: cx + Math.cos(angle) * r * pct,
      y: cy + Math.sin(angle) * r * pct,
      lx: cx + Math.cos(angle) * (r + 14),
      ly: cy + Math.sin(angle) * (r + 14),
      color: s.color,
      label: s.icon,
      pct,
    };
  });
  const poly = pts.map((p) => `${p.x},${p.y}`).join(" ");

  // Grid rings
  const rings = [0.25, 0.5, 0.75, 1];

  return (
    <svg width={160} height={160} style={{ overflow: "visible" }}>
      {rings.map((scale, i) => {
        const ringPts = suites.map((_, j) => {
          const angle = (j / n) * Math.PI * 2 - Math.PI / 2;
          return `${cx + Math.cos(angle) * r * scale},${cy + Math.sin(angle) * r * scale}`;
        }).join(" ");
        return <polygon key={i} points={ringPts} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={1} />;
      })}

      {suites.map((_, i) => {
        const angle = (i / n) * Math.PI * 2 - Math.PI / 2;
        return <line key={i} x1={cx} y1={cy} x2={cx + Math.cos(angle) * r} y2={cy + Math.sin(angle) * r} stroke="rgba(255,255,255,0.08)" strokeWidth={1} />;
      })}

      <polygon points={poly} fill="rgba(99,179,237,0.15)" stroke="#63b3ed" strokeWidth={1.5} />

      {pts.map((p, i) => (
        <g key={i}>
          <circle cx={p.x} cy={p.y} r={4} fill={p.color} />
          <text x={p.lx} y={p.ly} textAnchor="middle" dominantBaseline="middle" fontSize={11} fill={p.color}>{p.label}</text>
        </g>
      ))}
    </svg>
  );
}

// ══════════════════════════════════════════════════════
//  Main Dashboard
// ══════════════════════════════════════════════════════
export default function TestDashboard() {
  const [selected, setSelected] = useState(TEST_SUITES[0].id);
  const [animated, setAnimated] = useState(false);
  const [tab, setTab] = useState("results"); // results | duration | overview

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 200);
    return () => clearTimeout(t);
  }, []);

  const activeSuite = TEST_SUITES.find((s) => s.id === selected);
  const totalPass = TEST_SUITES.reduce((a, s) => a + s.tests.filter((t) => t.status === "pass").length, 0);
  const totalTests = TEST_SUITES.reduce((a, s) => a + s.tests.length, 0);
  const totalFail = TEST_SUITES.reduce((a, s) => a + s.tests.filter((t) => t.status === "fail").length, 0);
  const totalDur = TEST_SUITES.reduce((a, s) => a + s.tests.reduce((b, t) => b + t.duration, 0), 0);

  const totalPassCnt = useCounter(totalPass, 1200, animated);
  const totalTestsCnt = useCounter(totalTests, 1200, animated);

  const font = "'IBM Plex Mono', 'Courier New', monospace";

  return (
    <div style={{
      minHeight: "100vh",
      background: "#080f1a",
      color: "#e2e8f0",
      fontFamily: "'Inter', 'Segoe UI', sans-serif",
      padding: "0",
    }}>
      {/* ── Header ── */}
      <div style={{
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        padding: "20px 32px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "rgba(255,255,255,0.015)",
        backdropFilter: "blur(20px)",
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#22c55e", boxShadow: "0 0 10px #22c55e" }} />
            <span style={{ fontSize: 11, letterSpacing: 3, color: "#22c55e", fontFamily: font }}>
              DOCSTRING STUDIO PRO
            </span>
          </div>
          <h1 style={{ margin: "4px 0 0", fontSize: 20, fontWeight: 700, letterSpacing: -0.5 }}>
            Test Results Dashboard
          </h1>
        </div>

        {/* Global stats */}
        <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
          {[
            { label: "PASSED", val: animated ? totalPassCnt : totalPass, color: "#22c55e" },
            { label: "TOTAL", val: animated ? totalTestsCnt : totalTests, color: "#94a3b8" },
            { label: "FAILED", val: totalFail, color: "#ef4444" },
            { label: "DURATION", val: `${(totalDur / 1000).toFixed(1)}s`, color: "#38bdf8" },
          ].map((s) => (
            <div key={s.label} style={{ textAlign: "center" }}>
              <div style={{ fontSize: 22, fontWeight: 700, color: s.color, fontFamily: font }}>{s.val}</div>
              <div style={{ fontSize: 9, letterSpacing: 2, color: "#475569" }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ padding: "24px 32px" }}>
        {/* ── Suite Cards ── */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5,1fr)", gap: 14, marginBottom: 28 }}>
          {TEST_SUITES.map((suite) => (
            <SuiteCard
              key={suite.id}
              suite={suite}
              selected={selected === suite.id}
              onClick={() => setSelected(suite.id)}
              animated={animated}
            />
          ))}
        </div>

        {/* ── Tabs ── */}
        <div style={{ display: "flex", gap: 4, marginBottom: 18, borderBottom: "1px solid rgba(255,255,255,0.07)", paddingBottom: 0 }}>
          {[
            { id: "results", label: "Test Results" },
            { id: "duration", label: "Duration Analysis" },
            { id: "overview", label: "Coverage Overview" },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              style={{
                background: "none", border: "none", cursor: "pointer",
                padding: "8px 18px",
                fontSize: 13, fontWeight: 500,
                color: tab === t.id ? activeSuite.color : "#64748b",
                borderBottom: tab === t.id ? `2px solid ${activeSuite.color}` : "2px solid transparent",
                marginBottom: -1,
                transition: "all 0.2s",
              }}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* ── Content ── */}
        {tab === "results" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: 20 }}>
            {/* Test list */}
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
                <span style={{ fontSize: 11, color: activeSuite.color, fontFamily: font, letterSpacing: 2 }}>
                  {activeSuite.icon} {activeSuite.label.toUpperCase()}
                </span>
                <div style={{ flex: 1, height: 1, background: "rgba(255,255,255,0.06)" }} />
                <span style={{ fontSize: 11, color: "#475569", fontFamily: font }}>
                  {activeSuite.tests.length} tests
                </span>
              </div>
              <div style={{ maxHeight: 480, overflowY: "auto", paddingRight: 4 }}>
                {activeSuite.tests.map((t, i) => (
                  <TestRow key={t.name} test={t} color={activeSuite.color} idx={i} />
                ))}
              </div>
            </div>

            {/* Side panel */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {/* Pass rate */}
              <div style={{
                background: "rgba(255,255,255,0.025)",
                border: "1px solid rgba(255,255,255,0.07)",
                borderRadius: 14, padding: 18, textAlign: "center",
              }}>
                <div style={{ fontSize: 11, letterSpacing: 2, color: "#64748b", marginBottom: 10 }}>PASS RATE</div>
                <div style={{ position: "relative", display: "inline-block" }}>
                  <Donut
                    pass={activeSuite.tests.filter((t) => t.status === "pass").length}
                    total={activeSuite.tests.length}
                    color={activeSuite.color}
                    size={110}
                  />
                  <div style={{
                    position: "absolute", inset: 0, display: "flex",
                    alignItems: "center", justifyContent: "center",
                    fontSize: 20, fontWeight: 700, color: activeSuite.color, fontFamily: font,
                  }}>
                    {Math.round((activeSuite.tests.filter((t) => t.status === "pass").length / activeSuite.tests.length) * 100)}%
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div style={{
                background: "rgba(255,255,255,0.025)",
                border: "1px solid rgba(255,255,255,0.07)",
                borderRadius: 14, padding: 18,
              }}>
                <div style={{ fontSize: 11, letterSpacing: 2, color: "#64748b", marginBottom: 12 }}>SUITE STATS</div>
                {[
                  { label: "Total Tests", val: activeSuite.tests.length, color: "#94a3b8" },
                  { label: "Passed", val: activeSuite.tests.filter((t) => t.status === "pass").length, color: "#22c55e" },
                  { label: "Failed", val: activeSuite.tests.filter((t) => t.status === "fail").length, color: "#ef4444" },
                  {
                    label: "Avg Duration",
                    val: `${Math.round(activeSuite.tests.reduce((a, t) => a + t.duration, 0) / activeSuite.tests.length)}ms`,
                    color: "#38bdf8",
                  },
                  {
                    label: "Total Duration",
                    val: `${activeSuite.tests.reduce((a, t) => a + t.duration, 0)}ms`,
                    color: "#a78bfa",
                  },
                ].map((s) => (
                  <div key={s.label} style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                    <span style={{ fontSize: 12, color: "#64748b" }}>{s.label}</span>
                    <span style={{ fontSize: 12, fontWeight: 600, color: s.color, fontFamily: font }}>{s.val}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {tab === "duration" && (
          <div style={{
            background: "rgba(255,255,255,0.025)",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: 14, padding: 24,
          }}>
            <div style={{ fontSize: 11, letterSpacing: 2, color: "#64748b", marginBottom: 20 }}>TOP 15 SLOWEST TESTS</div>
            <DurationChart suites={TEST_SUITES} />
          </div>
        )}

        {tab === "overview" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            {/* Radar */}
            <div style={{
              background: "rgba(255,255,255,0.025)",
              border: "1px solid rgba(255,255,255,0.07)",
              borderRadius: 14, padding: 24,
              display: "flex", flexDirection: "column", alignItems: "center",
            }}>
              <div style={{ fontSize: 11, letterSpacing: 2, color: "#64748b", marginBottom: 20 }}>SUITE COVERAGE RADAR</div>
              <RadarChart suites={TEST_SUITES} />
              <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 16, justifyContent: "center" }}>
                {TEST_SUITES.map((s) => (
                  <div key={s.id} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: s.color }}>
                    <div style={{ width: 8, height: 8, borderRadius: "50%", background: s.color }} />
                    {s.icon} {s.id}
                  </div>
                ))}
              </div>
            </div>

            {/* Summary table */}
            <div style={{
              background: "rgba(255,255,255,0.025)",
              border: "1px solid rgba(255,255,255,0.07)",
              borderRadius: 14, padding: 24,
            }}>
              <div style={{ fontSize: 11, letterSpacing: 2, color: "#64748b", marginBottom: 16 }}>SUITE SUMMARY</div>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.07)" }}>
                    {["Suite", "Tests", "Pass", "Fail", "Pass%", "Duration"].map((h) => (
                      <th key={h} style={{ padding: "6px 10px", color: "#475569", fontWeight: 500, textAlign: "left", letterSpacing: 0.5 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {TEST_SUITES.map((s) => {
                    const p = s.tests.filter((t) => t.status === "pass").length;
                    const f = s.tests.filter((t) => t.status === "fail").length;
                    const pct = Math.round((p / s.tests.length) * 100);
                    const dur = s.tests.reduce((a, t) => a + t.duration, 0);
                    return (
                      <tr key={s.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)", cursor: "pointer" }}
                        onClick={() => { setSelected(s.id); setTab("results"); }}>
                        <td style={{ padding: "8px 10px", color: s.color, fontFamily: font }}>{s.icon} {s.id}</td>
                        <td style={{ padding: "8px 10px", color: "#94a3b8" }}>{s.tests.length}</td>
                        <td style={{ padding: "8px 10px", color: "#22c55e" }}>{p}</td>
                        <td style={{ padding: "8px 10px", color: f > 0 ? "#ef4444" : "#475569" }}>{f}</td>
                        <td style={{ padding: "8px 10px", color: pct === 100 ? "#22c55e" : "#eab308", fontWeight: 600 }}>{pct}%</td>
                        <td style={{ padding: "8px 10px", color: "#64748b", fontFamily: font }}>{dur}ms</td>
                      </tr>
                    );
                  })}
                  <tr style={{ borderTop: "1px solid rgba(255,255,255,0.1)", fontWeight: 700 }}>
                    <td style={{ padding: "8px 10px", color: "#e2e8f0" }}>Total</td>
                    <td style={{ padding: "8px 10px", color: "#e2e8f0" }}>{totalTests}</td>
                    <td style={{ padding: "8px 10px", color: "#22c55e" }}>{totalPass}</td>
                    <td style={{ padding: "8px 10px", color: totalFail > 0 ? "#ef4444" : "#475569" }}>{totalFail}</td>
                    <td style={{ padding: "8px 10px", color: "#22c55e" }}>{Math.round((totalPass / totalTests) * 100)}%</td>
                    <td style={{ padding: "8px 10px", color: "#38bdf8", fontFamily: font }}>{totalDur}ms</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ── Footer ── */}
        <div style={{ marginTop: 24, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 10, color: "#334155", fontFamily: font, letterSpacing: 1 }}>
            RUN: pytest tests/ -v --tb=short
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            {[{ c: "#22c55e", l: "PASS" }, { c: "#ef4444", l: "FAIL" }, { c: "#eab308", l: "SKIP" }, { c: "#f97316", l: "ERR" }].map((s) => (
              <div key={s.l} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 10, color: s.c }}>
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: s.c }} /> {s.l}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
