// HomeScreen.jsx — REAL DATA ONLY.
//
// There is NO hardcoded product list anywhere in this file. Everything the user
// sees is fetched from the backend:
//   GET /api/v1/search/categories  -> category chips
//   GET /api/v1/search/loot-deals  -> live loot deals (real scrapers)
//   GET /api/v1/search/stores      -> real store count
//   GET /api/v1/admin/stats        -> real user/track counts
//
// When the live scrapers return nothing (stores block datacenter IPs), this
// screen says so plainly. It never substitutes sample products.
import React, { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { searchAPI, adminAPI } from "../api/services";

const C = {
  bg: "#0f131c",
  card: "rgba(15, 23, 42, 0.65)",
  border: "rgba(255, 255, 255, 0.08)",
  primary: "#6366f1",
  secondary: "#22d3ee",
  tertiary: "#10b981",
  gold: "#f59e0b",
  red: "#ef4444",
  text: "#f8fafc",
  textSecondary: "#cbd5e1",
  textMuted: "#64748b",
};

export default function HomeScreen() {
  const [search, setSearch] = useState("");
  const [deals, setDeals] = useState([]);
  const [categories, setCategories] = useState([]);
  const [liveStats, setLiveStats] = useState(null);
  const [storeCount, setStoreCount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [note, setNote] = useState("");

  const loadHomeData = useCallback(async () => {
    // Fast calls first — these read from the app config / database, no scraping.
    try {
      const [cats, stores, stats] = await Promise.all([
        searchAPI.categories(),
        searchAPI.stores(),
        adminAPI.stats(),
      ]);
      setCategories(cats.data.categories || []);
      const st = stores.data.stores || stores.data.supported_stores || [];
      setStoreCount(Array.isArray(st) ? st.length : null);
      setLiveStats(stats.data);
    } catch {
      setNote("Live stats / categories could not be loaded — is the API running on :8000?");
    }

    // Slow live scrape — this really hits Amazon/Flipkart/Ajio.
    try {
      const res = await searchAPI.lootDeals(12);
      const list = res.data.loot_deals || [];
      setDeals(list);
      if (list.length === 0) {
        setNote(
          "Live scrapers ran but returned 0 products: Amazon / Flipkart / Ajio block requests from this server's IP. No sample deals are shown in their place."
        );
      }
    } catch {
      setNote(
        "Live loot-deal scrape did not return in time. The stores likely rate-limited or blocked this IP. No sample deals are shown in their place."
      );
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadHomeData();
  }, [loadHomeData]);

  const handleSearch = async (e) => {
    if (e.key !== "Enter" || !search.trim()) return;
    setSearching(true);
    setNote("");
    try {
      const res = await searchAPI.search(search.trim());
      const list = res.data.results || [];
      setDeals(list);
      if (list.length === 0) {
        setNote(
          `Live search for "${search.trim()}" returned 0 results after querying the real stores — they blocked this server's IP. Nothing is faked to fill the gap.`
        );
      }
    } catch {
      setNote(`Search request to the backend failed. No results are shown.`);
      setDeals([]);
    }
    setSearching(false);
  };

  const stats = liveStats
    ? [
        { num: String(liveStats.total_users ?? 0), label: "Registered Users", color: C.primary },
        { num: String(liveStats.total_tracks ?? 0), label: "Tracked Products", color: C.secondary },
        { num: storeCount != null ? String(storeCount) : "—", label: "Live Scrapers", color: C.tertiary },
        { num: String(Object.keys(liveStats.deals_by_store || {}).length), label: "Stores Tracked", color: C.gold },
      ]
    : [];

  return (
    <div style={{ maxWidth: 1400, margin: "0 auto", padding: "0 24px" }}>
      {/* Hero */}
      <section style={{ padding: "40px 0 32px", textAlign: "center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 16px", borderRadius: 20, background: `${C.gold}15`, border: `1px solid ${C.gold}30`, color: C.gold, fontSize: 13, fontWeight: 600, marginBottom: 24 }}>
          ⚡ Live Price Intelligence
        </div>
        <h1 style={{ fontSize: "clamp(28px, 5vw, 56px)", fontWeight: 800, lineHeight: 1.1, marginBottom: 16, color: C.text }}>
          Compare <span className="shimmer-text">Real Prices</span> Across<br />Live Store Scrapers
        </h1>
        <p style={{ fontSize: 16, color: C.textSecondary, maxWidth: 620, margin: "0 auto 32px", lineHeight: 1.6 }}>
          Every price on this page is fetched live from the stores below. If a store blocks the
          request, the page shows nothing rather than inventing a product.
        </p>

        {/* Search */}
        <div style={{ maxWidth: 600, margin: "0 auto", position: "relative" }}>
          <div style={{ display: "flex", background: C.card, borderRadius: 16, border: `1px solid ${C.border}`, overflow: "hidden", backdropFilter: "blur(20px)" }}>
            <input
              type="text"
              placeholder="Search products... (e.g., iPhone 15, Samsung S24)"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={handleSearch}
              style={{ flex: 1, padding: "16px 24px", background: "transparent", border: "none", color: C.text, fontSize: 16, outline: "none" }}
            />
            <button onClick={handleSearch} className="btn-primary" style={{ padding: "16px 32px", border: "none" }}>
              {searching ? "Searching…" : "🔍 Search"}
            </button>
          </div>
        </div>

        {/* Live stats — only rendered when the API actually answered */}
        {stats.length > 0 && (
          <div style={{ display: "flex", justifyContent: "center", gap: 48, marginTop: 40, flexWrap: "wrap" }}>
            {stats.map((s, i) => (
              <div key={i} style={{ textAlign: "center" }}>
                <div style={{ fontSize: 28, fontWeight: 800, color: s.color }}>{s.num}</div>
                <div style={{ fontSize: 13, color: C.textSecondary, marginTop: 4 }}>{s.label}</div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Categories — from /search/categories */}
      {categories.length > 0 && (
        <section style={{ padding: "16px 0 32px" }}>
          <div style={{ display: "flex", gap: 12, overflowX: "auto", paddingBottom: 8 }} className="no-scrollbar">
            {categories.map((c, i) => (
              <div key={i} style={{ minWidth: 110, padding: "12px 16px", background: C.card, borderRadius: 12, border: `1px solid ${C.border}`, textAlign: "center", cursor: "pointer", transition: "all 0.2s", flexShrink: 0 }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = C.primary; e.currentTarget.style.transform = "translateY(-2px)"; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.transform = "translateY(0)"; }}
              >
                <div style={{ fontSize: 12, fontWeight: 600, color: C.text }}>{c.name}</div>
                <div style={{ fontSize: 11, color: C.textMuted, marginTop: 2 }}>{c.count} keywords</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Live deals */}
      <section style={{ padding: "32px 0" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
          <h2 style={{ fontSize: 24, fontWeight: 800, color: C.text }}>
            🔥 Loot Deals <span style={{ fontSize: 12, padding: "4px 10px", background: `${C.red}20`, color: C.red, borderRadius: 8, fontWeight: 600 }}>LIVE SCRAPE</span>
          </h2>
          <Link to="/compare" style={{ fontSize: 13, color: C.primary, textDecoration: "none", fontWeight: 600 }}>Compare URLs →</Link>
        </div>

        {(loading || searching) && (
          <div style={{ textAlign: "center", padding: 40 }}>
            <div style={{ display: "inline-block", width: 40, height: 40, border: `3px solid ${C.border}`, borderTopColor: C.primary, borderRadius: "50%", animation: "spin 1s linear infinite" }} />
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            <p style={{ color: C.textMuted, marginTop: 16, fontSize: 14 }}>
              Querying the real stores now — this takes 20-120s because it is a live scrape.
            </p>
          </div>
        )}

        {!loading && !searching && deals.length === 0 && (
          <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 16, padding: 32, textAlign: "center" }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>🚫</div>
            <p style={{ color: C.text, fontSize: 16, fontWeight: 600, margin: "0 0 8px 0" }}>
              No live products returned
            </p>
            <p style={{ color: C.textSecondary, fontSize: 14, lineHeight: 1.7, maxWidth: 620, margin: "0 auto" }}>
              {note ||
                "The scrapers ran but every store returned an empty result set. No placeholder products are shown — that would be fake data."}
            </p>
            <p style={{ color: C.textMuted, fontSize: 12, marginTop: 16 }}>
              To get real results this server needs either a shopping API key (e.g. RapidAPI / SerpApi)
              or a residential proxy — datacenter IPs are blocked by Amazon, Flipkart and Ajio.
            </p>
          </div>
        )}

        {deals.length > 0 && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 20 }}>
            {deals.map((p, i) => (
              <ProductCard key={p.url || p.id || i} product={p} />
            ))}
          </div>
        )}
      </section>

      {/* Features — descriptions of what the code actually does */}
      <section style={{ padding: "48px 0" }}>
        <h2 style={{ fontSize: 24, fontWeight: 800, color: C.text, textAlign: "center", marginBottom: 32 }}>What This App Actually Does</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 20 }}>
          {[
            { icon: "⚡", title: "Live Price Comparison", desc: "Real HTTP scrapers read Amazon / Flipkart / Ajio result pages", color: C.gold },
            { icon: "🔥", title: "Loot Deal Detection", desc: "Flags items whose discount percentage crosses the threshold", color: C.red },
            { icon: "🛡️", title: "Fake Discount Alert", desc: "Flags an inflated MRP so a 'discount' is really a fake sale", color: C.tertiary },
            { icon: "🤖", title: "AI Shopping Assistant", desc: "Backend proxies chat to the SAM-LLM model server on :5000", color: C.primary },
            { icon: "🚚", title: "Multi-Store Tracking", desc: "Tracks a product URL and records real price history", color: C.secondary },
            { icon: "🏷️", title: "Affiliate Cashback", desc: "Rewrites store URLs with a real affiliate tag", color: "#a855f7" },
          ].map((f, i) => (
            <div key={i} style={{ padding: 24, background: C.card, borderRadius: 16, border: `1px solid ${C.border}`, transition: "all 0.3s" }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = f.color; e.currentTarget.style.transform = "translateY(-4px)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.transform = "translateY(0)"; }}
            >
              <div style={{ width: 44, height: 44, borderRadius: 12, background: `${f.color}15`, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 16, fontSize: 22 }}>{f.icon}</div>
              <h3 style={{ fontSize: 18, fontWeight: 700, color: C.text, marginBottom: 8 }}>{f.title}</h3>
              <p style={{ fontSize: 14, color: C.textSecondary, lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function ProductCard({ product }) {
  // Field names differ per endpoint (/search/ uses name+price, /loot-deals/ uses
  // name+price+original_price). Read whichever is actually present. No defaults
  // are invented — a missing value renders as "—".
  const title = product.name || product.title;
  // A price of 0 (or null/NaN) means the scraper could not parse it — the
  // backend returns 0.0 on a failed parse. Rendering "₹0" would present a
  // failure as a real price, so treat it as unavailable.
  const rawPrice = Number(product.price);
  const price = Number.isFinite(rawPrice) && rawPrice > 0 ? rawPrice : null;
  const rawOriginal = Number(product.original_price ?? product.originalPrice);
  const original = Number.isFinite(rawOriginal) && rawOriginal > 0 ? rawOriginal : null;
  const discount = product.discount_percentage ?? (original && price ? Math.round(((original - price) / original) * 100) : null);
  const store = product.store;
  const rating = product.rating;
  const link = product.url || product.affiliate_url;

  // The search scrapers put the product's canonical URL in `id`, not a numeric
  // row id. Linking to `/product/<url>` produced a broken route, so detect that
  // and route through the PDP's ?url= handler instead.
  const rawId = product.id;
  const numericId = typeof rawId === "number" || /^\d+$/.test(String(rawId ?? ""));
  const detailLink =
    numericId && rawId != null
      ? `/product/${rawId}`
      : link
        ? `/product/live?url=${encodeURIComponent(link)}`
        : null;

  return (
    <div style={{ background: C.card, borderRadius: 16, border: `1px solid ${C.border}`, overflow: "hidden", transition: "all 0.3s" }}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = C.primary; e.currentTarget.style.transform = "translateY(-4px)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.transform = "translateY(0)"; }}
    >
      <div style={{ position: "relative", height: 180, background: "rgba(30, 41, 59, 0.5)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        {product.image ? (
          <img src={product.image} alt={title || "product"} style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }}
            onError={(e) => { e.currentTarget.style.display = "none"; }} />
        ) : (
          <span style={{ fontSize: 14, color: C.textMuted }}>no image</span>
        )}
        {discount != null && discount > 0 && (
          <div style={{ position: "absolute", top: 10, left: 10, padding: "4px 10px", borderRadius: 8, background: C.red, color: "#fff", fontSize: 12, fontWeight: 700 }}>
            -{discount}%
          </div>
        )}
      </div>
      <div style={{ padding: 16 }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: C.text, marginBottom: 6, lineHeight: 1.4 }}>{title || "Untitled (scraper returned no name)"}</h3>
        {rating != null && (
          <div style={{ display: "flex", alignItems: "center", gap: 4, marginBottom: 8 }}>
            <span style={{ color: C.gold }}>{"★".repeat(Math.max(1, Math.round(Number(rating))))}</span>
            <span style={{ fontSize: 12, color: C.textMuted }}>{rating}</span>
          </div>
        )}
        <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 8 }}>
          {price != null ? (
            <span style={{ fontSize: 22, fontWeight: 800, color: C.tertiary }}>₹{Number(price).toLocaleString("en-IN")}</span>
          ) : (
            <span style={{ fontSize: 18, fontWeight: 700, color: C.textMuted }}>price unavailable</span>
          )}
          {original != null && (
            <span style={{ fontSize: 14, color: C.textMuted, textDecoration: "line-through" }}>₹{Number(original).toLocaleString("en-IN")}</span>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 12 }}>
          <span style={{ fontSize: 12, color: C.textSecondary, padding: "2px 8px", background: `${C.primary}15`, borderRadius: 6 }}>{store || "store unknown"}</span>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {link ? (
            <a href={link} target="_blank" rel="noopener noreferrer" style={{ flex: 1, padding: "10px 0", background: "linear-gradient(135deg, var(--primary), var(--primary-dark))", borderRadius: 10, color: "#fff", fontWeight: 600, fontSize: 13, textAlign: "center", textDecoration: "none" }}>
              View Deal
            </a>
          ) : (
            <span style={{ flex: 1, padding: "10px 0", background: "rgba(100,116,139,0.25)", borderRadius: 10, color: C.textMuted, fontWeight: 600, fontSize: 13, textAlign: "center" }}>
              no store link
            </span>
          )}
          {detailLink ? (
            <Link to={detailLink} style={{ padding: "10px 14px", background: "transparent", border: `1px solid ${C.border}`, borderRadius: 10, color: C.primary, fontSize: 13, fontWeight: 600, textDecoration: "none" }}>
              Details
            </Link>
          ) : (
            <Link to="/compare" style={{ padding: "10px 14px", background: "transparent", border: `1px solid ${C.border}`, borderRadius: 10, color: C.primary, fontSize: 13, fontWeight: 600, textDecoration: "none" }}>
              Compare
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}