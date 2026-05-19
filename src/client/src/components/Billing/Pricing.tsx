import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import PrivateRoute from "../Common/PrivateRoute";
import "./Pricing.css";

const PricingTable: React.FC = () => {
  const { token, user, logout } = useAuth(); // auth context gives us JWT and user info for display
  const navigate = useNavigate();            // navigation for the logout redirect 
  const location = useLocation();            // used to mark which nav link is active
  const priceId5 =
    process.env.REACT_APP_PRICE_ID_5 || "price_1SYcpkLaHFh9HK7m3WHKgdyY";
  const priceId10 =
    process.env.REACT_APP_PRICE_ID_10 || "price_1SYcsrLaHFh9HK7mHz0PM1Tf";
  // These defaults are handy for demos; swap them with env vars in production so they align with your Stripe dashboard.
  const [isLoading, setIsLoading] = useState(false);       // button loading state during Stripe session creation
  const [error, setError] = useState<string | null>(null); // surface any errors to the user

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (path: string) => location.pathname === path;

  const startCheckout = async (priceId: string) => {
    // Trigger Stripe Checkout via backend; redirect to Stripe if session is created
    if (!token) {
      setError("You need to be logged in to start checkout.");
      return;
    }
    if (!priceId) {
      setError("Price ID is not configured.");
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const origin = window.location.origin;
      const response = await fetch("http://localhost:8000/billing/checkout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          price_id: priceId,
          success_url: `${origin}/dashboard?payment=success`,
          cancel_url: `${origin}/dashboard?payment=cancel`,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "Failed to create checkout session");
      }

      const data = await response.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error("Missing checkout URL");
      }
    } catch (err: any) {
      setError(err.message || "Failed to start checkout");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="billing-page">
      <div className="billing-background" />
      <div className="billing-inner">
        <header className="billing-header">
          <div className="brand">
            <Link to="/dashboard" className="brand-title">
              StoryGen
            </Link>
            <span className="brand-subtitle">Billing</span>
          </div>
          <nav className="billing-nav">
            {/* Keep nav consistent with the other authenticated screens */}
            <Link
              to="/dashboard"
              className={`nav-link ${isActive("/dashboard") ? "active" : ""}`}
            >
              Dashboard
            </Link>
            <Link
              to="/generate"
              className={`nav-link ${isActive("/generate") ? "active" : ""}`}
            >
              Generate
            </Link>
            <Link
              to="/billing"
              className={`nav-link ${isActive("/billing") ? "active" : ""}`}
            >
              Billing
            </Link>
          </nav>
          <div className="nav-user">
            {/* Show who is signed in and their current balance */}
            <div className="nav-meta">
              <span className="nav-email">{user?.email || "Loading user..."}</span>
              <span className="nav-credits">Credits: {user?.credits ?? 0}</span>
            </div>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </header>

        <main className="pricing-content">
          <h1>Buy Credits</h1>
          <p>
            Pick a pack, complete Stripe Checkout, and credits will appear in your
            account.
          </p>
          {/* Render the available credit bundles */}
          <div className="cards-grid">
            <div className="card">
              <h3>5 credits</h3>
              <p>Starter pack</p>
              <button
                onClick={() => startCheckout(priceId5)}
                disabled={isLoading}
                className="btn btn-primary"
              >
                {isLoading ? "Redirecting..." : "Checkout"}
              </button>
            </div>
            <div className="card">
              <h3>10 credits</h3>
              <p>Best value</p>
              <button
                onClick={() => startCheckout(priceId10)}
                disabled={isLoading}
                className="btn btn-success"
              >
                {isLoading ? "Redirecting..." : "Checkout"}
              </button>
            </div>
          </div>
          {/* Show any checkout creation errors */}
          {error && <div className="error-banner">{error}</div>}
        </main>
      </div>
    </div>
  );
};

export default function BillingPage() {
  return (
    // Protected route ensures only authenticated users can access billing
    <PrivateRoute>
      <PricingTable />
    </PrivateRoute>
  );
}
