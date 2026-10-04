// ProfileScreen.jsx — REAL DATA ONLY. No mock user, no invented earnings.
// Shows live user from GET /api/v1/auth/me (token in localStorage).
// REAL logout: POST /api/v1/auth/logout + clears token.
import React from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "/api/v1";

export default function ProfileScreen() {
  const navigate = useNavigate();
  const [user, setUser] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    (async () => {
      const token = localStorage.getItem("vgas_token");
      if (!token) { setLoading(false); return; }
      try {
        const res = await axios.get(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(res.data.user);
      } catch {
        localStorage.removeItem("vgas_token");
      }
      setLoading(false);
    })();
  }, []);

  const logout = async () => {
    const token = localStorage.getItem("vgas_token");
    try {
      if (token) {
        await axios.post(`${API_BASE}/auth/logout`, {}, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    } catch { /* token cleared below regardless */ }
    localStorage.removeItem("vgas_token");
    navigate("/");
  };

  const containerStyle = { minHeight: "100vh", background: "#0f131c", color: "#f8fafc", fontFamily: "system-ui, sans-serif", padding: "24px", display: "flex", flexDirection: "column", gap: "24px", alignItems: "center" };
  const glassStyle = { background: "rgba(15,23,42,0.65)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 16, padding: "16px 24px", width: "100%", maxWidth: "800px", boxSizing: "border-box" };

  const name = user?.username || user?.name || "";
  const email = user?.email || "";
  const initial = (name || email || "?").charAt(0).toUpperCase();
  const isPremium = !!(user?.is_premium || (user?.plan && user.plan !== "free"));

  return (
    <div style={containerStyle}>
      <div style={{ ...glassStyle, background: isPremium ? "linear-gradient(90deg, #f59e0b, #fcd34d)" : "rgba(15,23,42,0.65)", color: isPremium ? "#0f131c" : "#f8fafc", fontWeight: "600", textAlign: "center", fontSize: "1.1rem" }}>
        {isPremium ? "VGAS VIP - Ad-free + exclusive deals" : "VGAS Free plan"}
      </div>

      <div style={glassStyle}>
        {loading ? (
          <p>⏳ Loading account…</p>
        ) : !user ? (
          <div style={{ textAlign: "center" }}>
            <p style={{ color: "#cbd5e1" }}>Not logged in. Log in to see your real account.</p>
            <button onClick={() => navigate("/")} style={{ background: "#6366f1", color: "#fff", border: "none", borderRadius: 8, padding: "8px 16px", cursor: "pointer" }}>
              Back to Home
            </button>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ width: 80, height: 80, borderRadius: "50%", background: "#22d3ee", color: "#0f131c", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "2rem", fontWeight: "600", marginBottom: "12px" }}>
              {initial}
            </div>
            <div style={{ fontSize: "1.25rem", fontWeight: "600" }}>{name || "VGAS User"}</div>
            <div style={{ color: "#cbd5e1", marginTop: "4px" }}>{email}</div>
            <div style={{ color: "#cbd5e1", marginBottom: "12px" }}>Plan: {user?.plan || "free"}</div>
            <button onClick={logout} style={{ background: "rgba(239,68,68,0.2)", color: "#ef4444", border: "1px solid rgba(239,68,68,0.4)", borderRadius: 8, padding: "8px 16px", cursor: "pointer" }}>
              Logout
            </button>
          </div>
        )}
      </div>

      <div style={{ ...glassStyle, color: "#64748b", fontSize: 13, textAlign: "center" }}>
        Earnings, alerts, wishlist and order history will appear here once their backend endpoints are enabled. No sample numbers are shown.
      </div>
    </div>
  );
}
