// AdminDashboardScreen.jsx — REAL DATA ONLY. No static stats/deals/charts.
// Fetches live: /admin/stats, /admin/products, /admin/users, /admin/revenue.
// Honest empty states; never invents numbers.
import React from "react";
import axios from "axios";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "/api/v1";

const COLORS = {
  bg: "#0f131c", card: "rgba(15,23,42,0.65)", border: "rgba(255,255,255,0.08)",
  primary: "#6366f1", secondary: "#22d3ee", tertiary: "#10b981", gold: "#f59e0b",
  red: "#ef4444", text: "#f8fafc", textSecondary: "#cbd5e1", muted: "#64748b",
};

const priceFont = "'JetBrains Mono', monospace";
const navItems = ["Dashboard", "Products", "Users", "Deals"];

function StatCard({ label, value, color }) {
  return (
    <div style={{ flex: 1, background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 16, padding: 20, minWidth: 160 }}>
      <div style={{ color: COLORS.muted, fontSize: 13, marginBottom: 8 }}>{label}</div>
      <div style={{ color, fontSize: 28, fontWeight: 700, fontFamily: priceFont }}>{value}</div>
    </div>
  );
}

function SectionCard({ title, children }) {
  return (
    <div style={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 16, padding: 20 }}>
      <h2 style={{ color: COLORS.text, fontSize: 16, fontWeight: 600, margin: "0 0 16px 0" }}>{title}</h2>
      {children}
    </div>
  );
}

const thStyle = { textAlign: "left", padding: "10px 12px", color: COLORS.muted, fontWeight: 600, borderBottom: `1px solid ${COLORS.border}` };
const tdStyle = { padding: "12px 12px", color: COLORS.text, borderBottom: `1px solid ${COLORS.border}` };

