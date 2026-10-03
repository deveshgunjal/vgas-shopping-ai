jsx
// ProductComparison.jsx
import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const products = [
  {
    id: "iphone15",
    name: "iPhone 15",
    image: "https://via.placeholder.com/150?text=iPhone+15",
    priceHistory: [
      { date: "2024-01-01", price: 119900 },
      { date: "2024-02-01", price: 117900 },
      { date: "2024-03-01", price: 115900 },
      { date: "2024-04-01", price: 115900 },
    ],
    stores: [
      { name: "Amazon", price: 115900 },
      { name: "Flipkart", price: 117900 },
      { name: "Reliance", price: 119900 },
    ],
  },
  {
    id: "samsungs24",
    name: "Samsung S24",
    image: "https://via.placeholder.com/150?text=Samsung+S24",
    priceHistory: [
      { date: "2024-01-01", price: 84999 },
      { date: "2024-02-01", price: 83999 },
      { date: "2024-03-01", price: 82999 },
      { date: "2024-04-01", price: 81999 },
    ],
    stores: [
      { name: "Amazon", price: 81999 },
      { name: "Flipkart", price: 83999 },
      { name: "Reliance", price: 84999 },
    ],
  },
  {
    id: "oneplus12",
    name: "OnePlus 12",
    image: "https://via.placeholder.com/150?text=OnePlus+12",
    priceHistory: [
      { date: "2024-01-01", price: 64999 },
      { date: "2024-02-01", price: 63999 },
      { date: "2024-03-01", price: 62999 },
      { date: "2024-04-01", price: 62999 },
    ],
    stores: [
      { name: "Amazon", price: 62999 },
      { name: "Flipkart", price: 63999 },
      { name: "Reliance", price: 64999 },
    ],
  },
];

const getBestDeal = () => {
  let best = null;
  products.forEach((p) => {
    p.stores.forEach((s) => {
      if (!best || s.price < best.price) {
        best = { product: p.name, store: s.name, price: s.price };
      }
    });
  });
  // find second best price for savings calculation
  const sorted = products
    .flatMap((p) => p.stores.map((s) => ({ ...s, product: p.name })))
    .sort((a, b) => a.price - b.price);
  const secondBest = sorted[1];
  const savings = secondBest ? secondBest.price - best.price : 0;
  return { ...best, savings };
};

const bestDeal = getBestDeal();

export default function ProductComparison() {
  const navigate = useNavigate();

  return (
    <div className="pc-container">
      <style>{`
        :root {
          --bg: #0f131c;
          --primary: #6366f1;
          --secondary: #22d3ee;
          --tertiary: #10b981;
          --glass: rgba(255,255,255,0.08);
          --glass-border: rgba(255,255,255,0.12);
        }
        body {
          font-family: 'Inter', sans-serif;
          background: var(--bg);
          color: #e5e7eb;
          margin: 0;
          padding: 0;
        }
        .pc-container {
          padding: 2rem;
        }
        .pc-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 1.5rem;
        }
        .pc-card {
          background: var(--glass);
          backdrop-filter: blur(12px);
          border: 1px solid var(--glass-border);
          border-radius: 1rem;
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        .pc-header {
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--primary);
          text-align: center;
        }
        .pc-price {
          font-family: 'JetBrains Mono', monospace;
          font-size: 1.5rem;
          color: var(--secondary);
          text-align: center;
        }
        .pc-table {
          width: 100%;
          border-collapse: collapse;
        }
        .pc-table th,
        .pc-table td {
          padding: 0.5rem;
          text-align: center;
        }
        .pc-table th {
          background: var(--glass);
          color: var(--primary);
        }
        .pc-table td {
          background: var(--glass);
        }
        .best-price {
          border: 2px solid var(--tertiary);
          border-radius: 0.5rem;
        }
        .recommend-banner {
          background: var(--tertiary);
          color: #fff;
          padding: 0.75rem 1rem;
          border-radius: 0.75rem;
          text-align: center;
          font-weight: 600;
          margin-bottom: 1.5rem;
        }
        @media (max-width: 640px) {
          .pc-header { font-size: 1rem; }
          .pc-price { font-size: 1.25rem; }
        }
      `}</style>

      <div className="recommend-banner">
        Best deal: {bestDeal.store} at ₹{bestDeal.price.toLocaleString()} (save ₹{bestDeal.savings.toLocaleString()})
      </div>

      <div className="pc-grid">
        {products.map((product) => {
          const bestStorePrice = Math.min(...product.stores.map((s) => s.price));
          return (
            <div key={product.id} className="pc-card">
              <div className="pc-header">{product.name}</div>
              <img src={product.image} alt={product.name} style={{ width: "100%", borderRadius: "0.5rem" }} />
              <div className="pc-price">₹{bestStorePrice.toLocaleString()}</div>

              {/* Price History Chart */}
              <ResponsiveContainer width="100%" height={150}>
                <LineChart data={product.priceHistory}>
                  <XAxis dataKey="date" tick={{ fill: "#e5e7eb", fontSize: 10 }} />
                  <YAxis tickFormatter={(v) => `₹${v / 1000}k`} tick={{ fill: "#e5e7eb", fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "var(--glass)", border: "none", color: "#e5e7eb" }}
                    labelStyle={{ color: "#e5e7eb" }}
                  />
                  <Legend wrapperStyle={{ color: "#e5e7eb", fontSize: 10 }} />
                  <Line type="monotone" dataKey="price" stroke="var(--primary)" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>

              {/* Store-wise price table */}
              <table className="pc-table">
                <thead>
                  <tr>
                    <th>Store</th>
                    <th>Price (₹)</th>
                  </tr>
                </thead>
                <tbody>
                  {product.stores.map((store) => (
                    <tr
                      key={store.name}
                      className={store.price === bestStorePrice ? "best-price" : ""}
                    >
                      <td>{store.name}</td>
                      <td className="pc-price">{store.price.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <button
                onClick={() => navigate(`/product/${product.id}`)}
                style={{
                  marginTop: "0.5rem",
                  padding: "0.5rem 1rem",
                  background: "var(--primary)",
                  color: "#fff",
                  border: "none",
                  borderRadius: "0.5rem",
                  cursor: "pointer",
                }}
              >
                View Details
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}