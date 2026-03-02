/**
 * Order detail stránka — kompletní informace o zakázce.
 * Status-dependent akce, potvrzovací checkbox, protokol/finance/historie odkazy.
 */
import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ordersApi } from "../../api";
import type { OrderStatus } from "../../types";
import { useToast } from "../../components/Toast";
import {
  ArrowLeft,
  FileText,
  Mail,
  EyeOff,
  CheckCircle,
  History,
  Edit,
  Trash2,
  DollarSign,
  ArrowRightCircle,
  Copy,
  AlertTriangle,
  ExternalLink,
} from "lucide-react";

const STATUS_LABELS: Record<OrderStatus, string> = {
  New: "Nový",
  Adviced: "Zatermínováno",
  Realized: "Realizováno",
  Billed: "Vyúčtováno",
  Canceled: "Zrušeno",
  Hidden: "Skryto",
};

export default function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const orderId = Number(id);

  const [hideConfirm, setHideConfirm] = useState(false);
  const [realizeConfirm, setRealizeConfirm] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(false);

  const { data: order, isLoading } = useQuery({
    queryKey: ["order", orderId],
    queryFn: () => ordersApi.detail(orderId),
    select: (res) => res.data,
    enabled: !!orderId,
  });

  const invalidateOrder = () => {
    queryClient.invalidateQueries({ queryKey: ["order", orderId] });
    queryClient.invalidateQueries({ queryKey: ["orders"] });
  };

  const hideMutation = useMutation({
    mutationFn: () => ordersApi.hide(orderId),
    onSuccess: () => { invalidateOrder(); addToast("success", "Zakázka skryta."); setHideConfirm(false); },
    onError: () => addToast("error", "Chyba při skrývání zakázky."),
  });

  const realizeMutation = useMutation({
    mutationFn: () => ordersApi.switchToRealized(orderId),
    onSuccess: () => { invalidateOrder(); addToast("success", "Zakázka realizována."); setRealizeConfirm(false); },
    onError: () => addToast("error", "Chyba při realizaci."),
  });

  const deleteMutation = useMutation({
    mutationFn: () => ordersApi.delete(orderId),
    onSuccess: () => { addToast("success", "Zakázka smazána."); navigate("/orders"); },
    onError: () => addToast("error", "Chyba při mazání."),
  });

  const switchToAssemblyMutation = useMutation({
    mutationFn: () => ordersApi.switchToAssembly(orderId),
    onSuccess: () => { invalidateOrder(); addToast("success", "Přepnuto na montáž."); },
    onError: () => addToast("error", "Chyba při přepínání."),
  });

  const generatePdfMutation = useMutation({
    mutationFn: () => ordersApi.generatePdf(orderId),
    onSuccess: () => { invalidateOrder(); addToast("success", "PDF vygenerován."); },
    onError: () => addToast("error", "Chyba při generování PDF."),
  });

  const sendMailMutation = useMutation({
    mutationFn: () => ordersApi.sendMail(orderId),
    onSuccess: () => { invalidateOrder(); addToast("success", "Email odeslán."); },
    onError: () => addToast("error", "Chyba při odesílání emailu."),
  });

  const handleDownloadPdf = async () => {
    try {
      const response = await ordersApi.downloadPdf(orderId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `protokol_${order?.order_number || orderId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      addToast("error", "Chyba při stahování PDF.");
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      addToast("info", `Zkopírováno: ${text}`);
    } catch { /* silent */ }
  };

  if (isLoading) return <div className="page-loading">Načítání...</div>;
  if (!order) return <div className="page-error">Zakázka nenalezena.</div>;

  const isAssembly = order.team_type === "By_assembly_crew";
  const isDelivery = order.team_type === "By_delivery_crew";
  const isCustomer = order.team_type === "By_customer";
  const teamMismatch = order.pdf && order.team_detail && order.pdf.team !== order.team_detail.name;
  const teamInactive = order.team_detail && !order.team_detail.active;
  const emailNotSent = order.status === "Adviced" && isAssembly && !order.mail_datum_sended;
  const canSendMail = order.has_pdf && order.team_detail?.active && !teamMismatch;

  return (
    <div className="order-detail-page">
      {/* Header */}
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">
            Zakázka {order.order_number}
            <button className="btn-icon-inline" onClick={() => copyToClipboard(order.order_number)} title="Kopírovat">
              <Copy size={14} />
            </button>
          </h1>
          <span className={`badge badge--lg badge--${order.status.toLowerCase()}`}>
            {STATUS_LABELS[order.status]}
          </span>
        </div>
        <div className="page-header__actions">
          <Link to={`/orders/${orderId}/edit`} className="btn btn--primary">
            <Edit size={16} /> Upravit
          </Link>
          <Link to={`/orders/${orderId}/finance`} className="btn btn--secondary">
            <DollarSign size={16} /> Finance
          </Link>
          <Link to={`/orders/${orderId}/history`} className="btn btn--ghost">
            <History size={16} /> Historie
          </Link>
        </div>
      </div>

      {/* Varování */}
      {teamMismatch && (
        <div className="alert alert--warning">
          <AlertTriangle size={18} /> Tým na PDF ({order.pdf?.team}) neodpovídá aktuálnímu týmu ({order.team_detail?.name}).
          Před odesláním emailu vygenerujte nový PDF.
        </div>
      )}
      {teamInactive && (
        <div className="alert alert--warning">
          <AlertTriangle size={18} /> Tým <strong>{order.team_detail?.name}</strong> je neaktivní.
          <Link to={`/teams/${order.team_detail?.slug}/edit`}> Upravit tým</Link>
        </div>
      )}
      {order.client_detail?.incomplete && (
        <div className="alert alert--warning">
          <AlertTriangle size={18} /> Zákazník má neúplné údaje.
          <Link to={`/clients/${order.client_detail.slug}/edit`}> Doplnit</Link>
        </div>
      )}
      {emailNotSent && (
        <div className="alert alert--warning">
          <AlertTriangle size={18} /> E-mail zákazníkovi nebyl dosud odeslán.
        </div>
      )}

      {/* Status-dependent akce */}
      <div className="action-bar">
        {/* New → Hide */}
        {order.status === "New" && (
          <div className="action-group">
            <label className="confirm-check">
              <input type="checkbox" checked={hideConfirm} onChange={(e) => setHideConfirm(e.target.checked)} />
              Opravdu chci skrýt
            </label>
            <button className="btn btn--danger" onClick={() => hideMutation.mutate()}
              disabled={!hideConfirm || hideMutation.isPending}>
              <EyeOff size={16} /> Skrýt zakázku
            </button>
          </div>
        )}

        {/* New + BY_CUSTOMER → přepnout na montáž */}
        {order.status === "New" && isCustomer && (
          <button className="btn btn--secondary" onClick={() => switchToAssemblyMutation.mutate()}
            disabled={switchToAssemblyMutation.isPending}>
            <ArrowRightCircle size={16} /> Přepnout na montáž
          </button>
        )}

        {/* Adviced + Delivery → Realize */}
        {order.status === "Adviced" && isDelivery && (
          <div className="action-group">
            <label className="confirm-check">
              <input type="checkbox" checked={realizeConfirm} onChange={(e) => setRealizeConfirm(e.target.checked)} />
              Potvrdit realizaci
            </label>
            <button className="btn btn--success" onClick={() => realizeMutation.mutate()}
              disabled={!realizeConfirm || realizeMutation.isPending}>
              <CheckCircle size={16} /> Na Realizováno
            </button>
          </div>
        )}

        {/* Hidden → Delete */}
        {order.status === "Hidden" && (
          <div className="action-group">
            <label className="confirm-check">
              <input type="checkbox" checked={deleteConfirm} onChange={(e) => setDeleteConfirm(e.target.checked)} />
              Opravdu smazat
            </label>
            <button className="btn btn--danger" onClick={() => deleteMutation.mutate()}
              disabled={!deleteConfirm || deleteMutation.isPending}>
              <Trash2 size={16} /> Smazat zakázku
            </button>
          </div>
        )}
      </div>

      {/* Info grid */}
      <div className="detail-grid">
        {/* Základní info */}
        <div className="detail-card">
          <h3 className="detail-card__title">Základní informace</h3>
          <dl className="detail-list">
            <dt>Mandant</dt>
            <dd>{order.mandant}</dd>
            <dt>Místo určení</dt>
            <dd>{order.distrib_hub_label}</dd>
            <dt>Typ realizace</dt>
            <dd>{order.team_type_display}</dd>
            <dt>Termín evidence</dt>
            <dd>{order.evidence_termin}</dd>
            <dt>Termín doručení</dt>
            <dd>{order.delivery_termin || <span className="text-muted">Nevybráno</span>}</dd>
            <dt>Termín montáže</dt>
            <dd>
              {order.montage_termin
                ? new Date(order.montage_termin).toLocaleString("cs-CZ")
                : <span className="text-muted">Nevybráno</span>}
            </dd>
          </dl>
        </div>

        {/* Zákazník */}
        <div className="detail-card">
          <h3 className="detail-card__title">Zákazník</h3>
          {order.client_detail ? (
            <>
              <dl className="detail-list">
                <dt>Jméno</dt>
                <dd>
                  <Link to={`/clients/${order.client_detail.slug}`}>
                    {order.client_detail.name}
                  </Link>
                  {order.client_detail.incomplete && (
                    <span className="badge badge--red badge--sm">Neúplný</span>
                  )}
                </dd>
                <dt>Adresa</dt>
                <dd>
                  {order.client_detail.street}, {order.client_detail.city}{" "}
                  {order.client_detail.formatted_psc}
                </dd>
                <dt>Telefon</dt>
                <dd>{order.client_detail.formatted_phone || <span className="text-muted">—</span>}</dd>
                <dt>Email</dt>
                <dd>{order.client_detail.email || <span className="text-muted">—</span>}</dd>
              </dl>
              <div className="detail-card__actions">
                <Link to={`/clients/${order.client_detail.slug}/edit`} className="btn btn--ghost btn--sm">
                  <Edit size={14} /> Upravit zákazníka
                </Link>
                <Link to={`/clients/${order.client_detail.slug}`} className="btn btn--ghost btn--sm">
                  <ExternalLink size={14} /> Objednávky zákazníka
                </Link>
              </div>
            </>
          ) : (
            <p className="text-muted">Zákazník nepřiřazen.</p>
          )}
        </div>

        {/* Tým */}
        <div className="detail-card">
          <h3 className="detail-card__title">Montážní tým</h3>
          {order.team_detail ? (
            <dl className="detail-list">
              <dt>Název</dt>
              <dd>
                <Link to={`/teams/${order.team_detail.slug}`}
                  className={!order.team_detail.active ? "link--inactive" : ""}>
                  {order.team_detail.name}
                </Link>
                <span className={`badge badge--sm ${order.team_detail.active ? "badge--green" : "badge--gray"}`}>
                  {order.team_detail.active ? "Aktivní" : "Neaktivní"}
                </span>
              </dd>
              <dt>Město</dt>
              <dd>{order.team_detail.city}</dd>
              <dt>Telefon</dt>
              <dd>{order.team_detail.phone || "—"}</dd>
              <dt>Email</dt>
              <dd>{order.team_detail.email || "—"}</dd>
            </dl>
          ) : (
            <p className="text-muted">
              {isDelivery ? "Realizace dopravcem — bez týmu." : "Tým nepřiřazen."}
            </p>
          )}
        </div>

        {/* Finance */}
        <div className="detail-card">
          <h3 className="detail-card__title">
            Finance
            <Link to={`/orders/${orderId}/finance`} className="btn btn--ghost btn--sm" style={{ marginLeft: "auto" }}>
              <DollarSign size={14} /> Detail
            </Link>
          </h3>
          <dl className="detail-list">
            <dt>Výnos</dt>
            <dd>{order.vynos ? `${Number(order.vynos).toLocaleString("cs-CZ")} Kč` : <span className="text-muted">—</span>}</dd>
            <dt>Náklad</dt>
            <dd>{order.naklad ? `${Number(order.naklad).toLocaleString("cs-CZ")} Kč` : <span className="text-muted">—</span>}</dd>
            <dt>Profit</dt>
            <dd className={Number(order.profit) >= 0 ? "text-success" : "text-danger"}>
              {Number(order.profit).toLocaleString("cs-CZ")} Kč
            </dd>
          </dl>
        </div>
      </div>

      {/* Artikly */}
      {order.articles.length > 0 && (
        <div className="detail-card detail-card--full">
          <h3 className="detail-card__title">Artikly ({order.articles.length})</h3>
          <table className="data-table data-table--sm">
            <thead>
              <tr>
                <th>Název</th>
                <th>Množství</th>
                <th>Poznámka</th>
              </tr>
            </thead>
            <tbody>
              {order.articles.map((article) => (
                <tr key={article.id}>
                  <td>{article.name}</td>
                  <td>{article.quantity}</td>
                  <td>{article.note || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Protokol a komunikace */}
      <div className="detail-card detail-card--full">
        <h3 className="detail-card__title">Protokol a komunikace</h3>
        <div className="action-buttons">
          {isAssembly && (
            <Link to={`/orders/${orderId}/protocol`} className="btn btn--primary">
              <FileText size={16} /> Montážní protokol
            </Link>
          )}
          <button className="btn btn--secondary"
            onClick={() => generatePdfMutation.mutate()}
            disabled={generatePdfMutation.isPending || !!teamInactive}>
            <FileText size={16} /> Generovat PDF
          </button>
          {order.has_pdf && (
            <button className="btn btn--ghost" onClick={handleDownloadPdf}>
              <FileText size={16} /> Stáhnout PDF
            </button>
          )}
          {order.has_pdf && (
            <Link to={`/orders/${orderId}/pdf`} className="btn btn--ghost">
              <FileText size={16} /> Zobrazit PDF
            </Link>
          )}
          {order.team_detail && (
            <button className="btn btn--success"
              onClick={() => sendMailMutation.mutate()}
              disabled={sendMailMutation.isPending || !canSendMail}>
              <Mail size={16} /> Poslat email
            </button>
          )}
        </div>
        {order.mail_datum_sended && (
          <p className="text-muted" style={{ marginTop: "0.5rem" }}>
            Email odeslán: {new Date(order.mail_datum_sended).toLocaleString("cs-CZ")}{" "}
            (tým: <strong>{order.mail_team_sended}</strong>)
            {order.team_detail && order.mail_team_sended !== order.team_detail.name && (
              <span className="text-danger"> — nesoulad s aktuálním týmem!</span>
            )}
          </p>
        )}
      </div>

      {/* Poznámky */}
      {order.notes && (
        <div className="detail-card detail-card--full">
          <h3 className="detail-card__title">Poznámky</h3>
          <p style={{ whiteSpace: "pre-wrap" }}>{order.notes}</p>
        </div>
      )}

      {/* Přijatý protokol */}
      {order.back_protocol && (
        <div className="detail-card detail-card--full">
          <h3 className="detail-card__title">Přijatý protokol</h3>
          <div className="image-grid">
            <a href={order.back_protocol.file} target="_blank" rel="noopener noreferrer" className="image-grid__item">
              <img src={order.back_protocol.file} alt={order.back_protocol.alt_text || "Protokol"} />
            </a>
          </div>
          <p className="text-muted">
            Nahráno: {new Date(order.back_protocol.created).toLocaleString("cs-CZ")}
          </p>
        </div>
      )}

      {/* Montážní fotky */}
      {order.montage_images.length > 0 && (
        <div className="detail-card detail-card--full">
          <h3 className="detail-card__title">
            Fotky z montáže ({order.montage_images.length})
            <Link to={`/orders/${orderId}/assembly-docs`} className="btn btn--ghost btn--sm" style={{ marginLeft: "auto" }}>
              Kompletní dokumentace →
            </Link>
          </h3>
          <div className="image-grid">
            {order.montage_images.map((img) => (
              <a key={img.id} href={img.image} target="_blank" rel="noopener noreferrer" className="image-grid__item">
                <img src={img.image} alt={img.alt_text || "Montážní foto"} />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
