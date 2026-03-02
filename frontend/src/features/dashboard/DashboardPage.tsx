/**
 * Dashboard stránka — statistiky a přehledy s filtry.
 * Layout odpovídá originálnímu Django SSR:
 *   Row 1: 4 grafy (otevřené, uzavřené, typ zatermínovaných, finance)
 *   Row 2: invalid_orders card + new_issues_orders tabulka
 *   Row 3: placeholder card + customer_r_orders tabulka s akcemi
 */
import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { dashboardApi, distribHubsApi, ordersApi } from "../../api";
import type { DistribHub, Order } from "../../types";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import {
  Filter,
  RotateCcw,
  AlertTriangle,
  Trash2,
  Users,
  EyeOff,
  CalendarOff,
  ShieldAlert,
} from "lucide-react";

const COLORS = ["#3384ff", "#fd7e14", "#10b981", "#ef4444", "#8b5cf6", "#6366f1"];
const MONTHS = [
  { value: "", label: "Vše" },
  { value: "1", label: "Leden" }, { value: "2", label: "Únor" },
  { value: "3", label: "Březen" }, { value: "4", label: "Duben" },
  { value: "5", label: "Květen" }, { value: "6", label: "Červen" },
  { value: "7", label: "Červenec" }, { value: "8", label: "Srpen" },
  { value: "9", label: "Září" }, { value: "10", label: "Říjen" },
  { value: "11", label: "Listopad" }, { value: "12", label: "Prosinec" },
];

const currentYear = new Date().getFullYear();

/** Format ISO date string to d.m.YYYY */
function fmtDate(iso: string | null | undefined): string | null {
  if (!iso) return null;
  const d = new Date(iso);
  if (isNaN(d.getTime())) return null;
  return `${d.getDate()}.${d.getMonth() + 1}.${d.getFullYear()}`;
}

