/**
 * Login stránka — přihlášení do AMS.
 * Design odpovídá původní Django SSR aplikaci s ikonou wrench-adjustable-circle.
 */
import { useState, useEffect, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { Lock, User, AlertCircle, Loader2 } from "lucide-react";

/** Bootstrap Icons — wrench-adjustable-circle (originální ikona z Django SSR) */
function WrenchIcon({ size = 48 }: { size?: number }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      fill="currentColor"
      viewBox="0 0 16 16"
    >
      <path d="M12.496 8a4.5 4.5 0 0 1-1.703 3.526L9.497 8.5l2.959-1.11q.04.3.04.61" />
      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-1 0a7 7 0 1 0-13.202 3.249l1.988-1.657a4.5 4.5 0 0 1 7.537-4.623L7.497 6.5l1 2.5 1.333 3.11c-.56.251-1.18.39-1.833.39a4.5 4.5 0 0 1-1.592-.29L4.747 14.2A7 7 0 0 0 15 8m-8.295.139a.25.25 0 0 0-.288-.376l-1.5.5.159.474.808-.27-.595.894a.25.25 0 0 0 .287.376l.808-.27-.595.894a.25.25 0 0 0 .287.376l1.5-.5-.159-.474-.808.27.596-.894a.25.25 0 0 0-.288-.376l-.808.27z" />
    </svg>
  );
}

export default function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Navigace až PO tom, co React commitne user state
  useEffect(() => {
    if (user) navigate("/dashboard", { replace: true });
  }, [user, navigate]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      // Navigace proběhne přes useEffect výše
    } catch {
      setError("Neplatné přihlašovací údaje.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* Background decoration */}
      <div className="login-page__bg" />

      <div className="login-card">
        {/* Icon + branding */}
        <div className="login-card__brand">
          <div className="login-card__icon">
            <WrenchIcon size={48} />
          </div>
          <h1 className="login-card__title">
            Rhenus HD — <span>AMS</span>
          </h1>
          <p className="login-card__subtitle">Systém správy montáží</p>
        </div>

        {/* Divider */}
        <div className="login-card__divider" />

        {/* Error message */}
        {error && (
          <div className="login-error">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-field">
            <label htmlFor="login-username">Uživatelské jméno</label>
            <div className="login-field__input-wrap">
              <User size={16} className="login-field__icon" />
              <input
                id="login-username"
                className="input"
                type="text"
                placeholder="Zadejte jméno"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoFocus
                autoComplete="username"
              />
            </div>
          </div>

          <div className="login-field">
            <label htmlFor="login-password">Heslo</label>
            <div className="login-field__input-wrap">
              <Lock size={16} className="login-field__icon" />
              <input
                id="login-password"
                className="input"
                type="password"
                placeholder="Zadejte heslo"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>
          </div>

          <button
            type="submit"
            className="login-btn"
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 size={18} className="login-btn__spinner" />
                Přihlašování…
              </>
            ) : (
              "Přihlásit se"
            )}
          </button>
        </form>

        {/* Footer */}
        <p className="login-card__footer">
          &copy; {new Date().getFullYear()} Rhenus Home Delivery
        </p>
      </div>
    </div>
  );
}

export { WrenchIcon };
