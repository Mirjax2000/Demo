/**
 * Stránka historie změn zakázky — field-level diff (Order + Article).
 */
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ordersApi } from "../../api";
import type { HistoryRecord } from "../../types";
import { ArrowLeft, Plus, Edit, Minus, FileText, Package } from "lucide-react";

const TYPE_ICONS: Record<string, typeof Plus> = {
  Vytvořeno: Plus,
  "Created": Plus,
  Změněno: Edit,
  "Changed": Edit,
  Smazáno: Minus,
  "Deleted": Minus,
};

const TYPE_LABELS: Record<string, string> = {
  Vytvořeno: "Vytvořeno",
  "Created": "Vytvořeno",
  Změněno: "Upraveno",
  "Changed": "Upraveno",
  Smazáno: "Smazáno",
  "Deleted": "Smazáno",
};

const TYPE_COLORS: Record<string, string> = {
  Vytvořeno: "badge--green",
  "Created": "badge--green",
  Změněno: "badge--yellow",
  "Changed": "badge--yellow",
  Smazáno: "badge--red",
  "Deleted": "badge--red",
};

const FIELD_LABELS: Record<string, string> = {
  order_number: "Číslo zakázky",
  mandant: "Mandant",
  status: "Stav",
  team_type: "Typ realizace",
  distrib_hub: "Distribuční hub",
  client: "Zákazník",
  team: "Tým",
  evidence_termin: "Termín evidence",
  delivery_termin: "Termín doručení",
  montage_termin: "Termín montáže",
  naklad: "Náklad",
  vynos: "Výnos",
  notes: "Poznámky",
  name: "Název",
  quantity: "Množství",
  note: "Poznámka",
  mail_datum_sended: "Email odeslán",
  mail_team_sended: "Email tým",
};

export default function OrderHistoryPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const orderId = Number(id);

  const { data: records, isLoading } = useQuery({
    queryKey: ["order-history", orderId],
    queryFn: () => ordersApi.history(orderId),
    select: (res) => res.data as HistoryRecord[],
    enabled: !!orderId,
  });

  if (isLoading) return <div className="page-loading">Načítání...</div>;

  return (
    <div className="history-page">
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">Historie zakázky</h1>
        </div>
        <div className="page-header__actions">
          <Link to={`/orders/${orderId}`} className="btn btn--secondary">
            Zpět na detail
          </Link>
        </div>
      </div>

      {records && records.length > 0 ? (
        <div className="history-list">
          {records.map((rec) => {
            const Icon = TYPE_ICONS[rec.history_type] || Edit;
            const ModelIcon = rec.model === "Article" ? Package : FileText;
            return (
              <div key={`${rec.model}-${rec.history_id}`} className="history-item">
                <div className="history-item__head">
                  <span className={`badge badge--sm ${TYPE_COLORS[rec.history_type] || "badge--gray"}`}>
                    <Icon size={12} /> {TYPE_LABELS[rec.history_type] || rec.history_type}
                  </span>
                  <span className="badge badge--sm badge--outline">
                    <ModelIcon size={12} />
                    {rec.model === "Article"
                      ? ` Artikl${rec.article_name ? `: ${rec.article_name}` : ""}`
                      : " Zakázka"}
                  </span>
                  <time className="history-item__date">
                    {new Date(rec.history_date).toLocaleString("cs-CZ")}
                  </time>
                  <span className="history-item__user">
                    {rec.history_user || "Systém"}
                  </span>
                </div>

                {/* Field-level changes */}
                {rec.changes && rec.changes.length > 0 && (
                  <table className="history-item__changes">
                    <thead>
                      <tr>
                        <th>Pole</th>
                        <th>Původní</th>
                        <th>Nová</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rec.changes.map((ch, idx) => (
                        <tr key={idx}>
                          <td className="history-field">
                            {FIELD_LABELS[ch.field] || ch.field}
                          </td>
                          <td className="history-old">{ch.old || "-"}</td>
                          <td className="history-new">{ch.new || "-"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}

                {/* Fallback: show status/notes if no changes array */}
                {(!rec.changes || rec.changes.length === 0) && rec.status && (
                  <p className="history-item__detail">
                    Status: <strong>{rec.status}</strong>
                  </p>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-muted">Žádná historie.</p>
      )}
    </div>
  );
}
