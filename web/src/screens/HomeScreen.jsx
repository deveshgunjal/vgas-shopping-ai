import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { searchAPI } from "../api/services";

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

const categories = [
  { name: "Electronics", icon: "📱", color: C.primary },
  { name: "Fashion", icon: "👕", color: "#ec4899" },
  { name: "Home", icon: "🏠", color: C.tertiary },
  { name: "Beauty", icon: "💄", color: "#a855f7" },
  { name: "Sports", icon: "⚽", color: "#f97316" },
  { name: "Books", icon: "📚", color: C.secondary },
  { name: "Grocery", icon: "🛒", color: C.gold },
  { name: "Toys", icon: "🎮", color: C.red },
];

const trending = [
  { id: 1, title: "iPhone 15 Pro Max 256GB", price: 134990, originalPrice: 159900, store: "Amazon", rating: 4.5, discount: 16, image: "📱" },
  { id: 2, title: "Samsung Galaxy S24 Ultra", price: 129999, originalPrice: 144999, store: "Flipkart", rating: 4.7, discount: 10, image: "📱" },
  { id: 3, title: "Nike Air Jordan 1 Retro", price: 8999, originalPrice: 14995, store: "Myntra", rating: 4.3, discount: 40, image: "👟" },
  { id: 4, title: "MacBook Air M3 15-inch", price: 134900, originalPrice: 154900, store: "Amazon", rating: 4.8, discount: 13, image: "💻" },
  { id: 5, title: "Sony WH-1000XM5", price: 26990, originalPrice: 34990, store: "Amazon", rating: 4.6, discount: 23, image: "🎧" },
  { id: 6, title: "Dyson V15 Detect", price: 52900, originalPrice: 62900, store: "Flipkart", rating: 4.4, discount: 16, image: "🏠" },
];

