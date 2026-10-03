jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";


const mockUser = {
  avatar: "https://i.pravatar.cc/150?img=3",
  name: "Arun Kumar",
  email: "arun.kumar@example.com",
  phone: "+91 98765 43210",
};

const mockStats = {
  alerts: 12,
  earnings: 4500,
  wishlist: 28,
  orders: 45,
};

const menuItems = [
  { label: "My Alerts", path: "/alerts" },
  { label: "Payment Methods", path: "/payments" },
  { label: "Affiliate Dashboard", path: "/affiliate" },
  { label: "Notification Settings", path: "/notifications" },
  { label: "Language", path: "/language" },
  { label: "Help", path: "/help" },
  { label: "Logout", path: "/logout" },
];

export default function Profile() {
  const navigate = useNavigate();
  const [user, setUser] = useState(mockUser);
  const [stats, setStats] = useState(mockStats);

  // Example of real fetch – currently using mock data
  useEffect(() => {
    async function fetchData() {
      try {
        // const res = await axios.get("/api/profile");
        // setUser(res.data.user);
        // setStats(res.data.stats);
      } catch (e) {
        console.error("Failed to fetch profile data", e);
      }
    }
    fetchData();
  }, []);

  const handleNav = (path) => {
    if (path === "/logout") {
      // logout logic here
    }
    navigate(path);
  };

  return (
    <div className="profile-screen">
      <div className="vip-banner">
        <span>VIP Membership</span>
      </div>

      <div className="user-card">
        <div className="avatar-wrapper">
          <img src={user.avatar} alt="Avatar" className="avatar" />
          <div className="glow-ring" />
        </div>
        <div className="user-info">
          <h2 className="user-name">{user.name}</h2>
          <p className="user-email">{user.email}</p>
          <p className="user-phone">{user.phone}</p>
        </div>
      </div>

      <div className="stats-row">
        <div className="stat-item">
          <span className="stat-number mono">{stats.alerts}</span>
          <span className="stat-label">Saved Alerts</span>
        </div>
        <div className="stat-item">
          <span className="stat-number mono">
            ₹{stats.earnings.toLocaleString()}
          </span>
          <span className="stat-label">Affiliate Earnings</span>
        </div>
        <div className="stat-item">
          <span className="stat-number mono">{stats.wishlist}</span>
          <span className="stat-label">Wishlist</span>
        </div>
        <div className="stat-item">
          <span className="stat-number mono">{stats.orders}</span>
          <span className="stat-label">Orders</span>
        </div>
      </div>

      <ul className="menu-list">
        {menuItems.map((item) => (
          <li
            key={item.label}
            className="menu-item"
            onClick={() => handleNav(item.path)}
          >
            {item.label}
          </li>
        ))}
      </ul>
    </div>
  );
}