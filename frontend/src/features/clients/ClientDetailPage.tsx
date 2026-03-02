/**
 * Detail zákazníka — kontakt + zakázky.
 */
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { clientsApi } from "../../api";
import type { ClientDetail, Order } from "../../types";
import { ArrowLeft, Phone, Mail, MapPin, AlertTriangle, Download, Check, X } from "lucide-react";
import { useToast } from "../../components/Toast";

export default function ClientDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const { data: client, isLoading } = useQuery({
    queryKey: ["client", slug],
    queryFn: () => clientsApi.detail(slug!),
    select: (res) => res.data as ClientDetail,
    enabled: !!slug,
  });

  const { data: ordersData } = useQuery({
    queryKey: ["client-orders", slug],
    queryFn: () => clientsApi.orders(slug!),
    select: (res) => res.data as Order[],
    enabled: !!slug,
  });

  const orders = ordersData ?? [];

  const handleExportGdpr = async () => {
    try {
      const { data } = await clientsApi.exportData(slug!);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `gdpr_export_${client?.name?.replace(/\s/g, "_") || slug}.json`;
      a.click();
      window.URL.revokeObjectURL(url);
      addToast("success", "GDPR export stažen.");
    } catch {
      addToast("error", "Chyba při exportu dat.");
    }
  };

  if (isLoading) return <div className="page-loading">Načítání...</div>;
  if (!client) return <div className="page-error">Zákazník nenalezen.</div>;

  return (
    <div className="client-detail-page">
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">{client.name}</h1>
          {client.incomplete && (
            <span className="badge badge--red">
              <AlertTriangle size={14} /> Neúplný
            </span>
          )}
        </div>
        <div className="page-header__actions">
          <button className="btn btn--ghost" onClick={handleExportGdpr} title="GDPR export">
            <Download size={16} /> Export dat
          </button>
          <Link to={`/clients/${slug}/edit`} className="btn btn--primary">
            Upravit
          </Link>
        </div>
      </div>

      <div className="detail-grid">
        <div className="detail-card">
          <h3 className="detail-card__title">Kontaktní údaje</h3>
          <dl className="detail-list">
            <dt>
              <MapPin size={14} /> Adresa
            </dt>
            <dd>
              {client.street}, {client.city} {client.formatted_psc || client.zip_code}
            </dd>
            <dt>
              <Phone size={14} /> Telefon
            </dt>
            <dd>{client.formatted_phone || client.phone || "-"}</dd>
            <dt>
              <Mail size={14} /> Email
            </dt>
            <dd>{client.email || "-"}</dd>
          </dl>
        </div>

        <div className="detail-card">
          <h3 className="detail-card__title">Statistika</h3>
          <dl className="detail-list">
            <dt>Počet zakázek</dt>
            <dd>{client.order_count ?? orders.length}</dd>
          </dl>
        </div>
      </div>

      {/* Zakázky zákazníka */}
      <div className="detail-card detail-card--full">
        <h3 className="detail-card__title">Zakázky</h3>
        {orders.length > 0 ? (
          <table className="data-table data-table--sm">
            <thead>
              <tr>
                <th>Číslo</th>
                <th>Mandant</th>
                <th>Status</th>
                <th>Tým</th>
                <th>Termín montáže</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id}>
                  <td>
                    <Link to={`/orders/${o.id}`}>{o.order_number}</Link>
                  </td>
                  <td>{o.mandant}</td>
                  <td>
                    <span className={`badge badge--sm badge--${o.status.toLowerCase()}`}>
                      {o.status}
                    </span>
                  </td>
                  <td>{o.team_name || "-"}</td>
                  <td>
                    {o.montage_termin
                      ? new Date(o.montage_termin).toLocaleDateString("cs-CZ")
                      : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-muted">Žádné zakázky.</p>
        )}
      </div>

      {/* Záznamy hovorů */}
      <div className="detail-card detail-card--full">
        <h3 className="detail-card__title">
          <Phone size={16} /> Záznamy hovorů ({client.call_logs?.length ?? 0})
        </h3>
        {client.call_logs && client.call_logs.length > 0 ? (
          <table className="data-table data-table--sm">
            <thead>
              <tr>
                <th>Stav</th>
                <th>Poznámka</th>
                <th>Autor</th>
                <th>Datum</th>
              </tr>
            </thead>
            <tbody>
              {client.call_logs.map((log) => (
                <tr key={log.id}>
                  <td>
                    {log.was_successful
                      ? <Check size={14} className="icon--success" />
                      : <X size={14} className="icon--danger" />}
                  </td>
                  <td>{log.note}</td>
                  <td>{log.user_name}</td>
                  <td>{new Date(log.called_at).toLocaleString("cs-CZ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-muted">Žádné záznamy hovorů.</p>
        )}
      </div>
    </div>
  );
}
