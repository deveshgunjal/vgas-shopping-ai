// ProductDetailScreen.jsx — REAL DATA ONLY. No mocked product.
// Fetches live product from backend by ID (?url= for live URL scrape).
// Honest states: loading / live / unavailable. Never invents prices.
import React, { useState, useEffect } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "/api/v1";

export default function ProductDetailScreen() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const urlParam = searchParams.get("url") || "";

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [fromCache, setFromCache] = useState(false);
  const [pasteUrl, setPasteUrl] = useState(urlParam);
  const [specOpen, setSpecOpen] = useState(false);

  const loadById = async (pid) => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/products/by-id`, { params: { product_id: pid } });
      setProduct(res.data.product);
      setFromCache(!!res.data.from_cache);
    } catch (e) {
      setError(e.response?.data?.detail || `Live data unavailable for item "${pid}". Paste a real product URL below for a live scrape.`);
    }
    setLoading(false);
  };

  const loadByUrl = async (url) => {
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/products/by-url`, { params: { url: url.trim() } });
      setProduct(res.data.product);
      setFromCache(!!res.data.from_cache);
    } catch (e) {
      setError(e.response?.data?.detail || "Could not scrape that URL (store may block bots). Try another link.");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (urlParam) loadByUrl(urlParam);
    else if (id) loadById(id);
    else { setLoading(false); setError("No product selected."); }
  }, [id, urlParam]);

  const colors = {
    bg: "#0f131c", card: "rgba(15,23,42,0.65)", border: "rgba(255,255,255,0.08)",
    primary: "#6366f1", secondary: "#22d3ee", tertiary: "#10b981", gold: "#f59e0b",
    red: "#ef4444", text: "#f8fafc", secondaryText: "#cbd5e1", muted: "#64748b", green: "#10b981",
  };
  const cardStyle = { background: colors.card, border: `1px solid ${colors.border}`, borderRadius: 16, padding: "16px 24px", marginBottom: 24, color: colors.text };

  return (
    <div style={{ background: colors.bg, minHeight: "100vh", padding: 24, fontFamily: "Arial, sans-serif" }}>
      {/* Live URL scrape box — always real */}
      <div style={cardStyle}>
        <h2 style={{ margin: "0 0 12px 0", color: colors.text }}>🔍 Live product lookup</h2>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            type="text"
            placeholder="Paste Amazon / Flipkart product URL for a live scrape..."
            value={pasteUrl}
            onChange={(e) => setPasteUrl(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") loadByUrl(pasteUrl); }}
            style={{ flex: 1, padding: "12px 16px", background: "rgba(30,41,59,0.6)", border: `1px solid ${colors.border}`, borderRadius: 10, color: colors.text, fontSize: 14, outline: "none" }}
          />
          <button onClick={() => loadByUrl(pasteUrl)} className="btn-primary" style={{ padding: "12px 24px", border: "none" }}>Scrape</button>
        </div>
      </div>

      {loading && <div style={cardStyle}>⏳ Fetching live product data from backend…</div>}

      {!loading && error && (
        <div style={{ ...cardStyle, border: `1px solid ${colors.red}` }}>
          <h2 style={{ margin: "0 0 8px 0", color: colors.red }}>⚠️ Live data unavailable</h2>
          <p style={{ color: colors.secondaryText }}>{error}</p>
          <p style={{ color: colors.muted, fontSize: 13 }}>No demo or sample prices are shown — only verified live data appears on this page.</p>
        </div>
      )}

      {!loading && product && (
        <>
          <div style={cardStyle}>
            <h1 style={{ margin: 0, color: colors.text }}>{product.title || product.name || "Untitled product"}</h1>
            <div style={{ marginTop: 8, display: "flex", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
              {product.rating && <span style={{ color: colors.gold }}>★ {product.rating}</span>}
              {(() => {
                // The scrapers return 0.0 when they could not parse the price.
                // Showing "₹ 0" would dress a failure up as a real price.
                const p = Number(product.price);
                const o = Number(product.original_price);
                if (Number.isFinite(p) && p > 0) {
                  return <span style={{ fontWeight: "bold", color: colors.green, fontSize: "1.5rem" }}>₹ {p.toLocaleString("en-IN")}</span>;
                }
                return <span style={{ color: colors.muted, fontStyle: "italic" }}>price not parsed from the store page</span>;
              })()}
              {Number(product.original_price) > 0 && <span style={{ textDecoration: "line-through", color: colors.muted }}>₹ {Number(product.original_price).toLocaleString("en-IN")}</span>}
              {product.discount_percentage != null && <span style={{ background: colors.red, color: "#fff", borderRadius: 8, padding: "2px 6px", fontSize: "0.85rem", fontWeight: "bold" }}>-{product.discount_percentage}%</span>}
              {product.is_fake_discount && <span style={{ background: colors.red, color: "#fff", borderRadius: 8, padding: "2px 6px", fontSize: "0.85rem", fontWeight: "bold" }}>⚠️ {product.fake_discount_reason || "Possible fake discount"}</span>}
            </div>
            <p style={{ color: colors.muted, fontSize: 13, marginTop: 8 }}>
              Store: {product.store || product.store_domain || "unknown"} · {fromCache ? "served from cache" : "freshly scraped"} · {product.url && <a href={product.url} target="_blank" rel="noreferrer" style={{ color: colors.secondary }}>open original</a>}
            </p>
          </div>

          {product.affiliate_url && (
            <div style={cardStyle}>
              <h2 style={{ margin: "0 0 12px 0", color: colors.text }}>Buy from</h2>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "rgba(16,185,129,0.2)", padding: "8px 12px", borderRadius: 8 }}>
                <span>{product.store || "Store"}</span>
                <span>₹ {Number(product.price).toLocaleString("en-IN")}</span>
                <a href={product.affiliate_url} target="_blank" rel="noreferrer"><button className="btn-primary" style={{ border: "none", borderRadius: 6, padding: "6px 12px" }}>Buy</button></a>
              </div>
            </div>
          )}

          {product.specifications && Object.keys(product.specifications).length > 0 && (
            <div style={cardStyle}>
              <div style={{ display: "flex", justifyContent: "space-between", cursor: "pointer", padding: "8px 12px", background: "rgba(255,255,255,0.04)", borderRadius: 8 }} onClick={() => setSpecOpen(!specOpen)}>
                <span style={{ fontWeight: 600 }}>Specifications</span><span>{specOpen ? "▲" : "▼"}</span>
              </div>
              {specOpen && Object.entries(product.specifications).map(([k, v], i) => (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "6px 12px", borderBottom: `1px solid ${colors.border}` }}>
                  <span style={{ color: colors.secondaryText }}>{k}</span>
                  <span style={{ color: colors.text }}>{String(v)}</span>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
