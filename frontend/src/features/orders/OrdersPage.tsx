/**
 * Orders seznam — tabulka zakázek s pokročilým filtrováním, řazením a stránkováním.
 */
import { useState, useMemo, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { ordersApi, distribHubsApi } from "../../api";
import type { Order, OrderStatus, DistribHub } from "../../types";
import {
  Eye,
  Download,
  Plus,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Copy,
  Mail,
  FileText,
  Image,
  AlertTriangle,
  Filter,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react";
import { useToast } from "../../components/Toast";

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

const STATUS_COLORS: Record<OrderStatus, string> = {
  New: "badge--blue",
  Adviced: "badge--yellow",
  Realized: "badge--green",
  Billed: "badge--purple",
  Canceled: "badge--red",
  Hidden: "badge--gray",
};

const STATUS_OPTIONS = [
  { value: "New", label: "Nový" },
  { value: "Adviced", label: "Zatermínováno" },
  { value: "Realized", label: "Realizováno" },
  { value: "Billed", label: "Vyúčtováno" },
  { value: "Canceled", label: "Zrušeno" },
  { value: "Hidden", label: "Skryto" },
];

const OD_OPTIONS = [
  { value: "701", label: "701 — OD Stodůlky" },
  { value: "702", label: "702" },
  { value: "703", label: "703 — OD Černý Most" },
  { value: "704", label: "704" },
  { value: "705", label: "705 — OD Liberec" },
  { value: "706", label: "706 — OD Ústí nad Labem" },
  { value: "707", label: "707 — OD Č. Budějovice" },
  { value: "708", label: "708 — OD Hradec Králové" },
  { value: "709", label: "709 — OD Plzeň" },
];

const TEAM_TYPE_ICONS: Record<string, string> = {
  By_assembly_crew: "🔧",
  By_delivery_crew: "🚚",
  By_customer: "👤",
};

export default function OrdersPage() {
  const { addToast } = useToast();
  const [sp, setSp] = useSearchParams();

  /** Helper: update one or more URL search params and reset page to 1 (unless 'page' is being set). */
  const updateParams = useCallback(
    (updates: Record<string, string | undefined>, keepPage = false) => {
      setSp((prev) => {
        const next = new URLSearchParams(prev);
        for (const [k, v] of Object.entries(updates)) {
          if (v) next.set(k, v);
          else next.delete(k);
        }
        if (!keepPage && !("page" in updates)) {
          next.delete("page");
        }
        return next;
      });
    },
    [setSp],
  );

  // Read all filter state from URL search params
  const page = Number(sp.get("page")) || 1;
  const pageSize = Number(sp.get("page_size")) || 25;
  const search = sp.get("search") ?? "";
  const statusFilter = sp.get("status") ? "" : sp.get("status_group") ?? "open";
  const status = sp.get("status") ?? "";
  const dateFrom = sp.get("date_from") ?? "";
  const dateTo = sp.get("date_to") ?? "";
  const hubFilter = sp.get("hub") ?? "";
  const mandantFilter = sp.get("mandant") ?? "";
  const odFilter = sp.get("od") ?? "";
  const teamTypeFilter = sp.get("team_type") ?? "";
  const invalidOnly = sp.get("invalid") === "true";
  const noMontageTerm = sp.get("no_montage_term") === "true";
  const ordering = sp.get("ordering") ?? "-evidence_termin";
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(
    !!(sp.get("invalid") || sp.get("no_montage_term") || sp.get("status") || sp.get("date_from") || sp.get("hub") || sp.get("od") || sp.get("team_type"))
  );

  const { data: hubs } = useQuery({
    queryKey: ["distrib-hubs"],
    queryFn: () => distribHubsApi.list(),
    select: (res) => res.data as DistribHub[],
  });

  const params: Record<string, string | number | undefined> = {
    page,
    page_size: pageSize,
    search: search || undefined,
    status_group: !status ? statusFilter || undefined : undefined,
    status: status || undefined,
    evidence_termin_after: dateFrom || undefined,
    evidence_termin_before: dateTo || undefined,
    distrib_hub: hubFilter || undefined,
    mandant: mandantFilter || undefined,
    order_number_prefix: odFilter || undefined,
    team_type: teamTypeFilter || undefined,
    invalid: invalidOnly ? "true" : undefined,
    no_montage_term: noMontageTerm ? "true" : undefined,
    ordering: ordering || undefined,
  };

  const { data, isLoading } = useQuery({
    queryKey: ["orders", params],
    queryFn: () => ordersApi.list(params),
    select: (res) => res.data,
  });

  const totalPages = useMemo(
    () => (data?.count ? Math.ceil(data.count / pageSize) : 1),
    [data?.count, pageSize],
  );

  /** Generate page numbers: first, last, and a window around current page */
  const pageNumbers = useMemo(() => {
    if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1);
    const pages: (number | "...")[] = [];
    pages.push(1);
    if (page > 3) pages.push("...");
    for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) {
      pages.push(i);
    }
    if (page < totalPages - 2) pages.push("...");
    pages.push(totalPages);
    return pages;
  }, [page, totalPages]);

  const handleSort = (field: string) => {
    const next = ordering === field ? `-${field}` : ordering === `-${field}` ? "" : field;
    updateParams({ ordering: next || undefined });
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (ordering === field) return <ArrowUp size={12} />;
    if (ordering === `-${field}`) return <ArrowDown size={12} />;
    return <ArrowUpDown size={12} className="sort-icon--inactive" />;
  };

  const handleDownloadPdf = async (orderId: number, orderNumber: string) => {
    try {
      const response = await ordersApi.downloadPdf(orderId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `protokol_${orderNumber}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      addToast("error", "Chyba při stahování PDF.");
    }
  };

  const handleExportExcel = async () => {
    try {
      const response = await ordersApi.exportExcel(params);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `zakazky_export_${new Date().toISOString().slice(0, 10)}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
      addToast("success", "Excel exportován.");
    } catch {
      addToast("error", "Chyba při exportu.");
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      addToast("info", `Zkopírováno: ${text}`);
    } catch {
      /* silent */
    }
  };

  const resetFilters = () => {
    setSp(new URLSearchParams({ status_group: "open" }));
  };

  return (
    <div className="orders-page">
      <div className="page-header">
        <h1 className="page-title">Zakázky</h1>
        <div className="page-header__actions">
          <Link to="/orders/new" className="btn btn--primary">
            <Plus size={16} /> Nová zakázka
          </Link>
          <button className="btn btn--secondary" onClick={handleExportExcel}>
            <Download size={16} /> Export
          </button>
        </div>
      </div>

      {/* Hlavní filtry */}
      <div className="filter-bar">
        <input
          type="search"
          className="input"
          placeholder="Hledat číslo, zákazník, město..."
          value={search}
          onChange={(e) => updateParams({ search: e.target.value || undefined })}
        />
        <select
          className="input input--sm"
          value={statusFilter}
          onChange={(e) => updateParams({ status_group: e.target.value || undefined, status: undefined })}
        >
          <option value="open">Otevřené</option>
          <option value="closed">Uzavřené</option>
          <option value="all">Všechny</option>
          <option value="">Včetně skrytých</option>
        </select>
        <select
          className="input input--sm"
          value={status}
          onChange={(e) => updateParams({ status: e.target.value || undefined, status_group: e.target.value ? undefined : statusFilter || undefined })}
        >
          <option value="">— Stav —</option>
          {STATUS_OPTIONS.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
        <button
          className={`btn btn--ghost btn--sm ${showAdvancedFilters ? "btn--active" : ""}`}
          onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
        >
          <Filter size={14} /> Filtry
        </button>
        <button className="btn btn--ghost btn--sm" onClick={resetFilters} title="Reset filtrů">
          <RotateCcw size={14} />
        </button>
      </div>

      {/* Rozšířené filtry — all items use filter-group for uniform height */}
      {showAdvancedFilters && (
        <div className="filter-bar filter-bar--advanced">
          <div className="filter-group">
            <label>OD</label>
            <input type="date" value={dateFrom}
              onChange={(e) => updateParams({ date_from: e.target.value || undefined })} />
          </div>
          <div className="filter-group">
            <label>DO</label>
            <input type="date" value={dateTo}
              onChange={(e) => updateParams({ date_to: e.target.value || undefined })} />
          </div>
          <div className="filter-group filter-group--wide">
            <label>Hub</label>
            <select value={hubFilter}
              onChange={(e) => updateParams({ hub: e.target.value || undefined })}>
              <option value="">Všechny huby</option>
              {hubs?.map((h) => (
                <option key={h.id} value={h.id}>{h.label}</option>
              ))}
            </select>
          </div>
          <div className="filter-group filter-group--wide">
            <label>Mandant</label>
            <select value={mandantFilter}
              onChange={(e) => updateParams({ mandant: e.target.value || undefined })}>
              <option value="">Všichni mandanti</option>
              <option value="Rhenus">Rhenus</option>
              <option value="SMS">SMS</option>
              <option value="Zlatohor">Zlatohor</option>
              <option value="Ikea">Ikea</option>
            </select>
          </div>
          <div className="filter-group">
            <label>OD</label>
            <select value={odFilter}
              onChange={(e) => updateParams({ od: e.target.value || undefined })}>
              <option value="">Všechny OD</option>
              {OD_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          <div className="filter-group">
            <label>Typ</label>
            <select value={teamTypeFilter}
              onChange={(e) => updateParams({ team_type: e.target.value || undefined })}>
              <option value="">Všechny typy</option>
              <option value="By_assembly_crew">🔧 Montážníky</option>
              <option value="By_delivery_crew">🚚 Dopravcem</option>
              <option value="By_customer">👤 Zákazníkem</option>
            </select>
          </div>
          <label className="toggle-label toggle-label--aligned">
            <input type="checkbox" checked={invalidOnly}
              onChange={(e) => updateParams({ invalid: e.target.checked ? "true" : undefined })} />
            <AlertTriangle size={14} /> Nevalidní
          </label>
          <label className="toggle-label toggle-label--aligned">
            <input type="checkbox" checked={noMontageTerm}
              onChange={(e) => updateParams({ no_montage_term: e.target.checked ? "true" : undefined })} />
            Bez termínu montáže
          </label>
        </div>
      )}

      {/* Tabulka */}
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
                  <th>Mandant</th>
                  <th className="sortable" onClick={() => handleSort("status")}>
                    Stav <SortIcon field="status" />
                  </th>
                  <th>Zákazník</th>
                  <th>Typ</th>
                  <th>Tým</th>
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
                  <th>Pozn.</th>
                  <th>Info</th>
                  <th>Akce</th>
                </tr>
              </thead>
              <tbody>
                {data?.results.map((order: Order) => (
                  <tr key={order.id} className={order.client_incomplete ? "row--warning" : ""}>
                    <td className="font-mono">
                      <Link to={`/orders/${order.id}`} className="order-link">
                        {order.order_number}
                      </Link>
                      <button
                        className="btn-icon-inline"
                        onClick={() => copyToClipboard(order.order_number)}
                        title="Kopírovat"
                      >
                        <Copy size={12} />
                      </button>
                    </td>
                    <td>{order.mandant}</td>
                    <td>
                      <span className={`badge ${STATUS_COLORS[order.status]}`}>
                        {order.status_display}
                      </span>
                    </td>
                    <td>
                      {order.client_name || <span className="text-muted">—</span>}
                      {order.client_incomplete && (
                        <span className="badge badge--red badge--sm" title="Neúplný zákazník">!</span>
                      )}
                    </td>
                    <td>
                      <span title={order.team_type_display}>
                        {TEAM_TYPE_ICONS[order.team_type] || "?"}
                      </span>
                    </td>
                    <td>{order.team_name || <span className="text-muted">—</span>}</td>
                    <td>{order.distrib_hub_label}</td>
                    <td>{order.evidence_termin}</td>
                    <td>{order.delivery_termin || "—"}</td>
                    <td>
                      {order.montage_termin
                        ? new Date(order.montage_termin).toLocaleString("cs-CZ", {
                            day: "2-digit", month: "2-digit", year: "2-digit",
                            hour: "2-digit", minute: "2-digit",
                          })
                        : "—"}
                    </td>
                    <td>
                      {order.notes ? (
                        <span className="text-truncate" title={order.notes}>
                          {order.notes.slice(0, 10)}{order.notes.length > 10 ? "…" : ""}
                        </span>
                      ) : ""}
                    </td>
                    <td className="info-icons">
                      {order.has_pdf && (
                        <button
                          className="btn-icon-inline"
                          onClick={() => handleDownloadPdf(order.id, order.order_number)}
                          title="Stáhnout PDF"
                        >
                          <FileText size={13} className="icon--success" />
                        </button>
                      )}
                      {order.mail_datum_sended && (
                        <span title="Email odeslán"><Mail size={13} className="icon--info" /></span>
                      )}
                      {order.montage_images_count > 0 && (
                        <span title={`${order.montage_images_count} fotek`}><Image size={13} className="icon--warning" /></span>
                      )}
                      {order.has_back_protocol && (
                        <Link to={`/orders/${order.id}/protocol`} title="Protokol přijat" className="btn-icon-inline">
                          <FileText size={13} className="icon--accent" />
                        </Link>
                      )}
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

          {/* Stránkování */}
          <div className="pagination">
            <div className="pagination__per-page">
              <span>Zobrazit</span>
              <select value={pageSize} onChange={(e) => updateParams({ page_size: e.target.value })}>
                {PAGE_SIZE_OPTIONS.map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
              <span>záznamů</span>
            </div>

            <div className="pagination__nav">
              <button className="pagination__btn" disabled={page <= 1}
                onClick={() => updateParams({ page: "1" }, true)} title="První strana">
                <ChevronsLeft size={14} />
              </button>
              <button className="pagination__btn" disabled={page <= 1}
                onClick={() => updateParams({ page: String(page - 1) }, true)} title="Předchozí">
                <ChevronLeft size={14} />
              </button>

              {pageNumbers.map((pn, idx) =>
                pn === "..." ? (
                  <span key={`dots-${idx}`} className="pagination__dots">…</span>
                ) : (
                  <button
                    key={pn}
                    className={`pagination__btn ${pn === page ? "pagination__btn--active" : ""}`}
                    onClick={() => updateParams({ page: String(pn) }, true)}
                  >
                    {pn}
                  </button>
                ),
              )}

              <button className="pagination__btn" disabled={page >= totalPages}
                onClick={() => updateParams({ page: String(page + 1) }, true)} title="Další">
                <ChevronRight size={14} />
              </button>
              <button className="pagination__btn" disabled={page >= totalPages}
                onClick={() => updateParams({ page: String(totalPages) }, true)} title="Poslední strana">
                <ChevronsRight size={14} />
              </button>
            </div>

            <span className="pagination__info">
              {data?.count ?? 0} zakázek
            </span>
          </div>
        </>
      )}
    </div>
  );
}
