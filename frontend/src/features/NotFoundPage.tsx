/**
 * NotFoundPage — 404 stránka pro neznámé URL.
 */
import { Link } from "react-router-dom";
import { Home } from "lucide-react";

export default function NotFoundPage() {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "60vh",
        textAlign: "center",
        gap: "1rem",
        padding: "2rem",
      }}
    >
      <h1 style={{ fontSize: "5rem", fontWeight: 800, opacity: 0.15, margin: 0 }}>
        404
      </h1>
      <h2 style={{ margin: 0 }}>Stránka nenalezena</h2>
      <p style={{ opacity: 0.6, maxWidth: 400 }}>
        Požadovaná stránka neexistuje nebo byla přesunuta.
      </p>
      <Link to="/dashboard" className="btn btn--primary">
        <Home size={16} /> Zpět na Dashboard
      </Link>
    </div>
  );
}