export default function DashboardPage() {
  const [month, setMonth] = useState("");
  const [year, setYear] = useState("");
  const [mandant, setMandant] = useState("");
  const [hub, setHub] = useState("");

  const queryClient = useQueryClient();

  const params: Record<string, string | undefined> = {
    month: month || undefined,
    year: year || undefined,
    mandant: mandant || undefined,
    distrib_hub: hub || undefined,
  };

  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard", params],
    queryFn: () => dashboardApi.get(params),
    select: (res) => res.data,
  });

  const { data: hubs } = useQuery({
    queryKey: ["distrib-hubs"],
    queryFn: () => distribHubsApi.list(),
    select: (res) => res.data as DistribHub[],
  });

  const resetFilters = () => {
    setMonth("");
    setYear("");
    setMandant("");
    setHub("");
  };

  /** Refresh dashboard data after an action mutation */
  const refreshDashboard = () => {
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  if (isLoading) return <div className="page-loading">Načítání...</div>;
  if (error) return <div className="page-error">Chyba načítání dashboardu.</div>;
  if (!data) return null;

  const openOrdersData = [
    { name: "Nové", value: data.open_orders.nove },
    { name: "Zatermínované", value: data.open_orders.zaterminovane },
    { name: "Realizované", value: data.open_orders.realizovane },
  ];

  const closedOrdersData = [
    { name: "Vyúčtované", value: data.closed_orders.vyuctovane },
    { name: "Zrušené", value: data.closed_orders.zrusene },
  ];

  const advicedTypeData = [
    { name: "Montážní", value: data.adviced_type_orders?.montazni ?? 0 },
    { name: "Dopravní", value: data.adviced_type_orders?.dopravni ?? 0 },
  ];

  const financeData = [
    { name: "Výnosy", value: data.finance_summary.vynos },
    { name: "Náklady", value: data.finance_summary.naklad },
    { name: "Profit", value: data.finance_summary.profit },
  ];

  return (
    <div className="dashboard-page">
      <h1 className="page-title">Dashboard</h1>

      {/* ═══ Filter bar ═══ */}
      <div className="filter-bar">
        <Filter size={16} />
        <div className="filter-group">
          <label>Rok</label>
          <select className="input input--sm" value={year} onChange={(e) => setYear(e.target.value)}>
            <option value="">Vše</option>
            {(data.year_options ?? [currentYear]).map((y: number) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>Měsíc</label>
          <select className="input input--sm" value={month} onChange={(e) => setMonth(e.target.value)}>
            {MONTHS.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>
        <div className="filter-group filter-group--wide">
          <label>Mandant</label>
          <select className="input input--sm" value={mandant} onChange={(e) => setMandant(e.target.value)}>
            <option value="">Všichni mandanti</option>
            {[...new Set(data.mandant_options ?? [])].map((m: string) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
        <div className="filter-group filter-group--wide">
          <label>Hub</label>
          <select className="input input--sm" value={hub} onChange={(e) => setHub(e.target.value)}>
            <option value="">Všechny huby</option>
            {hubs?.map((h) => (
              <option key={h.id} value={h.id}>{h.label}</option>
            ))}
          </select>
        </div>
        <button className="btn btn--ghost btn--sm" onClick={resetFilters} title="Reset filtrů">
          <RotateCcw size={14} />
        </button>
      </div>

      {/* ═══ Row 1: Charts (2×2) on left + KPI counters on right ═══ */}
      <div className="dashboard-top-row">
        {/* Charts 2×2 grid */}
        <div className="dashboard-charts-2x2">
          <div className="chart-card chart-card--sm">
            <h3 className="chart-card__title">Otevřené zakázky</h3>
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={openOrdersData} cx="50%" cy="50%" innerRadius={35} outerRadius={65} dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}>
                  {openOrdersData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                </Pie>
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: "0.6rem" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card chart-card--sm">
            <h3 className="chart-card__title">Uzavřené zakázky</h3>
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={closedOrdersData} cx="50%" cy="50%" innerRadius={35} outerRadius={65} dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}>
                  {closedOrdersData.map((_, i) => <Cell key={i} fill={COLORS[i + 3]} />)}
                </Pie>
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: "0.6rem" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card chart-card--sm">
            <h3 className="chart-card__title">Zatermínované podle typu</h3>
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={advicedTypeData} cx="50%" cy="50%" innerRadius={35} outerRadius={65} dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}>
                  {advicedTypeData.map((_, i) => <Cell key={i} fill={COLORS[i + 1]} />)}
                </Pie>
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: "0.6rem" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card chart-card--sm">
            <h3 className="chart-card__title">Výnos vs. Náklady a Zisk</h3>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={financeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="name" stroke="var(--txt-muted)" />
                <YAxis stroke="var(--txt-muted)" />
                <Tooltip
                  formatter={(value) => `${Number(value ?? 0).toLocaleString("cs-CZ")} Kč`}
                  contentStyle={{ background: "var(--bck-card)", border: "1px solid var(--border)" }}
                />
                <Bar dataKey="value" fill="var(--accent)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* KPI counters — clickable, link to Orders page with filters */}
        <div className="dashboard-kpi-stack">
          <Link to="/orders?status_group=all" className="kpi-card kpi-card--link">
            <span className="kpi-card__value">{data.count_all}</span>
            <span className="kpi-card__label">Celkem</span>
          </Link>
          <Link to="/orders?invalid=true" className="kpi-card kpi-card--danger kpi-card--link">
            <span className="kpi-card__value">{data.invalid_count}</span>
            <span className="kpi-card__label"><ShieldAlert size={10} /> Nevalidní</span>
          </Link>
          <Link to="/orders?status=Hidden" className="kpi-card kpi-card--link">
            <span className="kpi-card__value">{data.hidden}</span>
            <span className="kpi-card__label"><EyeOff size={10} /> Skryto</span>
          </Link>
          <Link to="/orders?no_montage_term=true" className="kpi-card kpi-card--info kpi-card--link">
            <span className="kpi-card__value">{data.no_montage_term_count}</span>
            <span className="kpi-card__label"><CalendarOff size={10} /> Bez termínu montáže</span>
          </Link>
          <Link to={`/orders?status=New&status_group=`} className="kpi-card kpi-card--warning kpi-card--link">
            <span className="kpi-card__value">{data.new_issues_count}</span>
            <span className="kpi-card__label"><AlertTriangle size={10} /> Nové s problémy</span>
          </Link>
          {data.customer_r_count > 0 && (
            <div className="kpi-card kpi-card--info">
              <span className="kpi-card__value">{data.customer_r_count}</span>
              <span className="kpi-card__label"><Users size={10} /> Reklamace -R</span>
            </div>
          )}
          <div className="kpi-card kpi-card--success">
            <span className="kpi-card__value">
              {data.finance_summary.profit.toLocaleString("cs-CZ")} Kč
            </span>
            <span className="kpi-card__label">Profit</span>
          </div>
        </div>
      </div>

      {/* ═══ Row 2: New Issues Table (always visible) ═══ */}
      <NewIssuesTable orders={data.new_issues_orders ?? []} />

      {/* ═══ Row 3: Customer-R orders table (always visible) ═══ */}
      <CustomerRTable orders={data.customer_r_orders ?? []} onAction={refreshDashboard} />
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   New Issues Table — matches new_orders_issues.html
   Columns: Číslo zakázky, Evidence, Doručení, Montážní tým, Zákazník, Problém
   ══════════════════════════════════════════════════════════════════ */
function NewIssuesTable({ orders }: { orders: Order[] }) {
  return (
    <div className="dashboard-detail-table">
      <h3 className="dashboard-detail-table__title">
        <AlertTriangle size={14} /> Nové zakázky s chybějícími údaji
      </h3>
      <div className="table-responsive">
        <table className="data-table data-table--compact">
          <thead>
            <tr>
              <th>Číslo zakázky</th>
              <th>Evidence</th>
              <th>Doručení</th>
              <th>Montážní tým</th>
              <th>Zákazník</th>
              <th>Problém</th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center text-muted">
                  Žádné problémové zakázky
                </td>
              </tr>
            ) : (
              orders.map((o) => {
                const missingDelivery = !o.delivery_termin;
                const missingTeam = !o.team_name && o.team_type === "By_assembly_crew";
                const noClient = !o.client;
                const incompleteClient = !!o.client && !!o.client_incomplete;

                return (
                  <tr key={o.id}>
                    <td>
                      <Link to={`/orders/${o.id}`} className="link--accent">
                        {o.order_number}
                      </Link>
                    </td>
                    <td>{fmtDate(o.evidence_termin) ?? "—"}</td>
                    <td>
                      {o.delivery_termin ? (
                        fmtDate(o.delivery_termin)
                      ) : (
                        <span className="badge badge--warning">chybí</span>
                      )}
                    </td>
                    <td>
                      {o.team_name ? (
                        o.team_name
                      ) : o.team_type === "By_assembly_crew" ? (
                        <span className="badge badge--warning">chybí</span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>
                      {o.client_name ? (
                        <>
                          {o.client_name}
                          {o.client_incomplete && (
                            <span className="badge badge--warning ms-1">neúplné</span>
                          )}
                        </>
                      ) : (
                        <span className="badge badge--warning">bez zákazníka</span>
                      )}
                    </td>
                    <td>
                      {missingDelivery && (
                        <span className="badge badge--danger">bez doručení</span>
                      )}
                      {missingTeam && (
                        <span className="badge badge--danger">bez montážního týmu</span>
                      )}
                      {(noClient || incompleteClient) && (
                        <span className="badge badge--danger">neúplné kontakty</span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   Customer-R Table — matches customer_r_orders.html
   Columns: Číslo zakázky, Zákazník, Poznámka, Akce
   Action pattern: toggle switch "Opravdu přepnout?" enables buttons
   ══════════════════════════════════════════════════════════════════ */
function CustomerRTable({
  orders,
  onAction,
}: {
  orders: Order[];
  onAction: () => void;
}) {
  // Track which rows have the confirmation toggle checked
  const [confirmed, setConfirmed] = useState<Record<number, boolean>>({});
  const [loading, setLoading] = useState<Record<number, string>>({});

  const toggle = (id: number) =>
    setConfirmed((prev) => ({ ...prev, [id]: !prev[id] }));

  const handleHide = async (id: number) => {
    setLoading((p) => ({ ...p, [id]: "hide" }));
    try {
      await ordersApi.hide(id);
      onAction();
    } catch {
      /* handled by global error */
    } finally {
      setLoading((p) => {
        const next = { ...p };
        delete next[id];
        return next;
      });
      setConfirmed((p) => ({ ...p, [id]: false }));
    }
  };

  const handleSwitchToAssembly = async (id: number) => {
    setLoading((p) => ({ ...p, [id]: "assembly" }));
    try {
      await ordersApi.switchToAssembly(id);
      onAction();
    } catch {
      /* handled by global error */
    } finally {
      setLoading((p) => {
        const next = { ...p };
        delete next[id];
        return next;
      });
      setConfirmed((p) => ({ ...p, [id]: false }));
    }
  };

  return (
    <div className="dashboard-detail-table">
      <h3 className="dashboard-detail-table__title">
        <Users size={14} /> Reklamace — k rozhodnutí, jestli jde o montáž
      </h3>
      <div className="table-responsive">
        <table className="data-table data-table--compact">
          <thead>
            <tr>
              <th>Číslo zakázky</th>
              <th>Zákazník</th>
              <th>Poznámka</th>
              <th>Akce</th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center text-muted">
                  Žádné reklamace k rozhodnutí
                </td>
              </tr>
            ) : (
              orders.map((o) => {
                const isConfirmed = !!confirmed[o.id];
                const rowLoading = loading[o.id];

                return (
                  <tr key={o.id}>
                    <td>
                      <Link to={`/orders/${o.id}`} className="link--accent">
                        {o.order_number}
                      </Link>
                    </td>
                    <td>
                      {o.client_name ? (
                        o.client_name
                      ) : (
                        <span className="badge badge--warning">bez zákazníka</span>
                      )}
                    </td>
                    <td>{o.notes || "—"}</td>
                    <td>
                      <div className="cr-actions">
                        {/* Confirmation toggle — matches original form-switch */}
                        <label className="cr-actions__switch">
                          <input
                            type="checkbox"
                            checked={isConfirmed}
                            onChange={() => toggle(o.id)}
                          />
                          <span className="cr-actions__slider" />
                          <span className="cr-actions__switch-label">
                            Opravdu přepnout?
                          </span>
                        </label>

                        {/* "Bez montáže" — hide order (danger) */}
                        <button
                          className="btn btn--danger btn--xs"
                          disabled={!isConfirmed || !!rowLoading}
                          onClick={() => handleHide(o.id)}
                        >
                          <Trash2 size={12} />
                          {rowLoading === "hide" ? "…" : "Bez montáže"}
                        </button>

                        {/* "Montáž" — switch to assembly crew (warning) */}
                        <button
                          className="btn btn--warning btn--xs"
                          disabled={!isConfirmed || !!rowLoading}
                          onClick={() => handleSwitchToAssembly(o.id)}
                        >
                          <Users size={12} />
                          {rowLoading === "assembly" ? "…" : "Montáž"}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