export default function HomeScreen() {
  const [search, setSearch] = useState("");
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDeals();
  }, []);

  const fetchDeals = async () => {
    try {
      const res = await searchAPI.lootDeals();
      setDeals(res.data.deals || res.data.products || []);
    } catch {
      setDeals(trending);
    }
  };

  const handleSearch = async (e) => {
    if (e.key === "Enter" && search.trim()) {
      setLoading(true);
      try {
        const res = await searchAPI.search(search);
        setDeals(res.data.products || res.data.results || []);
      } catch {
        setDeals(trending);
      }
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1400, margin: "0 auto", padding: "0 24px" }}>
      {/* Hero */}
      <section style={{ padding: "40px 0 32px", textAlign: "center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 16px", borderRadius: 20, background: `${C.gold}15`, border: `1px solid ${C.gold}30`, color: C.gold, fontSize: 13, fontWeight: 600, marginBottom: 24 }}>
          🔥 AI-Powered Price Intelligence
        </div>
        <h1 style={{ fontSize: "clamp(28px, 5vw, 56px)", fontWeight: 800, lineHeight: 1.1, marginBottom: 16, color: C.text }}>
          Find <span className="shimmer-text">Lowest Prices</span> Across<br />10 Crore+ Products
        </h1>
        <p style={{ fontSize: 16, color: C.textSecondary, maxWidth: 600, margin: "0 auto 32px", lineHeight: 1.6 }}>
          AI compares prices from Amazon, Flipkart, Meesho, Myntra & 50+ stores. Save up to 80% with real-time loot deals.
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
              🔍 Search
            </button>
          </div>
        </div>

        {/* Stats */}
        <div style={{ display: "flex", justifyContent: "center", gap: 48, marginTop: 40, flexWrap: "wrap" }}>
          {[
            { num: "10Cr+", label: "Products", color: C.primary },
            { num: "50+", label: "Stores", color: C.secondary },
            { num: "80%", label: "Max Savings", color: C.tertiary },
            { num: "500K+", label: "Users", color: C.gold },
          ].map((s, i) => (
            <div key={i} style={{ textAlign: "center" }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: s.color }}>{s.num}</div>
              <div style={{ fontSize: 13, color: C.textSecondary, marginTop: 4 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Categories */}
      <section style={{ padding: "16px 0 32px" }}>
        <div style={{ display: "flex", gap: 12, overflowX: "auto", paddingBottom: 8 }} className="no-scrollbar">
          {categories.map((c, i) => (
            <div key={i} style={{ minWidth: 100, padding: "12px 16px", background: C.card, borderRadius: 12, border: `1px solid ${C.border}`, textAlign: "center", cursor: "pointer", transition: "all 0.2s", flexShrink: 0 }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = c.color; e.currentTarget.style.transform = "translateY(-2px)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.transform = "translateY(0)"; }}
            >
              <div style={{ fontSize: 28, marginBottom: 4 }}>{c.icon}</div>
              <div style={{ fontSize: 12, fontWeight: 600, color: C.text }}>{c.name}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Deals */}
      <section style={{ padding: "32px 0" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
          <h2 style={{ fontSize: 24, fontWeight: 800, color: C.text }}>
            🔥 Loot Deals <span style={{ fontSize: 12, padding: "4px 10px", background: `${C.red}20`, color: C.red, borderRadius: 8, fontWeight: 600 }}>LIVE</span>
          </h2>
          <Link to="/compare" style={{ fontSize: 13, color: C.primary, textDecoration: "none", fontWeight: 600 }}>Compare All →</Link>
        </div>

        {loading && (
          <div style={{ textAlign: "center", padding: 40 }}>
            <div style={{ display: "inline-block", width: 40, height: 40, border: `3px solid ${C.border}`, borderTopColor: C.primary, borderRadius: "50%", animation: "spin 1s linear infinite" }} />
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          </div>
        )}

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 20 }}>
          {(deals.length > 0 ? deals : trending).map((p, i) => (
            <ProductCard key={p.id || i} product={p} />
          ))}
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: "48px 0" }}>
        <h2 style={{ fontSize: 24, fontWeight: 800, color: C.text, textAlign: "center", marginBottom: 32 }}>Why 500K+ Users Love VGAS AI</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 20 }}>
          {[
            { icon: "⚡", title: "AI Price Comparison", desc: "Compare prices across 50+ stores in real-time", color: C.gold },
            { icon: "🔥", title: "Loot Deal Detection", desc: "AI finds hidden deals with 80%+ discounts", color: C.red },
            { icon: "🛡️", title: "Fake Discount Alert", desc: "Detect inflated MRP and fake sales instantly", color: C.tertiary },
            { icon: "🤖", title: "AI Shopping Assistant", desc: "Chat with AI to find best products for your needs", color: C.primary },
            { icon: "🚚", title: "Multi-Store Tracking", desc: "Track prices across Amazon, Flipkart, Meesho", color: C.secondary },
            { icon: "🏷️", title: "Affiliate Cashback", desc: "Earn cashback on every purchase through VGAS", color: "#a855f7" },
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
  const discount = product.originalPrice || product.original_price
    ? Math.round(((product.originalPrice || product.original_price - product.price) / (product.originalPrice || product.original_price)) * 100)
    : 0;

  return (
    <div style={{ background: C.card, borderRadius: 16, border: `1px solid ${C.border}`, overflow: "hidden", transition: "all 0.3s" }}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = C.primary; e.currentTarget.style.transform = "translateY(-4px)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.transform = "translateY(0)"; }}
    >
      <div style={{ position: "relative", height: 180, background: "rgba(30, 41, 59, 0.5)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 64 }}>
        {product.image || "📦"}
        {discount > 0 && (
          <div style={{ position: "absolute", top: 10, left: 10, padding: "4px 10px", borderRadius: 8, background: C.red, color: "#fff", fontSize: 12, fontWeight: 700 }}>
            -{discount}%
          </div>
        )}
      </div>
      <div style={{ padding: 16 }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: C.text, marginBottom: 6, lineHeight: 1.4 }}>{product.title || "Product"}</h3>
        <div style={{ display: "flex", alignItems: "center", gap: 4, marginBottom: 8 }}>
          <span style={{ color: C.gold }}>★★★★★</span>
          <span style={{ fontSize: 12, color: C.textMuted }}>({product.rating || "4.2"})</span>
        </div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 8 }}>
          <span style={{ fontSize: 22, fontWeight: 800, color: C.tertiary }}>₹{(product.price || 0).toLocaleString()}</span>
          {(product.originalPrice || product.original_price) && (
            <span style={{ fontSize: 14, color: C.textMuted, textDecoration: "line-through" }}>₹{(product.originalPrice || product.original_price).toLocaleString()}</span>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 12 }}>
          <span style={{ fontSize: 12, color: C.textSecondary, padding: "2px 8px", background: `${C.primary}15`, borderRadius: 6 }}>{product.store || "Amazon"}</span>
          <span style={{ fontSize: 12, color: C.tertiary }}>🚚 Free Delivery</span>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <Link to={`/product/${product.id || 1}`} style={{ flex: 1, padding: "10px 0", background: "linear-gradient(135deg, var(--primary), var(--primary-dark))", borderRadius: 10, color: "#fff", fontWeight: 600, fontSize: 13, textAlign: "center", textDecoration: "none" }}>
            View Deal
          </Link>
          <Link to="/compare" style={{ padding: "10px 14px", background: "transparent", border: `1px solid ${C.border}`, borderRadius: 10, color: C.primary, fontSize: 13, fontWeight: 600, textDecoration: "none" }}>
            Compare
          </Link>
        </div>
      </div>
    </div>
  );
}
