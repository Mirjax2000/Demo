/**
 * Montážní dokumentace — obrázky z montáže, zpětný protokol, detaily.
 */
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ordersApi } from "../../api";
import type { OrderDetail } from "../../types";
import { useToast } from "../../components/Toast";
import { ArrowLeft, Download, Image, FileText, User, MapPin } from "lucide-react";

export default function AssemblyDocsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const orderId = Number(id);

  const { data: order, isLoading } = useQuery({
    queryKey: ["order", orderId],
    queryFn: () => ordersApi.detail(orderId),
    select: (res) => res.data as OrderDetail,
    enabled: !!orderId,
  });

  const handleDownloadZip = async () => {
    try {
      const response = await ordersApi.downloadMontageZip(orderId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `montaz_${order?.order_number ?? orderId}.zip`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      addToast("error", "Chyba při stahování ZIP archivu.");
    }
  };

  if (isLoading) return <div className="page-loading">Načítání...</div>;
  if (!order) return <div className="page-error">Zakázka nenalezena.</div>;

  const images = order.montage_images ?? [];
  const protocol = order.back_protocol;
  const client = order.client_detail;

  return (
    <div className="assembly-docs-page">
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">
            <Image size={22} /> Montážní dokumentace — {order.order_number}
          </h1>
        </div>
        <div className="page-header__actions">
          {images.length > 0 && (
            <button className="btn btn--secondary" onClick={handleDownloadZip}>
              <Download size={16} /> Stáhnout obrázky (ZIP)
            </button>
          )}
          <Link to={`/orders/${orderId}`} className="btn btn--primary">
            Zpět na detail
          </Link>
        </div>
      </div>

      <div className="detail-grid">
        {/* Montážní obrázky */}
        <div className="detail-card detail-card--full">
          <h3 className="detail-card__title">
            <Image size={16} /> Fotografie z montáže ({images.length})
          </h3>
          {images.length > 0 ? (
            <div className="assembly-gallery">
              {images.map((img) => (
                <div key={img.id} className="assembly-gallery__item">
                  <a href={img.image} target="_blank" rel="noopener noreferrer">
                    <img src={img.image} alt={img.alt_text || `Montáž #${img.position}`} />
                  </a>
                  <div className="assembly-gallery__meta">
                    <span>{img.alt_text || "—"}</span>
                    <small>{new Date(img.created).toLocaleString("cs-CZ")}</small>
                    <a href={img.image} download className="btn btn--ghost btn--sm">
                      <Download size={14} />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted">Žádné fotografie z montáže.</p>
          )}
        </div>

        {/* Zpětný protokol */}
        <div className="detail-card">
          <h3 className="detail-card__title">
            <FileText size={16} /> Přijatý montážní protokol
          </h3>
          {protocol ? (
            <div className="assembly-protocol">
              <a href={protocol.file} target="_blank" rel="noopener noreferrer">
                <img src={protocol.file} alt={protocol.alt_text || "Protokol"} className="assembly-protocol__img" />
              </a>
              <div className="assembly-protocol__meta">
                <p>Komentář: {protocol.alt_text || "—"}</p>
                <small>Přijato: {new Date(protocol.created).toLocaleString("cs-CZ")}</small>
                <a href={protocol.file} download className="btn btn--ghost btn--sm">
                  <Download size={14} /> Stáhnout
                </a>
              </div>
            </div>
          ) : (
            <p className="text-muted">Zpětný protokol nebyl nahrán.</p>
          )}
        </div>

        {/* Detaily montáže */}
        <div className="detail-card">
          <h3 className="detail-card__title">
            <User size={16} /> Detaily montáže
          </h3>
          <dl className="detail-list">
            <dt>Zákazník</dt>
            <dd>{client?.name ?? order.client_name ?? "—"}</dd>
            {client && (
              <>
                <dt><MapPin size={14} /> Adresa</dt>
                <dd>{client.street}, {client.city} {client.zip_code}</dd>
              </>
            )}
            <dt>Tým</dt>
            <dd>{order.team_name || "—"}</dd>
            <dt>Termín montáže</dt>
            <dd>
              {order.montage_termin
                ? new Date(order.montage_termin).toLocaleString("cs-CZ")
                : "—"}
            </dd>
            <dt>Stav</dt>
            <dd>
              <span className={`badge badge--${order.status.toLowerCase()}`}>
                {order.status_display}
              </span>
            </dd>
          </dl>
        </div>
      </div>
    </div>
  );
}
