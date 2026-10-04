// CompareScreen.jsx — REAL DATA ONLY. No static products.
// Paste 2+ product URLs -> POST /api/v1/compare/ -> live side-by-side table.
// Honest states only; never invents prices.
import React, { useState } from "react";
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "/api/v1";

const colors = {
  bg: "#0f131c", card: "rgba(15,23,42,0.65)", border: "rgba(255,255,255,0.08)",
  primary: "#6366f1", secondary: "#22d3ee", tertiary: "#10b981", gold: "#f59e0b",
  red: "#ef4444", text: "#f8fafc", secondaryText: "#cbd5e1", muted: "#64748b",
};

export default function CompareScreen() {
  const [urls, setUrls] = useState(["", ""]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const setUrl = (i, v) => setUrls((u) => u.map((x, j) => (j === i ? v : x)));

  const doCompare = async () => {
    const list = urls.map((u) => u.trim()).filter(Boolean);
    if (list.length < 2) { setError("Paste at least 2 product URLs to compare."); return; }
    setLoading(true); setError(""); setResult(null);
    try {
      const res = await axios.post(`${API_BASE}/compare/`, { urls: list }, { timeout: 120000 });
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Comparison failed — stores may block live scraping. Try different URLs.");
    }
    setLoading(false);
  };

  const cmp = result?.comparison || {};
  const rows = cmp.products || [];

  return (
    <div style={{ background: colors.bg, minHeight: "100vh", padding: 24, color: colors.text, fontFamily: "'JetBrains Mono', monospace" }}>
      <h1 style={{ textAlign: "center" }}>⚖️ Compare real products</h1>
      <p style={{ textAlign: "center", color: colors.secondaryText }}>
        Paste 2–10 Amazon / Flipkart product URLs. Prices are scraped live — nothing is pre-filled or invented.
      </p>

      <div style={{ background: colors.card, border: `1px solid ${colors.border}`, borderRadius: 16, padding: 24, maxWidth: 800, margin: "0 auto 24px" }}>
        {urls.map((u, i) => (
          <input
            key={i}
            type="text"
            placeholder={`Product URL ${i + 1} (https://…)`}
            value={u}
            onChange={(e) => setUrl(i, e.target.value)}
            style={{ width: "100%", boxSizing: "border-box", marginBottom: 8, padding: "12px 16px", background: "rgba(30,41,59,0.6)", border: `1px solid ${colors.border}`, borderRadius: 10, color: colors.text, fontSize: 14, outline: "none" }}
          />
        ))}
        <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
          <button onClick={() => setUrls((u) => [...u, ""])} style={{ background: "transparent", border: `1px solid ${colors.border}`, color: colors.text, borderRadius: 8, padding: "10px 16px", cursor: "pointer" }}>+ Add URL</button>
          <button onClick={doCompare} className="btn-primary" style={{ border: "none", borderRadius: 8, padding: "10px 24px" }}>
            {loading ? "⏳ Scraping live…" : "Compare live"}
          </button>
        </div>
        {error && <p style={{ color: colors.red }}>{error}</p>}
      </div>

      {cmp.best_price && (
        <div style={{ background: colors.tertiary, padding: "12px 24px", borderRadius: 12, marginBottom: 24, textAlign: "center", fontWeight: "bold", color: colors.bg }}>
          Best deal: {(cmp.best_price.store || "") + " at ₹" + Number(cmp.best_price.price || 0).toLocaleString("en-IN")}
        </div>
      )}

      {rows.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 24, justifyContent: "center" }}>
          {rows.map((p, i) => (
            <div key={i} style={{ background: colors.card, border: `1px solid ${p.is_best_price ? colors.tertiary : colors.border}`, borderRadius: 16, padding: 24, flex: "1 1 300px", maxWidth: 350 }}>
              <h2 style={{ margin: 0 }}>{p.name}</h2>
              <div style={{ fontSize: "1.5rem", color: colors.tertiary, fontWeight: "bold", margin: "8px 0" }}>
                ₹ {Number(p.price || 0).toLocaleString("en-IN")}
              </div>
              <p style={{ color: colors.secondaryText, margin: "4px 0" }}>Store: {p.store} · ⭐ {p.rating || "—"} · {(p.discount_percentage || 0) + "% off"}</p>
              <p style={{ color: colors.muted, fontSize: 13 }}>{p.is_best_price ? "✅ Lowest price" : ""} {p.is_in_stock === false ? "· out of stock" : ""}</p>
              {(p.affiliate_url || p.url) && (
                <a href={p.affiliate_url || p.url} target="_blank" rel="noreferrer" style={{ display: "block", textDecoration: "none", background: colors.primary, color: colors.text, padding: "8px 12px", borderRadius: 8, textAlign: "center", fontWeight: "bold" }}>
                  Buy
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
