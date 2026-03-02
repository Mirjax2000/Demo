/**
 * Detail montážního týmu — kontakt, zakázky, finance.
 */
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { teamsApi, ordersApi } from "../../api";
import type { TeamDetail, Order } from "../../types";
import { ArrowLeft, MapPin, Phone, Mail } from "lucide-react";

export default function TeamDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();

  const { data: team, isLoading: teamLoading } = useQuery({
    queryKey: ["team", slug],
    queryFn: () => teamsApi.detail(slug!),
    select: (res) => res.data as TeamDetail,
    enabled: !!slug,
  });

  const { data: ordersData } = useQuery({
    queryKey: ["team-orders", slug],
    queryFn: () => ordersApi.list({ team_id: team?.id?.toString(), page_size: "10" }),
    select: (res) => res.data,
    enabled: !!team?.id,
  });

  const orders: Order[] = ordersData?.results ?? [];

  if (teamLoading) return <div className="page-loading">Načítání...</div>;
  if (!team) return <div className="page-error">Tým nenalezen.</div>;

  return (
    <div className="team-detail-page">
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">{team.name}</h1>
          <span className={`badge ${team.active ? "badge--green" : "badge--gray"}`}>
            {team.active ? "Aktivní" : "Neaktivní"}
          </span>
        </div>
        <div className="page-header__actions">
          <Link to={`/teams/${slug}/edit`} className="btn btn--primary">
            Upravit
          </Link>
        </div>
      </div>

      <div className="detail-grid">
        {/* Kontakt */}
        <div className="detail-card">
          <h3 className="detail-card__title">Kontaktní údaje</h3>
          <dl className="detail-list">
            <dt><MapPin size={14} /> Město</dt>
            <dd>
              {team.city}
              {team.region && `, ${team.region}`}
            </dd>
            <dt><Phone size={14} /> Telefon</dt>
            <dd>{team.phone || "-"}</dd>
            <dt><Mail size={14} /> Email</dt>
            <dd>{team.email || "-"}</dd>
          </dl>
          {team.notes && (
            <p style={{ marginTop: "0.75rem", fontSize: "0.85rem", color: "var(--txt-muted)" }}>
              {team.notes}
            </p>
          )}
        </div>

        {/* Ceny */}
        <div className="detail-card">
          <h3 className="detail-card__title">Ceník</h3>
          <dl className="detail-list">
            <dt>Cena za hodinu</dt>
            <dd>{team.price_per_hour != null ? `${team.price_per_hour} Kč` : "-"}</dd>
            <dt>Cena za km</dt>
            <dd>{team.price_per_km != null ? `${team.price_per_km} Kč` : "-"}</dd>
          </dl>
        </div>
      </div>

      {/* Poslední zakázky */}
      <div className="detail-card detail-card--full">
        <h3 className="detail-card__title">Poslední zakázky</h3>
        {orders.length > 0 ? (
          <table className="data-table data-table--sm">
            <thead>
              <tr>
                <th>Číslo</th>
                <th>Mandant</th>
                <th>Status</th>
                <th>Zákazník</th>
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
                  <td>{o.client_name || "-"}</td>
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
    </div>
  );
}
