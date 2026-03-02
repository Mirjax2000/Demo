/**
 * Protokol stránka — generování PDF, preview, email, přijatý protokol, interní upload.
 */
import { useState, useRef } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ordersApi } from "../../api";
import { useToast } from "../../components/Toast";
import {
  ArrowLeft,
  FileText,
  Mail,
  AlertTriangle,
  CheckCircle,
  Image,
  Eye,
  Upload,
  Trash2,
  Download,
} from "lucide-react";

export default function ProtocolPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const orderId = Number(id);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const montageInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedMontageFiles, setSelectedMontageFiles] = useState<File[]>([]);

  const { data: order, isLoading } = useQuery({
    queryKey: ["order", orderId],
    queryFn: () => ordersApi.detail(orderId),
    select: (res) => res.data,
    enabled: !!orderId,
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["order", orderId] });
  };

  const generatePdf = useMutation({
    mutationFn: () => ordersApi.generatePdf(orderId),
    onSuccess: () => { invalidate(); addToast("success", "PDF protokol vygenerován."); },
    onError: () => addToast("error", "Chyba při generování PDF."),
  });

  const sendMail = useMutation({
    mutationFn: () => ordersApi.sendMail(orderId),
    onSuccess: () => { invalidate(); addToast("success", "Email s protokolem odeslán."); },
    onError: () => addToast("error", "Chyba při odesílání emailu."),
  });

  const uploadBackProtocol = useMutation({
    mutationFn: (file: File) => {
      const fd = new FormData();
      fd.append("image", file);
      return ordersApi.uploadBackProtocol(orderId, fd);
    },
    onSuccess: () => {
      invalidate();
      setSelectedFile(null);
      addToast("success", "Zpětný protokol nahrán.");
    },
    onError: () => addToast("error", "Chyba při nahrávání zpětného protokolu."),
  });

  const uploadMontageImage = useMutation({
    mutationFn: async (files: File[]) => {
      for (const file of files) {
        const fd = new FormData();
        fd.append("image", file);
        await ordersApi.uploadImage(orderId, fd);
      }
    },
    onSuccess: () => {
      invalidate();
      setSelectedMontageFiles([]);
      addToast("success", "Montážní fotky nahrány.");
    },
    onError: () => addToast("error", "Chyba při nahrávání montážních fotek."),
  });

  const deleteMontageImage = useMutation({
    mutationFn: (imageId: number) => ordersApi.deleteImage(orderId, imageId),
    onSuccess: () => { invalidate(); addToast("success", "Fotka smazána."); },
    onError: () => addToast("error", "Chyba při mazání fotky."),
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

  const handleDownloadMontageZip = async () => {
    try {
      const response = await ordersApi.downloadMontageZip(orderId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `fotky_${order?.order_number || orderId}.zip`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      addToast("error", "Chyba při stahování ZIP.");
    }
  };

  if (isLoading) return <div className="page-loading">Načítání...</div>;
  if (!order) return <div className="page-error">Zakázka nenalezena.</div>;

  const teamMismatch = order.pdf && order.team_detail && order.pdf.team !== order.team_detail.name;
  const teamInactive = order.team_detail && !order.team_detail.active;
  const canGenerate = order.team_detail?.active;
  const canSendMail = order.has_pdf && order.team_detail?.active && !teamMismatch;

  return (
    <div className="protocol-page">
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">Montážní protokol — {order.order_number}</h1>
        </div>
        <div className="page-header__actions">
          <Link to={`/orders/${orderId}`} className="btn btn--secondary">Zpět na detail</Link>
        </div>
      </div>

      {/* Varování */}
      {teamMismatch && (
        <div className="alert alert--warning">
          <AlertTriangle size={18} /> Tým na PDF (<strong>{order.pdf?.team}</strong>) neodpovídá
          aktuálnímu týmu (<strong>{order.team_detail?.name}</strong>). Vygenerujte nový PDF.
        </div>
      )}
      {teamInactive && (
        <div className="alert alert--danger">
          <AlertTriangle size={18} /> Tým <strong>{order.team_detail?.name}</strong> je neaktivní.
          <Link to={`/teams/${order.team_detail?.slug}/edit`}> Upravit tým</Link>
        </div>
      )}
      {!order.team_detail && (
        <div className="alert alert--warning">
          <AlertTriangle size={18} /> Zakázka nemá přiřazený tým.
        </div>
      )}

      {/* Akční tlačítka */}
      <div className="detail-card">
        <h3 className="detail-card__title">Akce</h3>
        <div className="action-buttons">
          <button className="btn btn--primary" onClick={() => generatePdf.mutate()}
            disabled={generatePdf.isPending || !canGenerate}>
            <FileText size={16} /> Generuj protokol
          </button>
          {order.has_pdf && (
            <button className="btn btn--secondary" onClick={handleDownloadPdf}>
              <Eye size={16} /> Zkontroluj protokol
            </button>
          )}
          <button className="btn btn--success" onClick={() => sendMail.mutate()}
            disabled={sendMail.isPending || !canSendMail}>
            <Mail size={16} /> Odeslat email
          </button>
        </div>
      </div>

      {/* Email info */}
      {order.mail_datum_sended && (
        <div className="detail-card">
          <h3 className="detail-card__title">Odeslaný email</h3>
          <dl className="detail-list">
            <dt>Datum odeslání</dt>
            <dd>{new Date(order.mail_datum_sended).toLocaleString("cs-CZ")}</dd>
            <dt>Tým</dt>
            <dd>
              {order.mail_team_sended}
              {order.team_detail && order.mail_team_sended !== order.team_detail.name && (
                <span className="text-danger"> — nesoulad!</span>
              )}
            </dd>
          </dl>
        </div>
      )}

      {/* PDF info */}
      {order.pdf && (
        <div className="detail-card">
          <h3 className="detail-card__title">PDF Protokol</h3>
          <dl className="detail-list">
            <dt>Tým na PDF</dt>
            <dd>{order.pdf.team}</dd>
            <dt>Vytvořen</dt>
            <dd>{new Date(order.pdf.created).toLocaleString("cs-CZ")}</dd>
          </dl>
        </div>
      )}

      {/* Interní upload zpětného protokolu */}
      <div className="detail-card">
        <h3 className="detail-card__title">
          <Upload size={16} /> Nahrát zpětný protokol
        </h3>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          />
          <button
            className="btn btn--secondary"
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={16} /> {selectedFile ? selectedFile.name : "Vybrat soubor"}
          </button>
          {selectedFile && (
            <button
              className="btn btn--primary"
              onClick={() => uploadBackProtocol.mutate(selectedFile)}
              disabled={uploadBackProtocol.isPending}
            >
              {uploadBackProtocol.isPending ? "Nahrávám..." : "Nahrát"}
            </button>
          )}
        </div>
      </div>

      {/* Přijatý protokol */}
      {order.back_protocol && (
        <div className="detail-card detail-card--full">
          <h3 className="detail-card__title">
            <CheckCircle size={16} className="icon--success" /> Přijatý zpětný protokol
          </h3>
          <div className="image-grid">
            <a href={order.back_protocol.file} target="_blank" rel="noopener noreferrer"
              className="image-grid__item">
              <img src={order.back_protocol.file} alt={order.back_protocol.alt_text || "Protokol"} />
            </a>
          </div>
          <p className="text-muted">
            Nahráno: {new Date(order.back_protocol.created).toLocaleString("cs-CZ")}
          </p>
        </div>
      )}

      {/* Montážní fotky — upload + galerie */}
      <div className="detail-card detail-card--full">
        <h3 className="detail-card__title">
          <Image size={16} /> Fotky z montáže ({order.montage_images.length})
        </h3>

        {/* Upload formulář + ZIP download */}
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap", marginBottom: "0.75rem" }}>
          <input
            ref={montageInputRef}
            type="file"
            accept="image/*"
            multiple
            style={{ display: "none" }}
            onChange={(e) => setSelectedMontageFiles(Array.from(e.target.files || []))}
          />
          <button className="btn btn--secondary" onClick={() => montageInputRef.current?.click()}>
            <Upload size={16} /> {selectedMontageFiles.length > 0
              ? `Vybráno ${selectedMontageFiles.length} soubor(ů)`
              : "Vybrat fotky"}
          </button>
          {selectedMontageFiles.length > 0 && (
            <button
              className="btn btn--primary"
              onClick={() => uploadMontageImage.mutate(selectedMontageFiles)}
              disabled={uploadMontageImage.isPending}
            >
              {uploadMontageImage.isPending ? "Nahrávám..." : "Nahrát"}
            </button>
          )}
          {order.montage_images.length > 0 && (
            <button className="btn btn--secondary" onClick={handleDownloadMontageZip}>
              <Download size={16} /> Stáhnout ZIP
            </button>
          )}
        </div>

        {/* Galerie */}
        {order.montage_images.length > 0 && (
          <div className="image-grid">
            {order.montage_images.map((img) => (
              <div key={img.id} className="image-grid__item" style={{ position: "relative" }}>
                <a href={img.image} target="_blank" rel="noopener noreferrer">
                  <img src={img.image} alt={img.alt_text || "Montážní foto"} />
                </a>
                <button
                  className="btn-icon-inline image-grid__delete"
                  onClick={() => deleteMontageImage.mutate(img.id)}
                  title="Smazat fotku"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
