/**
 * Finance detail — příjmy a náklady zakázky s CRUD.
 */
import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ordersApi, financeApi } from "../../api";
import type { FinanceRevenueItem, FinanceCostItem, Team } from "../../types";
import { teamsApi } from "../../api";
import { useToast } from "../../components/Toast";
import { ArrowLeft, Plus, Trash2, DollarSign, Check, Pencil, X } from "lucide-react";

export default function FinancePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const orderId = Number(id);

  // Data
  const { data: order } = useQuery({
    queryKey: ["order", orderId],
    queryFn: () => ordersApi.detail(orderId),
    select: (res) => res.data,
    enabled: !!orderId,
  });

  const { data: revenueData, refetch: refetchRevenues } = useQuery({
    queryKey: ["finance-revenue", orderId],
    queryFn: () => financeApi.revenues(orderId),
    select: (res) => res.data?.results ?? (Array.isArray(res.data) ? res.data : []) as FinanceRevenueItem[],
    enabled: !!orderId,
  });

  const { data: costData, refetch: refetchCosts } = useQuery({
    queryKey: ["finance-costs", orderId],
    queryFn: () => financeApi.costs(orderId),
    select: (res) => res.data?.results ?? (Array.isArray(res.data) ? res.data : []) as FinanceCostItem[],
    enabled: !!orderId,
  });

  const { data: teams } = useQuery({
    queryKey: ["teams-all"],
    queryFn: () => teamsApi.list({ page_size: "200" }),
    select: (res) => {
      const d = res.data;
      return (d?.results ?? (Array.isArray(d) ? d : [])) as Team[];
    },
  });

  const revenues = (revenueData ?? []) as FinanceRevenueItem[];
  const costs = (costData ?? []) as FinanceCostItem[];

  // Revenue form
  const [revDesc, setRevDesc] = useState("");
  const [revAmount, setRevAmount] = useState("");

  // Cost form
  const [costDesc, setCostDesc] = useState("");
  const [costAmount, setCostAmount] = useState("");
  const [costTeam, setCostTeam] = useState("");

  // Inline edit state
  const [editRevId, setEditRevId] = useState<number | null>(null);
  const [editRevDesc, setEditRevDesc] = useState("");
  const [editRevAmount, setEditRevAmount] = useState("");
  const [editCostId, setEditCostId] = useState<number | null>(null);
  const [editCostDesc, setEditCostDesc] = useState("");
  const [editCostAmount, setEditCostAmount] = useState("");

  const invalidateAll = () => {
    refetchRevenues();
    refetchCosts();
    queryClient.invalidateQueries({ queryKey: ["order", orderId] });
  };

  const addRevenue = useMutation({
    mutationFn: () => financeApi.createRevenue({ order: orderId, description: revDesc, amount: revAmount }),
    onSuccess: () => { invalidateAll(); setRevDesc(""); setRevAmount(""); addToast("success", "Příjem přidán."); },
    onError: () => addToast("error", "Chyba při přidávání příjmu."),
  });

  const deleteRevenue = useMutation({
    mutationFn: (revId: number) => financeApi.deleteRevenue(revId),
    onSuccess: () => { invalidateAll(); addToast("success", "Příjem smazán."); },
  });

  const addCost = useMutation({
    mutationFn: () => financeApi.createCost({
      order: orderId, description: costDesc, amount: costAmount,
      team: costTeam ? Number(costTeam) : null, carrier_confirmed: false,
    }),
    onSuccess: () => { invalidateAll(); setCostDesc(""); setCostAmount(""); setCostTeam(""); addToast("success", "Náklad přidán."); },
    onError: () => addToast("error", "Chyba při přidávání nákladu."),
  });

  const deleteCost = useMutation({
    mutationFn: (costId: number) => financeApi.deleteCost(costId),
    onSuccess: () => { invalidateAll(); addToast("success", "Náklad smazán."); },
  });

  const toggleCarrier = useMutation({
    mutationFn: (item: FinanceCostItem) =>
      financeApi.updateCost(item.id, { carrier_confirmed: !item.carrier_confirmed }),
    onSuccess: () => invalidateAll(),
  });

  const updateRevenueMut = useMutation({
    mutationFn: ({ revId, data }: { revId: number; data: { description: string; amount: string } }) =>
      financeApi.updateRevenue(revId, data),
    onSuccess: () => { invalidateAll(); setEditRevId(null); addToast("success", "Příjem upraven."); },
    onError: () => addToast("error", "Chyba při úpravě příjmu."),
  });

  const updateCostMut = useMutation({
    mutationFn: ({ costId, data }: { costId: number; data: { description: string; amount: string } }) =>
      financeApi.updateCost(costId, data),
    onSuccess: () => { invalidateAll(); setEditCostId(null); addToast("success", "Náklad upraven."); },
    onError: () => addToast("error", "Chyba při úpravě nákladu."),
  });

  const startEditRevenue = (r: FinanceRevenueItem) => {
    setEditRevId(r.id);
    setEditRevDesc(r.description);
    setEditRevAmount(String(r.amount));
  };

  const startEditCost = (c: FinanceCostItem) => {
    setEditCostId(c.id);
    setEditCostDesc(c.description);
    setEditCostAmount(String(c.amount));
  };

  const totalRevenue = revenues.reduce((s, r) => s + Number(r.amount), 0);
  const totalCost = costs.reduce((s, c) => s + Number(c.amount), 0);
  const itemsProfit = totalRevenue - totalCost;

  return (
    <div className="finance-page">
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">
            <DollarSign size={22} /> Finance — {order?.order_number ?? "…"}
          </h1>
        </div>
        <div className="page-header__actions">
          <Link to={`/orders/${orderId}`} className="btn btn--secondary">Zpět na detail</Link>
        </div>
      </div>

      {/* Souhrn */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <span className="kpi-card__value">{order?.vynos ? `${Number(order.vynos).toLocaleString("cs-CZ")} Kč` : "—"}</span>
          <span className="kpi-card__label">Výnos (zakázka)</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-card__value">{order?.naklad ? `${Number(order.naklad).toLocaleString("cs-CZ")} Kč` : "—"}</span>
          <span className="kpi-card__label">Náklad (zakázka)</span>
        </div>
        <div className={`kpi-card ${Number(order?.profit) >= 0 ? "kpi-card--success" : "kpi-card--danger"}`}>
          <span className="kpi-card__value">{order ? `${Number(order.profit).toLocaleString("cs-CZ")} Kč` : "—"}</span>
          <span className="kpi-card__label">Profit (zakázka)</span>
        </div>
        <div className="kpi-card kpi-card--info">
          <span className="kpi-card__value">{itemsProfit.toLocaleString("cs-CZ")} Kč</span>
          <span className="kpi-card__label">Profit (položky)</span>
        </div>
      </div>

      {/* Příjmy */}
      <div className="detail-card detail-card--full">
        <h3 className="detail-card__title">Příjmy ({revenues.length})</h3>
        {revenues.length > 0 && (
          <table className="data-table data-table--sm">
            <thead>
              <tr><th>Popis</th><th>Částka</th><th>Datum</th><th></th></tr>
            </thead>
            <tbody>
              {revenues.map((r) => (
                <tr key={r.id}>
                  {editRevId === r.id ? (
                    <>
                      <td>
                        <input className="input input--sm" value={editRevDesc}
                          onChange={(e) => setEditRevDesc(e.target.value)} />
                      </td>
                      <td>
                        <input type="number" className="input input--sm" step="0.01" value={editRevAmount}
                          onChange={(e) => setEditRevAmount(e.target.value)} />
                      </td>
                      <td>{new Date(r.created).toLocaleDateString("cs-CZ")}</td>
                      <td className="action-cell">
                        <button className="btn btn--success btn--icon btn--sm"
                          onClick={() => updateRevenueMut.mutate({ revId: r.id, data: { description: editRevDesc, amount: editRevAmount } })}>
                          <Check size={14} />
                        </button>
                        <button className="btn btn--ghost btn--icon btn--sm"
                          onClick={() => setEditRevId(null)}>
                          <X size={14} />
                        </button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td>{r.description}</td>
                      <td className="text-success">{Number(r.amount).toLocaleString("cs-CZ")} Kč</td>
                      <td>{new Date(r.created).toLocaleDateString("cs-CZ")}</td>
                      <td className="action-cell">
                        <button className="btn btn--ghost btn--icon btn--sm"
                          onClick={() => startEditRevenue(r)} title="Upravit">
                          <Pencil size={14} />
                        </button>
                        <button className="btn btn--danger btn--icon btn--sm"
                          onClick={() => deleteRevenue.mutate(r.id)}>
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </>
                  )}
                </tr>
              ))}
              <tr className="row--total">
                <td><strong>Celkem</strong></td>
                <td className="text-success"><strong>{totalRevenue.toLocaleString("cs-CZ")} Kč</strong></td>
                <td colSpan={2}></td>
              </tr>
            </tbody>
          </table>
        )}
        <form className="inline-form" onSubmit={(e) => { e.preventDefault(); addRevenue.mutate(); }}>
          <input className="input" placeholder="Popis příjmu" value={revDesc}
            onChange={(e) => setRevDesc(e.target.value)} required />
          <input type="number" className="input input--sm" placeholder="Částka" step="0.01"
            value={revAmount} onChange={(e) => setRevAmount(e.target.value)} required />
          <button type="submit" className="btn btn--success btn--sm" disabled={addRevenue.isPending}>
            <Plus size={14} /> Přidat
          </button>
        </form>
      </div>

      {/* Náklady */}
      <div className="detail-card detail-card--full">
        <h3 className="detail-card__title">Náklady ({costs.length})</h3>
        {costs.length > 0 && (
          <table className="data-table data-table--sm">
            <thead>
              <tr><th>Popis</th><th>Částka</th><th>Tým</th><th>Dopravce</th><th>Datum</th><th></th></tr>
            </thead>
            <tbody>
              {costs.map((c) => (
                <tr key={c.id}>
                  {editCostId === c.id ? (
                    <>
                      <td>
                        <input className="input input--sm" value={editCostDesc}
                          onChange={(e) => setEditCostDesc(e.target.value)} />
                      </td>
                      <td>
                        <input type="number" className="input input--sm" step="0.01" value={editCostAmount}
                          onChange={(e) => setEditCostAmount(e.target.value)} />
                      </td>
                      <td>{c.team_name || "—"}</td>
                      <td>
                        <button className={`btn btn--icon btn--sm ${c.carrier_confirmed ? "icon--success" : ""}`}
                          onClick={() => toggleCarrier.mutate(c)}>
                          <Check size={14} />
                        </button>
                      </td>
                      <td>{new Date(c.created).toLocaleDateString("cs-CZ")}</td>
                      <td className="action-cell">
                        <button className="btn btn--success btn--icon btn--sm"
                          onClick={() => updateCostMut.mutate({ costId: c.id, data: { description: editCostDesc, amount: editCostAmount } })}>
                          <Check size={14} />
                        </button>
                        <button className="btn btn--ghost btn--icon btn--sm"
                          onClick={() => setEditCostId(null)}>
                          <X size={14} />
                        </button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td>{c.description}</td>
                      <td className="text-danger">{Number(c.amount).toLocaleString("cs-CZ")} Kč</td>
                      <td>{c.team_name || "—"}</td>
                      <td>
                        <button className={`btn btn--icon btn--sm ${c.carrier_confirmed ? "icon--success" : ""}`}
                          onClick={() => toggleCarrier.mutate(c)} title={c.carrier_confirmed ? "Potvrzeno" : "Nepotrvzeno"}>
                          <Check size={14} />
                        </button>
                      </td>
                      <td>{new Date(c.created).toLocaleDateString("cs-CZ")}</td>
                      <td className="action-cell">
                        <button className="btn btn--ghost btn--icon btn--sm"
                          onClick={() => startEditCost(c)} title="Upravit">
                          <Pencil size={14} />
                        </button>
                        <button className="btn btn--danger btn--icon btn--sm"
                          onClick={() => deleteCost.mutate(c.id)}>
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </>
                  )}
                </tr>
              ))}
              <tr className="row--total">
                <td><strong>Celkem</strong></td>
                <td className="text-danger"><strong>{totalCost.toLocaleString("cs-CZ")} Kč</strong></td>
                <td colSpan={4}></td>
              </tr>
            </tbody>
          </table>
        )}
        <form className="inline-form" onSubmit={(e) => { e.preventDefault(); addCost.mutate(); }}>
          <input className="input" placeholder="Popis nákladu" value={costDesc}
            onChange={(e) => setCostDesc(e.target.value)} required />
          <input type="number" className="input input--sm" placeholder="Částka" step="0.01"
            value={costAmount} onChange={(e) => setCostAmount(e.target.value)} required />
          <select className="input input--sm" value={costTeam} onChange={(e) => setCostTeam(e.target.value)}>
            <option value="">— Tým —</option>
            {teams?.map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
          <button type="submit" className="btn btn--danger btn--sm" disabled={addCost.isPending}>
            <Plus size={14} /> Přidat
          </button>
        </form>
      </div>
    </div>
  );
}
