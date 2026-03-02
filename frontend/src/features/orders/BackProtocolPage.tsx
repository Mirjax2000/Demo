/**
 * Back Protocol Page — veřejná stránka pro nahrání zpětného protokolu.
 *
 * Montážní tým klikne na link v emailu → validace tokenu → upload fotky protokolu.
 * Stránka nevyžaduje přihlášení (token-gated).
 */
import { useState, useEffect, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";
import { Upload, CheckCircle, AlertTriangle, Loader } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "";

interface OrderInfo {
  order_id: number;
  order_number: string;
  client_name: string | null;
  team_name: string | null;
  has_back_protocol: boolean;
}

type PageState = "loading" | "valid" | "invalid" | "uploading" | "success" | "error";

export default function BackProtocolPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [pageState, setPageState] = useState<PageState>("loading");
  const [orderInfo, setOrderInfo] = useState<OrderInfo | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  // Validace tokenu
  const validateToken = useCallback(async () => {
    if (!token) {
      setErrorMsg("Token chybí v URL.");
      setPageState("invalid");
      return;
    }
    try {
      const { data } = await axios.get(`${API_BASE}/api/v1/back-protocol/validate/`, {
        params: { token },
      });
      setOrderInfo(data);
      setPageState("valid");
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setErrorMsg(err.response?.data?.detail || "Neplatný token.");
      } else {
        setErrorMsg("Nepodařilo se ověřit token.");
      }
      setPageState("invalid");
    }
  }, [token]);

  useEffect(() => {
    validateToken();
  }, [validateToken]);

  // Preview souboru
  useEffect(() => {
    if (!file) {
      setPreview(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  // Upload
  const handleUpload = async () => {
    if (!file || !token) return;
    setPageState("uploading");

    const formData = new FormData();
    formData.append("token", token);
    formData.append("image", file);

    try {
      await axios.post(`${API_BASE}/api/v1/back-protocol/upload/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setPageState("success");
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setErrorMsg(err.response?.data?.detail || "Chyba při nahrávání.");
      } else {
        setErrorMsg("Neočekávaná chyba.");
      }
      setPageState("error");
    }
  };

  // ── Render ──
  return (
    <div className="back-protocol-page" style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>Zpětný protokol</h1>

        {/* Loading */}
        {pageState === "loading" && (
          <div style={styles.center}>
            <Loader size={32} className="spin" />
            <p>Ověřuji token...</p>
          </div>
        )}

        {/* Invalid token */}
        {pageState === "invalid" && (
          <div style={styles.alert}>
            <AlertTriangle size={24} />
            <p>{errorMsg}</p>
          </div>
        )}

        {/* Valid — upload form */}
        {(pageState === "valid" || pageState === "uploading") && orderInfo && (
          <>
            <div style={styles.info}>
              <p>
                <strong>Zakázka:</strong> {orderInfo.order_number}
              </p>
              {orderInfo.client_name && (
                <p>
                  <strong>Zákazník:</strong> {orderInfo.client_name}
                </p>
              )}
              {orderInfo.team_name && (
                <p>
                  <strong>Tým:</strong> {orderInfo.team_name}
                </p>
              )}
              {orderInfo.has_back_protocol && (
                <p style={{ color: "#e67e00" }}>
                  ⚠️ Pro tuto zakázku již byl nahraný protokol. Nový nahradí předchozí.
                </p>
              )}
            </div>

            <div style={styles.uploadArea}>
              <label htmlFor="protocol-file" style={styles.fileLabel}>
                <Upload size={40} />
                <span>
                  {file ? file.name : "Klikněte nebo přetáhněte fotografii protokolu"}
                </span>
              </label>
              <input
                id="protocol-file"
                type="file"
                accept="image/*"
                capture="environment"
                style={{ display: "none" }}
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </div>

            {preview && (
              <div style={styles.preview}>
                <img
                  src={preview}
                  alt="Náhled"
                  style={{ maxWidth: "100%", maxHeight: "300px", borderRadius: "8px" }}
                />
              </div>
            )}

            <button
              onClick={handleUpload}
              disabled={!file || pageState === "uploading"}
              style={{
                ...styles.btn,
                opacity: !file || pageState === "uploading" ? 0.5 : 1,
              }}
            >
              {pageState === "uploading" ? (
                <>
                  <Loader size={18} className="spin" /> Nahrávám...
                </>
              ) : (
                <>
                  <Upload size={18} /> Odeslat protokol
                </>
              )}
            </button>
          </>
        )}

        {/* Success */}
        {pageState === "success" && (
          <div style={styles.success}>
            <CheckCircle size={48} color="#28a745" />
            <h2>Vše proběhlo v pořádku</h2>
            <p>Protokol byl úspěšně přijat. Děkujeme!</p>
          </div>
        )}

        {/* Error after upload attempt */}
        {pageState === "error" && (
          <div style={styles.alert}>
            <AlertTriangle size={24} />
            <p>{errorMsg}</p>
            <button
              onClick={() => setPageState("valid")}
              style={{ ...styles.btn, marginTop: "1rem", background: "#6c757d" }}
            >
              Zkusit znovu
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Inline styles (stránka je public, bez layout) ──
const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#f0f2f5",
    padding: "1rem",
    fontFamily: "'Segoe UI', sans-serif",
  },
  card: {
    background: "#fff",
    borderRadius: "12px",
    boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
    padding: "2rem",
    maxWidth: "500px",
    width: "100%",
  },
  title: {
    textAlign: "center" as const,
    marginBottom: "1.5rem",
    color: "#1a73e8",
    fontSize: "1.5rem",
  },
  center: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: "0.5rem",
    color: "#666",
  },
  alert: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: "0.5rem",
    color: "#dc3545",
    textAlign: "center" as const,
    padding: "1rem",
  },
  info: {
    background: "#f8f9fa",
    borderRadius: "8px",
    padding: "1rem",
    marginBottom: "1rem",
    fontSize: "0.9rem",
  },
  uploadArea: {
    border: "2px dashed #1a73e8",
    borderRadius: "12px",
    padding: "2rem",
    textAlign: "center" as const,
    cursor: "pointer",
    marginBottom: "1rem",
    transition: "border-color 0.2s",
  },
  fileLabel: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: "0.5rem",
    cursor: "pointer",
    color: "#555",
  },
  preview: {
    textAlign: "center" as const,
    marginBottom: "1rem",
  },
  btn: {
    width: "100%",
    padding: "0.75rem",
    background: "#1a73e8",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontSize: "1rem",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "0.5rem",
  },
  success: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: "0.75rem",
    padding: "2rem 0",
    textAlign: "center" as const,
  },
};
