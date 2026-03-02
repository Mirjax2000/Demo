/**
 * PdfViewerPage — zobrazí PDF protokol zakázky inline v prohlížeči.
 * Standalone stránka pro mandanty s možností stažení.
 */
import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ordersApi } from "../../api";
import { ArrowLeft, Download } from "lucide-react";
import { useToast } from "../../components/Toast";

export default function PdfViewerPage() {
  const { id } = useParams<{ id: string }>();
  const orderId = Number(id);
  const { addToast } = useToast();
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let revoked = false;
    const fetchPdf = async () => {
      try {
        const res = await ordersApi.viewPdf(orderId);
        const url = URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
        if (!revoked) setPdfUrl(url);
      } catch {
        if (!revoked) setError("PDF protokol neexistuje nebo došlo k chybě.");
      } finally {
        if (!revoked) setLoading(false);
      }
    };
    fetchPdf();
    return () => {
      revoked = true;
      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderId]);

  const handleDownload = async () => {
    try {
      const res = await ordersApi.downloadPdf(orderId);
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `protokol_${orderId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      addToast("error", "Chyba při stahování PDF.");
    }
  };

  return (
    <div className="pdf-viewer-page">
      <div className="page-header">
        <Link to={`/orders/${orderId}`} className="btn btn--ghost btn--sm">
          <ArrowLeft size={16} /> Zpět na zakázku
        </Link>
        <h1 className="page-title" style={{ flex: 1 }}>PDF Protokol</h1>
        <button className="btn btn--primary btn--sm" onClick={handleDownload}>
          <Download size={16} /> Stáhnout PDF
        </button>
      </div>

      {loading && <div className="page-loading">Načítání PDF…</div>}

      {error && (
        <div className="alert alert--warning" style={{ marginTop: "1rem" }}>
          {error}
        </div>
      )}

      {pdfUrl && (
        <iframe
          src={pdfUrl}
          title="PDF Protokol"
          style={{
            width: "100%",
            height: "calc(100vh - 120px)",
            border: "1px solid var(--color-border, #d1d5db)",
            borderRadius: "8px",
            marginTop: "1rem",
          }}
        />
      )}
    </div>
  );
}
