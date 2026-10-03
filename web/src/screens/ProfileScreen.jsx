jsx
import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";


const mockProduct = {
  id: "iphone-15-pro-max-256gb",
  name: "iPhone 15 Pro Max 256GB",
  rating: 4.5,
  image:
    "https://images.unsplash.com/photo-1701339276181-9a0e3c0f4c7d?auto=format&fit=crop&w=800&q=80",
  price: 139999,
  discount: 10, // percent
  priceHistory: Array.from({ length: 30 }, (_, i) => ({
    day: `Day ${i + 1}`,
    price: 139999 - i * 200,
  })),
  stores: [
    { name: "Amazon", price: 139999, link: "https://amazon.in" },
    { name: "Flipkart", price: 138499, link: "https://flipkart.com" },
    { name: "Myntra", price: 140499, link: "https://myntra.com" },
    { name: "Meesho", price: 137999, link: "https://meesho.com" },
  ],
  prediction: { dropTo: 132999, inDays: 5 },
  delivery: "Free Delivery • Estimated in 3‑5 days",
  specs: [
    { title: "Display", content: "6.7‑inch Super Retina XDR" },
    { title: "Processor", content: "A17 Bionic" },
    { title: "Camera", content: "48MP Triple Camera System" },
    { title: "Battery", content: "Li‑Ion 4323 mAh" },
    { title: "OS", content: "iOS 17" },
  ],
};

const StarRating = ({ rating }) => {
  const fullStars = Math.floor(rating);
  const halfStar = rating - fullStars >= 0.5;
  const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
  return (
    <div className="rating">
      {"★".repeat(fullStars)}
      {halfStar && "⯨"}
      {"☆".repeat(emptyStars)}
    </div>
  );
};

const ProductDetail = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [showSpecs, setShowSpecs] = useState(false);

  // In a real app replace with API call; using mock data for now
  useEffect(() => {
    // Simulate async fetch
    const fetchProduct = async () => {
      // await axios.get(`/api/products/${productId}`);
      setProduct(mockProduct);
    };
    fetchProduct();
  }, [productId]);

  if (!product) return <div className="loading">Loading…</div>;

  const discountedPrice = Math.round(
    product.price * (1 - product.discount / 100)
  );

  return (
    <div className="product-detail glass">
      {/* Image */}
      <div className="image-wrapper">
        <img src={product.image} alt={product.name} className="product-image" />
      </div>

      {/* Header */}
      <div className="header">
        <h1 className="title">{product.name}</h1>
        <StarRating rating={product.rating} />
        <div className="price-section">
          <span className="price-discounted">₹{discountedPrice.toLocaleString()}</span>
          <span className="price-original">₹{product.price.toLocaleString()}</span>
          <span className="badge-discount">{product.discount}% OFF</span>
        </div>
      </div>

      {/* AI Prediction */}
      <div className="prediction-banner">
        Expected price drop to <strong>₹{product.prediction.dropTo.toLocaleString()}</strong> in {product.prediction.inDays} days
      </div>

      {/* Delivery */}
      <div className="delivery-info">{product.delivery}</div>

      {/* Price History Chart */}
      <div className="chart-container">
        <h2>30‑Day Price History</h2>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={product.priceHistory}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="day" stroke="var(--secondary)" />
            <YAxis
              domain={["dataMin - 1000", "dataMax + 1000"]}
              stroke="var(--secondary)"
            />
            <Tooltip
              contentStyle={{ backgroundColor: "var(--bg)", border: "none" }}
              labelStyle={{ color: "var(--primary)" }}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="var(--primary)"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Store List */}
      <div className="stores">
        <h2>Buy from</h2>
        <div className="store-list">
          {product.stores.map((store) => (
            <div key={store.name} className="store-card glass">
              <span className="store-name">{store.name}</span>
              <span className="store-price">₹{store.price.toLocaleString()}</span>
              <button
                className="buy-btn"
                onClick={() => window.open(store.link, "_blank")}
              >
                Buy
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Specs Accordion */}
      <div className="specs">
        <h2 onClick={() => setShowSpecs((v) => !v)} className="accordion-toggle">
          Specifications {showSpecs ? "▲" : "▼"}
        </h2>
        {showSpecs && (
          <ul className="spec-list">
            {product.specs.map((s) => (
              <li key={s.title}>
                <strong>{s.title}:</strong> {s.content}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ProductDetail;