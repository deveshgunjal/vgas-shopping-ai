import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar({ user }) {
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    if (e.key === "Enter" && search.trim()) {
      navigate(`/?q=${encodeURIComponent(search)}`);
    }
  };

  return (
    <nav style={{
      position: "sticky", top: 0, zIndex: 100,
      background: "rgba(15, 19, 28, 0.85)", backdropFilter: "blur(20px)",
      borderBottom: "1px solid var(--border)", padding: "0 24px",
    }}>
      <div style={{ maxWidth: 1400, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", height: 64, gap: 16 }}>
        <Link to="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg, var(--primary), var(--primary-dark))", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 18, color: "#fff" }}>V</div>
          <span style={{ fontSize: 20, fontWeight: 800, color: "var(--text)" }}>
            VGAS<span style={{ color: "var(--primary-light)" }}>.AI</span>
          </span>
        </Link>

        <div style={{ flex: 1, maxWidth: 500, position: "relative" }}>
          <input
            type="text"
            placeholder="Search products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={handleSearch}
            style={{
              width: "100%", padding: "10px 16px 10px 40px",
              background: "rgba(30, 41, 59, 0.6)", border: "1px solid var(--border)",
              borderRadius: 12, color: "var(--text)", fontSize: 14, outline: "none",
            }}
          />
          <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>🔍</span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <NavLink to="/" label="Home" />
          <NavLink to="/compare" label="Compare" />
          <NavLink to="/admin" label="Admin" />
          <NavLink to="/profile" label="Profile" />
          {user ? (
            <span style={{ padding: "8px 16px", background: "rgba(99, 102, 241, 0.15)", borderRadius: 10, color: "var(--primary-light)", fontSize: 13, fontWeight: 600 }}>
              {user.name?.split(" ")[0] || "User"}
            </span>
          ) : (
            <button className="btn-primary" style={{ padding: "8px 16px", fontSize: 13 }}>Login</button>
          )}
        </div>
      </div>
    </nav>
  );
}

function NavLink({ to, label }) {
  return (
    <Link to={to} style={{ padding: "8px 12px", borderRadius: 8, color: "var(--text-secondary)", textDecoration: "none", fontSize: 13, fontWeight: 500, transition: "all 0.2s" }}
      onMouseEnter={(e) => { e.target.style.color = "var(--text)"; e.target.style.background = "rgba(99, 102, 241, 0.1)"; }}
      onMouseLeave={(e) => { e.target.style.color = "var(--text-secondary)"; e.target.style.background = "transparent"; }}
    >
      {label}
    </Link>
  );
}