export default function AdminDashboardScreen() {
  const [active, setActive] = React.useState("Dashboard");
  const [stats, setStats] = React.useState(null);
  const [products, setProducts] = React.useState([]);
  const [users, setUsers] = React.useState([]);
  const [revenue, setRevenue] = React.useState([]);
  const [revenueNote, setRevenueNote] = React.useState("");
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState("");

  React.useEffect(() => {
    (async () => {
      setLoading(true); setError("");
      try {
        const [s, p, u, r] = await Promise.all([
          axios.get(`${API_BASE}/admin/stats`),
          axios.get(`${API_BASE}/admin/products`),
          axios.get(`${API_BASE}/admin/users`, { params: { limit: 20 } }),
          axios.get(`${API_BASE}/admin/revenue`, { params: { days: 14 } }),
        ]);
        setStats(s.data);
        setProducts(p.data.products || []);
        setUsers(u.data.users || []);
        setRevenue(r.data.data || []);
        setRevenueNote(r.data.note || "");
      } catch (e) {
        setError("Backend admin API unreachable. Is the API server running on :8000?");
      }
      setLoading(false);
    })();
  }, []);

  const storeBars = stats ? Object.entries(stats.deals_by_store || {}).map(([store, items]) => ({ store, items })) : [];
  const cards = stats ? [
    { label: "Total Users (DB)", value: stats.total_users, color: COLORS.primary },
    { label: "Tracked Products (DB)", value: stats.total_tracks, color: COLORS.secondary },
    { label: "Active Subscriptions", value: stats.active_subscriptions, color: COLORS.tertiary },
    { label: "Revenue (Rs, real)", value: Number(stats.total_revenue || 0).toLocaleString("en-IN"), color: COLORS.gold },
  ] : [];

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: COLORS.bg, fontFamily: "'Inter', system-ui, sans-serif", color: COLORS.text }}>
      <aside style={{ width: 220, flexShrink: 0, borderRight: `1px solid ${COLORS.border}`, padding: 20, display: "flex", flexDirection: "column", gap: 24 }}>
        <div style={{ fontSize: 22, fontWeight: 800 }}>VGAS.AI</div>
        <nav style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {navItems.map((item) => (
            <div key={item} onClick={() => setActive(item)} style={{ padding: "10px 14px", borderRadius: 10, cursor: "pointer", fontSize: 14, color: item === active ? COLORS.text : COLORS.textSecondary, background: item === active ? "rgba(99,102,241,0.18)" : "transparent" }}>
              {item}
            </div>
          ))}
        </nav>
      </aside>

      <main style={{ flex: 1, padding: 24, display: "flex", flexDirection: "column", gap: 24, overflowY: "auto" }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0 }}>Admin Dashboard</h1>
        <p style={{ color: COLORS.muted, margin: 0, fontSize: 13 }}>All numbers below are live from the backend database — nothing is pre-filled.</p>
        {loading && <p>⏳ Loading live admin data…</p>}
        {error && <p style={{ color: COLORS.red }}>{error}</p>}

        {!loading && !error && (active === "Dashboard" || active === "Deals") && (
          <>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
              {cards.map((c) => <StatCard key={c.label} {...c} />)}
            </div>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: 320 }}>
                <SectionCard title="Revenue — last 14 days (live)">
                  {revenue.every((d) => d.total === 0) ? (
                    <p style={{ color: COLORS.muted }}>No revenue recorded yet. {revenueNote}</p>
                  ) : (
                    <ResponsiveContainer width="100%" height={260}>
                      <LineChart data={revenue}>
                        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                        <XAxis dataKey="date" stroke={COLORS.muted} tickFormatter={(d) => d.slice(5)} />
                        <YAxis stroke={COLORS.muted} />
                        <Tooltip contentStyle={{ background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: 8, color: COLORS.text }} />
                        <Line type="monotone" dataKey="total" stroke={COLORS.primary} strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  )}
                </SectionCard>
              </div>
              <div style={{ flex: 1, minWidth: 320 }}>
                <SectionCard title="Tracked products by store (live)">
                  {storeBars.length === 0 ? (
                    <p style={{ color: COLORS.muted }}>No tracked products yet — counts appear here once users track items.</p>
                  ) : (
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={storeBars}>
                        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                        <XAxis dataKey="store" stroke={COLORS.muted} />
                        <YAxis stroke={COLORS.muted} allowDecimals={false} />
                        <Tooltip contentStyle={{ background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: 8, color: COLORS.text }} />
                        <Bar dataKey="items" fill={COLORS.secondary} radius={[6, 6, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </SectionCard>
              </div>
            </div>
          </>
        )}

        {!loading && !error && (active === "Dashboard" || active === "Deals" || active === "Products") && (
          <SectionCard title="Recent Deals — tracked products (live)">
            {products.length === 0 ? (
              <p style={{ color: COLORS.muted }}>No products tracked yet. Tracked items will appear here with live prices.</p>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
                  <thead><tr>{["Product", "Store", "Price", "Target", "Status"].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr></thead>
                  <tbody>
                    {products.slice(0, 20).map((d) => (
                      <tr key={d.id}>
                        <td style={tdStyle}>{d.title || d.url}</td>
                        <td style={{ ...tdStyle, color: COLORS.textSecondary }}>{d.store || "—"}</td>
                        <td style={{ ...tdStyle, color: COLORS.tertiary, fontWeight: 700, fontFamily: priceFont }}>
                          {d.current_price != null ? `Rs ${Number(d.current_price).toLocaleString("en-IN")}` : "—"}
                        </td>
                        <td style={{ ...tdStyle, color: COLORS.gold }}>
                          {d.target_price != null ? `Rs ${Number(d.target_price).toLocaleString("en-IN")}` : "—"}
                        </td>
                        <td style={tdStyle}>{d.status || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </SectionCard>
        )}

        {!loading && !error && (active === "Users") && (
          <SectionCard title="Users (live)">
            {users.length === 0 ? (
              <p style={{ color: COLORS.muted }}>No users registered yet.</p>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
                  <thead><tr>{["Username", "Email", "Plan", "Joined"].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr></thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id}>
                        <td style={tdStyle}>{u.username}</td>
                        <td style={{ ...tdStyle, color: COLORS.textSecondary }}>{u.email}</td>
                        <td style={{ ...tdStyle, color: COLORS.gold }}>{u.plan || "free"}</td>
                        <td style={{ ...tdStyle, color: COLORS.textSecondary }}>{u.created_at ? u.created_at.slice(0, 10) : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </SectionCard>
        )}
      </main>
    </div>
  );
}
