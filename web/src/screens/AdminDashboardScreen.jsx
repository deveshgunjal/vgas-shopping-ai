jsx
// src/components/AdminDashboard.jsx
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
  CartesianGrid,
} from "recharts";
import axios from "axios";
import { NavLink } from "react-router-dom";


const sidebarItems = [
  { name: "Dashboard", path: "/dashboard" },
  { name: "Products", path: "/products" },
  { name: "Scrapers", path: "/scrapers" },
  { name: "Users", path: "/users" },
  { name: "Deals", path: "/deals" },
  { name: "Analytics", path: "/analytics" },
  { name: "Settings", path: "/settings" },
];

const stats = [
  { label: "Total Products", value: "10Cr+", color: "var(--primary)" },
  { label: "Active Scrapers", value: "50+", color: "var(--secondary)" },
  { label: "Users", value: "500K+", color: "var(--tertiary)" },
  { label: "Revenue", value: "₹2.4Cr", color: "var(--gold)" },
];

const priceTrendData = [
  { day: "Mon", price: 120 },
  { day: "Tue", price: 115 },
  { day: "Wed", price: 130 },
  { day: "Thu", price: 125 },
  { day: "Fri", price: 140 },
  { day: "Sat", price: 135 },
  { day: "Sun", price: 150 },
];

const scraperPerfData = [
  { name: "Amazon", runs: 120 },
  { name: "Flipkart", runs: 95 },
  { name: "Snapdeal", runs: 70 },
  { name: "Myntra", runs: 55 },
];

const userGrowthData = [
  { month: "Jan", users: 80 },
  { month: "Feb", users: 120 },
  { month: "Mar", users: 200 },
  { month: "Apr", users: 340 },
  { month: "May", users: 500 },
  { month: "Jun", users: 720 },
];

const recentDeals = [
  {
    product: "Apple iPhone 15",
    store: "Amazon",
    price: "₹79,999",
    discount: "15%",
    status: "LIVE",
  },
  {
    product: "Samsung Galaxy S24",
    store: "Flipkart",
    price: "₹69,999",
    discount: "10%",
    status: "EXPIRED",
  },
  {
    product: "OnePlus 12",
    store: "OnePlus Store",
    price: "₹54,999",
    discount: "12%",
    status: "LIVE",
  },
  {
    product: "Sony WH-1000XM5",
    store: "Sony",
    price: "₹24,999",
    discount: "20%",
    status: "LIVE",
  },
];

const AdminDashboard = () => {
  return (
    <div className="admin-dashboard">
      <aside className="sidebar">
        <h2 className="logo">VGAS.AI</h2>
        <nav>
          {sidebarItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className="nav-link"
              activeClassName="active"
            >
              {item.name}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="main-content">
        {/* Stats Cards */}
        <section className="stats-grid">
          {stats.map((s) => (
            <div key={s.label} className="stat-card" style={{ borderColor: s.color }}>
              <p className="stat-label">{s.label}</p>
              <p className="stat-value">{s.value}</p>
            </div>
          ))}
        </section>

        {/* Charts */}
        <section className="charts-grid">
          <div className="chart-card">
            <h3>Price Trends</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={priceTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="day" stroke="rgba(255,255,255,0.7)" />
                <YAxis stroke="rgba(255,255,255,0.7)" />
                <Tooltip />
                <Line type="monotone" dataKey="price" stroke="var(--primary)" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Scraper Performance</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={scraperPerfData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" />
                <YAxis stroke="rgba(255,255,255,0.7)" />
                <Tooltip />
                <Bar dataKey="runs" fill="var(--secondary)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>User Growth</h3>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={userGrowthData}>
                <defs>
                  <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--tertiary)" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="var(--tertiary)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="month" stroke="rgba(255,255,255,0.7)" />
                <YAxis stroke="rgba(255,255,255,0.7)" />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="users"
                  stroke="var(--tertiary)"
                  fillOpacity={1}
                  fill="url(#colorUsers)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Recent Deals Table */}
        <section className="deals-section">
          <h3>Recent Deals</h3>
          <table className="deals-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Store</th>
                <th>Price</th>
                <th>Discount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recentDeals.map((deal, idx) => (
                <tr key={idx}>
                  <td>{deal.product}</td>
                  <td>{deal.store}</td>
                  <td>{deal.price}</td>
                  <td>{deal.discount}</td>
                  <td>
                    <span
                      className={`status-badge ${
                        deal.status === "LIVE" ? "live" : "expired"
                      }`}
                    >
                      {deal.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
};

export default AdminDashboard;