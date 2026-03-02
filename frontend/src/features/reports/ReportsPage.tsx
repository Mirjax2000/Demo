/**
 * Sestavy (Reports) — přehled realizovaných zakázek.
 */
import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ordersApi, distribHubsApi } from "../../api";
import type { Order, OrderStatus, DistribHub } from "../../types";
import { BarChart3, Download, Eye, ArrowUpDown, ArrowUp, ArrowDown, Filter, RotateCcw } from "lucide-react";

const STATUS_COLORS: Record<OrderStatus, string> = {
  New: "badge--blue",
  Adviced: "badge--yellow",
  Realized: "badge--green",
  Billed: "badge--purple",
  Canceled: "badge--red",
  Hidden: "badge--gray",
};

export default function ReportsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [ordering, setOrdering] = useState("-evidence_termin");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [hubFilter, setHubFilter] = useState("");
  const [mandantFilter, setMandantFilter] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  const handleSort = (field: string) => {
    setOrdering((prev) => (prev === field ? `-${field}` : prev === `-${field}` ? "" : field));
    setPage(1);
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (ordering === field) return <ArrowUp size={12} />;
    if (ordering === `-${field}`) return <ArrowDown size={12} />;
    return <ArrowUpDown size={12} className="sort-icon--inactive" />;
  };

  const { data: hubs } = useQuery({
    queryKey: ["distrib-hubs"],
    queryFn: () => distribHubsApi.list(),
    select: (res) => res.data as DistribHub[],
  });

  const resetFilters = () => {
    setSearch("");
    setDateFrom("");
    setDateTo("");
    setHubFilter("");
    setMandantFilter("");
    setOrdering("-evidence_termin");
    setPage(1);
  };

  const { data, isLoading } = useQuery({
    queryKey: ["reports", page, search, ordering, dateFrom, dateTo, hubFilter, mandantFilter],
    queryFn: () =>
      ordersApi.list({
        page,
        search: search || undefined,
        status: "Realized",
        ordering: ordering || undefined,
        evidence_from: dateFrom || undefined,
        evidence_to: dateTo || undefined,
        distrib_hub: hubFilter || undefined,
        mandant: mandantFilter || undefined,
      }),
    select: (res) => res.data,
  });

  const handleExport = async () => {
    try {
      const response = await ordersApi.exportExcel({ status: "Realized" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `sestavy_realized_${new Date().toISOString().slice(0, 10)}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Chyba při exportu.");
    }
  };

  return (
    <div className="reports-page">
      <div className="page-header">
        <h1 className="page-title">
          <BarChart3 size={24} /> Sestavy — Realizované zakázky
        </h1>
        <div className="page-header__actions">
          <button className="btn btn--secondary" onClick={handleExport}>
            <Download size={16} /> Export Excel
          </button>
        </div>
      </div>

      <div className="filter-bar">
        <input
          type="search"
          className="input"
          placeholder="Hledat v sestavách..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        <button
          className={`btn btn--ghost ${showFilters ? "btn--active" : ""}`}
          onClick={() => setShowFilters((v) => !v)}
        >
          <Filter size={16} /> Filtry
        </button>
        <button className="btn btn--ghost" onClick={resetFilters}>
          <RotateCcw size={16} /> Reset
        </button>
      </div>

      {showFilters && (
        <div className="filter-bar filter-bar--advanced">
          <div className="filter-group">
            <label>Evidence od</label>
            <input type="date" className="input" value={dateFrom}
              onChange={(e) => { setDateFrom(e.target.value); setPage(1); }} />
          </div>
          <div className="filter-group">
            <label>Evidence do</label>
            <input type="date" className="input" value={dateTo}
              onChange={(e) => { setDateTo(e.target.value); setPage(1); }} />
          </div>
          <div className="filter-group">
            <label>Hub</label>
            <select className="input" value={hubFilter}
              onChange={(e) => { setHubFilter(e.target.value); setPage(1); }}>
              <option value="">Vše</option>
              {hubs?.map((h) => (
                <option key={h.id} value={h.id}>{h.code} — {h.city}</option>
              ))}
            </select>
          </div>
          <div className="filter-group">
            <label>Mandant</label>
            <select className="input" value={mandantFilter}
              onChange={(e) => { setMandantFilter(e.target.value); setPage(1); }}>
              <option value="">Vše</option>
              <option value="SCCZ">SCCZ</option>
              <option value="IKEA">IKEA</option>
            </select>
          </div>
        </div>
      )}

      <p className="text-muted" style={{ marginBottom: "0.5rem", fontSize: "0.8rem" }}>
        Tip: Klikněte na číslo zakázky pro přechod na detail. Využijte odkaz Finance pro finanční přehled.
      </p>

      {isLoading ? (
        <div className="page-loading">Načítání...</div>
      ) : (
        <>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th className="sortable" onClick={() => handleSort("order_number")}>
                    Č. zakázky <SortIcon field="order_number" />
                  </th>
                  <th className="sortable" onClick={() => handleSort("mandant")}>
                    Mandant <SortIcon field="mandant" />
                  </th>
                  <th>Stav</th>
                  <th className="sortable" onClick={() => handleSort("client__name")}>
                    Zákazník <SortIcon field="client__name" />
                  </th>
                  <th className="sortable" onClick={() => handleSort("team__name")}>
                    Tým <SortIcon field="team__name" />
                  </th>
                  <th>Místo</th>
                  <th className="sortable" onClick={() => handleSort("evidence_termin")}>
                    Evidence <SortIcon field="evidence_termin" />
                  </th>
                  <th className="sortable" onClick={() => handleSort("delivery_termin")}>
                    Doručení <SortIcon field="delivery_termin" />
                  </th>
                  <th className="sortable" onClick={() => handleSort("montage_termin")}>
                    Montáž <SortIcon field="montage_termin" />
                  </th>
                  <th>Finance</th>
                  <th>Akce</th>
                </tr>
              </thead>
              <tbody>
                {data?.results.map((order: Order) => (
                  <tr key={order.id}>
                    <td className="font-mono">
                      <Link to={`/orders/${order.id}`}>{order.order_number}</Link>
                    </td>
                    <td>{order.mandant}</td>
                    <td>
                      <span className={`badge ${STATUS_COLORS[order.status]}`}>
                        {order.status_display}
                      </span>
                    </td>
                    <td>{order.client_name || "—"}</td>
                    <td>{order.team_name || "—"}</td>
                    <td>{order.distrib_hub_label}</td>
                    <td>{order.evidence_termin}</td>
                    <td>{order.delivery_termin || "—"}</td>
                    <td>
                      {order.montage_termin
                        ? new Date(order.montage_termin).toLocaleDateString("cs-CZ")
                        : "—"}
                    </td>
                    <td>
                      <Link to={`/orders/${order.id}/finance`} className="btn btn--ghost btn--sm">
                        Finance
                      </Link>
                    </td>
                    <td>
                      <Link to={`/orders/${order.id}`} className="btn btn--icon" title="Detail">
                        <Eye size={16} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button className="btn btn--primary btn--sm" disabled={!data?.previous}
              onClick={() => setPage((p) => p - 1)}>
              ← Předchozí
            </button>
            <span className="pagination__info">
              Strana {page} ({data?.count ?? 0} zakázek)
            </span>
            <button className="btn btn--primary btn--sm" disabled={!data?.next}
              onClick={() => setPage((p) => p + 1)}>
              Další →
            </button>
          </div>
        </>
      )}
    </div>
  );
}
