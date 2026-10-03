import React from "react";

export default function Footer() {
  return (
    <footer style={{ padding: "48px 0 24px", borderTop: "1px solid var(--border)", background: "rgba(15, 19, 28, 0.5)" }}>
      <div style={{ maxWidth: 1400, margin: "0 auto", padding: "0 24px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 32, marginBottom: 32 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: "linear-gradient(135deg, var(--primary), var(--primary-dark))", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 16, color: "#fff" }}>V</div>
              <span style={{ fontSize: 18, fontWeight: 800, color: "var(--text)" }}>VGAS<span style={{ color: "var(--primary-light)" }}>.AI</span></span>
            </div>
            <p style={{ fontSize: 13, color: "var(--text-muted)", lineHeight: 1.6 }}>AI-powered shopping intelligence. Compare prices, find deals, save money.</p>
          </div>
          {[
            { title: "Product", links: ["Price Comparison", "Loot Deals", "AI Assistant", "Affiliate Program"] },
            { title: "Company", links: ["About Us", "Contact", "Privacy Policy", "Terms of Service"] },
            { title: "Support", links: ["Help Center", "Report Bug", "Feature Request", "Status Page"] },
          ].map((col, i) => (
            <div key={i}>
              <h4 style={{ fontSize: 14, fontWeight: 700, color: "var(--text)", marginBottom: 16 }}>{col.title}</h4>
              {col.links.map((l, j) => (
                <a key={j} href="#" style={{ display: "block", fontSize: 13, color: "var(--text-muted)", textDecoration: "none", marginBottom: 8 }}
                  onMouseEnter={(e) => e.target.style.color = "var(--primary-light)"}
                  onMouseLeave={(e) => e.target.style.color = "var(--text-muted)"}
                >{l}</a>
              ))}
            </div>
          ))}
        </div>
        <div style={{ borderTop: "1px solid var(--border)", paddingTop: 20, textAlign: "center", fontSize: 12, color: "var(--text-muted)" }}>
          2026 VGAS Shopping AI. Built with ❤️ by Vikas Gunjal.
        </div>
      </div>
    </footer>
  );
}
