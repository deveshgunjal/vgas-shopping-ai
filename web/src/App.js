import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { authAPI } from "./api/services";
import HomeScreen from "./screens/HomeScreen";
import CompareScreen from "./screens/CompareScreen";
import ProductDetailScreen from "./screens/ProductDetailScreen";
import AdminDashboardScreen from "./screens/AdminDashboardScreen";
import ProfileScreen from "./screens/ProfileScreen";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import "./index.css";

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem("vgas_user");
    if (saved) {
      try { setUser(JSON.parse(saved)); } catch { /* ignore */ }
    }
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", background: "var(--bg)" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ width: 48, height: 48, border: "3px solid var(--border)", borderTopColor: "var(--primary)", borderRadius: "50%", animation: "spin 1s linear infinite", margin: "0 auto" }} />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          <p style={{ color: "var(--text-secondary)", marginTop: 16 }}>Loading VGAS.AI...</p>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div style={{ minHeight: "100vh", background: "var(--bg)", color: "var(--text)", fontFamily: "var(--font-main)" }}>
        <Navbar user={user} />
        <main>
          <Routes>
            <Route path="/" element={<HomeScreen />} />
            <Route path="/compare" element={<CompareScreen />} />
            <Route path="/product/:id" element={<ProductDetailScreen />} />
            <Route path="/admin" element={<AdminDashboardScreen />} />
            <Route path="/profile" element={<ProfileScreen />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
