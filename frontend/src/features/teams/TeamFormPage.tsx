/**
 * Formulář pro vytvoření / úpravu týmu.
 */
import { useState, useEffect } from "react";
import type { FormEvent } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { teamsApi } from "../../api";
import { useToast } from "../../components/Toast";
import { ArrowLeft, Save, Trash2 } from "lucide-react";

interface TeamForm {
  name: string;
  city: string;
  region: string;
  phone: string;
  email: string;
  active: boolean;
  price_per_hour: string;
  price_per_km: string;
  notes: string;
}

const emptyForm: TeamForm = {
  name: "",
  city: "",
  region: "",
  phone: "",
  email: "",
  active: true,
  price_per_hour: "",
  price_per_km: "",
  notes: "",
};

export default function TeamFormPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const isEdit = !!slug;

  const [form, setForm] = useState<TeamForm>(emptyForm);
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [deleteConfirm, setDeleteConfirm] = useState(false);

  // Fetch existing team for edit
  const { data: existing } = useQuery({
    queryKey: ["team", slug],
    queryFn: () => teamsApi.detail(slug!),
    select: (res) => res.data,
    enabled: isEdit,
  });

  useEffect(() => {
    if (existing) {
      setForm({
        name: existing.name || "",
        city: existing.city || "",
        region: existing.region || "",
        phone: existing.phone || "",
        email: existing.email || "",
        active: existing.active ?? true,
        price_per_hour: existing.price_per_hour?.toString() || "",
        price_per_km: existing.price_per_km?.toString() || "",
        notes: existing.notes || "",
      });
    }
  }, [existing]);

  const set = (field: keyof TeamForm, value: string | boolean) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const saveMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      isEdit ? teamsApi.update(slug!, data) : teamsApi.create(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["teams"] });
      addToast("success", isEdit ? "Tým upraven." : "Tým vytvořen.");
      navigate(`/teams/${res.data.slug}`);
    },
    onError: (err: any) => {
      if (err.response?.data) setErrors(err.response.data);
      addToast("error", "Chyba při ukládání týmu.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => teamsApi.delete(slug!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams"] });
      addToast("success", "Tým smazán.");
      navigate("/teams");
    },
    onError: () => addToast("error", "Chyba při mazání. Pouze neaktivní týmy lze smazat."),
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setErrors({});
    const payload: Record<string, unknown> = {
      name: form.name,
      city: form.city,
      region: form.region,
      phone: form.phone,
      email: form.email,
      active: form.active,
      notes: form.notes,
    };
    if (form.price_per_hour) payload.price_per_hour = form.price_per_hour;
    if (form.price_per_km) payload.price_per_km = form.price_per_km;

    saveMutation.mutate(payload);
  };

  const canDelete = isEdit && existing && !existing.active;

  return (
    <div className="team-form-page">
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">{isEdit ? `Upravit tým — ${existing?.name ?? ""}` : "Nový tým"}</h1>
        </div>
      </div>

      <form className="form-card" onSubmit={handleSubmit}>
        {/* Name */}
        <div className="form-group">
          <label className="form-label">Název týmu *</label>
          <input className={`input ${errors.name ? "input--error" : ""}`}
            value={form.name} onChange={(e) => set("name", e.target.value)}
            disabled={isEdit} required />
          {errors.name && <span className="form-error">{errors.name.join(", ")}</span>}
          {isEdit && <span className="form-hint">Název nelze měnit.</span>}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Město</label>
            <input className="input" value={form.city} onChange={(e) => set("city", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Region</label>
            <input className="input" value={form.region} onChange={(e) => set("region", e.target.value)} />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Telefon</label>
            <input className="input" value={form.phone} onChange={(e) => set("phone", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input type="email" className="input" value={form.email}
              onChange={(e) => set("email", e.target.value)} />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Cena za hodinu (Kč)</label>
            <input type="number" step="0.01" className="input"
              value={form.price_per_hour} onChange={(e) => set("price_per_hour", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Cena za km (Kč)</label>
            <input type="number" step="0.01" className="input"
              value={form.price_per_km} onChange={(e) => set("price_per_km", e.target.value)} />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Poznámky</label>
          <textarea className="input" rows={3} value={form.notes}
            onChange={(e) => set("notes", e.target.value)} />
        </div>

        <div className="form-group form-group--checkbox">
          <label>
            <input type="checkbox" checked={form.active}
              onChange={(e) => set("active", e.target.checked)} />
            <span>Aktivní</span>
          </label>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn--primary" disabled={saveMutation.isPending}>
            <Save size={16} /> {isEdit ? "Uložit změny" : "Vytvořit tým"}
          </button>

          {canDelete && (
            <div className="form-group--inline">
              <label className="checkbox-confirm">
                <input type="checkbox" checked={deleteConfirm}
                  onChange={(e) => setDeleteConfirm(e.target.checked)} />
                Potvrdit smazání
              </label>
              <button type="button" className="btn btn--danger" disabled={!deleteConfirm || deleteMutation.isPending}
                onClick={() => deleteMutation.mutate()}>
                <Trash2 size={16} /> Smazat tým
              </button>
            </div>
          )}
        </div>
      </form>
    </div>
  );
}
