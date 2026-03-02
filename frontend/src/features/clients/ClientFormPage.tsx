/**
 * Formulář pro úpravu klienta + Call Log.
 */
import { useState, useEffect } from "react";
import type { FormEvent } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { clientsApi, callLogsApi } from "../../api";
import type { ClientDetail } from "../../types";
import { useToast } from "../../components/Toast";
import { ArrowLeft, Save, Plus, Phone, Trash2, Check, X } from "lucide-react";

interface ClientForm {
  name: string;
  street: string;
  city: string;
  zip_code: string;
  phone: string;
  email: string;
}

interface CallLogEntry {
  id?: number;
  note: string;
  was_successful: boolean;
  created?: string;
  _isNew?: boolean;
}

export default function ClientFormPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const [form, setForm] = useState<ClientForm>({
    name: "", street: "", city: "", zip_code: "", phone: "", email: "",
  });
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [callLogs, setCallLogs] = useState<CallLogEntry[]>([]);
  const [saving, setSaving] = useState(false);

  // Fetch client
  const { data: client } = useQuery({
    queryKey: ["client", slug],
    queryFn: () => clientsApi.detail(slug!),
    select: (res) => res.data as ClientDetail,
    enabled: !!slug,
  });

  useEffect(() => {
    if (client) {
      setForm({
        name: client.name || "",
        street: client.street || "",
        city: client.city || "",
        zip_code: client.zip_code || "",
        phone: client.phone || "",
        email: client.email || "",
      });
      if (client.call_logs) {
        setCallLogs(client.call_logs.map((c: any) => ({
          id: c.id, note: c.note,
          was_successful: c.was_successful === "Success" || c.was_successful === true,
          created: c.called_at || c.created, _isNew: false,
        })));
      }
    }
  }, [client]);

  const set = (field: keyof ClientForm, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});
    setSaving(true);
    const payload: Record<string, unknown> = {
      street: form.street,
      city: form.city,
      phone: form.phone,
      email: form.email,
    };
    // Save client first, then create new call logs via separate endpoint
    try {
      const res = await clientsApi.update(slug!, payload);
      // Create new call logs via CallLog API
      const newLogs = callLogs.filter((l) => l._isNew);
      for (const log of newLogs) {
        await callLogsApi.create({
          client: client!.id,
          note: log.note,
          was_successful: log.was_successful ? "Success" : "Failed",
        } as Partial<import("../../types").CallLog>);
      }
      queryClient.invalidateQueries({ queryKey: ["client", slug] });
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      addToast("success", "Klient uložen.");
      navigate(`/clients/${res.data.slug}`);
    } catch (err: any) {
      if (err.response?.data) setErrors(err.response.data);
      addToast("error", "Chyba při ukládání klienta.");
    } finally {
      setSaving(false);
    }
  };

  // Call log management
  const addCallLog = () => {
    setCallLogs((prev) => [...prev, { note: "", was_successful: false, _isNew: true }]);
  };

  const updateCallLog = (index: number, field: string, value: string | boolean) => {
    setCallLogs((prev) => prev.map((l, i) => i === index ? { ...l, [field]: value } : l));
  };

  const removeCallLog = (index: number) => {
    setCallLogs((prev) => prev.filter((_, i) => i !== index));
  };

  const deleteExistingCallLog = async (index: number, id: number) => {
    if (!confirm("Opravdu smazat záznam hovoru?")) return;
    try {
      await callLogsApi.delete(id);
      setCallLogs((prev) => prev.filter((_, i) => i !== index));
      addToast("success", "Záznam hovoru smazán.");
    } catch {
      addToast("error", "Chyba při mazání záznamu.");
    }
  };

  return (
    <div className="client-form-page">
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">Upravit klienta — {client?.name ?? "…"}</h1>
        </div>
        <div className="page-header__actions">
          {slug && (
            <Link to={`/clients/${slug}`} className="btn btn--secondary">
              Detail klienta
            </Link>
          )}
        </div>
      </div>

      <form className="form-card" onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Jméno</label>
          <input className="input" value={form.name} disabled />
          <span className="form-hint">Jméno nelze měnit.</span>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Ulice</label>
            <input className="input" value={form.street}
              onChange={(e) => set("street", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Město</label>
            <input className="input" value={form.city}
              onChange={(e) => set("city", e.target.value)} />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">PSČ</label>
            <input className="input" value={form.zip_code} disabled />
            <span className="form-hint">PSČ nelze měnit.</span>
          </div>
          <div className="form-group">
            <label className="form-label">Telefon</label>
            <input className="input" value={form.phone}
              onChange={(e) => set("phone", e.target.value)} />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Email</label>
          <input type="email" className="input" value={form.email}
            onChange={(e) => set("email", e.target.value)} />
        </div>

        {/* Call Log */}
        <div className="form-section">
          <h3 className="form-section__title">
            <Phone size={16} /> Záznamy hovorů ({callLogs.length})
          </h3>

          {callLogs.map((log, idx) => (
            <div key={log.id ?? `new-${idx}`} className="call-log-entry">
              {log._isNew ? (
                <div className="call-log-entry__inner">
                  <input className="input" placeholder="Poznámka k hovoru"
                    value={log.note} onChange={(e) => updateCallLog(idx, "note", e.target.value)} />
                  <label className="checkbox-confirm">
                    <input type="checkbox" checked={log.was_successful}
                      onChange={(e) => updateCallLog(idx, "was_successful", e.target.checked)} />
                    Úspěšný
                  </label>
                  <button type="button" className="btn btn--danger btn--icon btn--sm"
                    onClick={() => removeCallLog(idx)}>
                    <Trash2 size={14} />
                  </button>
                </div>
              ) : (
                <div className="call-log-entry__inner call-log-entry--readonly">
                  <span className="call-log-entry__status">
                    {log.was_successful
                      ? <Check size={14} className="icon--success" />
                      : <X size={14} className="icon--danger" />}
                  </span>
                  <span className="call-log-entry__note">{log.note}</span>
                  <time className="call-log-entry__date">
                    {log.created ? new Date(log.created).toLocaleString("cs-CZ") : ""}
                  </time>
                  <button type="button" className="btn btn--danger btn--icon btn--sm"
                    title="Smazat záznam"
                    onClick={() => deleteExistingCallLog(idx, log.id!)}>
                    <Trash2 size={14} />
                  </button>
                </div>
              )}
            </div>
          ))}

          <button type="button" className="btn btn--ghost btn--sm" onClick={addCallLog}>
            <Plus size={14} /> Přidat záznam hovoru
          </button>
        </div>

        {Object.keys(errors).length > 0 && (
          <div className="alert alert--danger">
            {Object.entries(errors).map(([field, msgs]) => (
              <p key={field}><strong>{field}:</strong> {msgs.join(", ")}</p>
            ))}
          </div>
        )}

        <div className="form-actions">
          <button type="submit" className="btn btn--primary" disabled={saving}>
            <Save size={16} /> Uložit klienta
          </button>
        </div>
      </form>
    </div>
  );
}
