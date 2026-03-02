/**
 * Formulář pro vytvoření / úpravu zakázky.
 * Obsahuje inline klient formulář, Adviced validaci, auto-uppercase.
 */
import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ordersApi, teamsApi, clientsApi, distribHubsApi } from "../../api";
import type { OrderWrite, OrderStatus, DistribHub, Team, Client, TeamType } from "../../types";
import { useToast } from "../../components/Toast";
import SearchableSelect from "../../components/SearchableSelect";
import type { SelectOption } from "../../components/SearchableSelect";
import { ArrowLeft, Plus, Trash2, Save, AlertTriangle } from "lucide-react";

const STATUS_OPTIONS = [
  { value: "New", label: "Nový" },
  { value: "Adviced", label: "Zatermínováno" },
  { value: "Realized", label: "Realizováno" },
  { value: "Billed", label: "Vyúčtováno" },
  { value: "Canceled", label: "Zrušeno" },
  { value: "Hidden", label: "Skryto" },
];

const MANDANT_OPTIONS = ["Rhenus", "SMS", "Zlatohor", "Ikea"];
const TEAM_TYPE_OPTIONS = [
  { value: "By_assembly_crew", label: "Montážníky" },
  { value: "By_delivery_crew", label: "Dopravcem" },
  { value: "By_customer", label: "Zákazníkem" },
];

interface ArticleInput {
  id?: number;
  name: string;
  quantity: number;
  note: string;
  _delete?: boolean;
}

interface ClientInput {
  name: string;
  street: string;
  city: string;
  zip_code: string;
  phone: string;
  email: string;
}

const emptyArticle = (): ArticleInput => ({ name: "", quantity: 1, note: "" });
const emptyClient = (): ClientInput => ({ name: "", street: "", city: "", zip_code: "", phone: "", email: "" });

const blankOrder = {
  order_number: "",
  mandant: "Rhenus",
  status: "New" as OrderStatus,
  team_type: "By_assembly_crew" as TeamType,
  distrib_hub: null as unknown as number,
  team: null as number | null,
  client: null as number | null,
  evidence_termin: "",
  delivery_termin: "",
  montage_termin: "",
  vynos: "",
  naklad: "",
  notes: "",
};

export default function OrderFormPage() {
  const { id } = useParams<{ id: string }>();
  const isEdit = !!id;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const [form, setForm] = useState(blankOrder);
  const [articles, setArticles] = useState<ArticleInput[]>([emptyArticle()]);
  const [clientMode, setClientMode] = useState<"existing" | "new">("existing");
  const [clientForm, setClientForm] = useState<ClientInput>(emptyClient());
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Lookup data
  const { data: hubs } = useQuery({
    queryKey: ["distrib-hubs"],
    queryFn: () => distribHubsApi.list(),
    select: (res) => res.data as DistribHub[],
  });

  const { data: teams } = useQuery({
    queryKey: ["teams-all"],
    queryFn: () => teamsApi.list({ page_size: "50" }),
    select: (res) => {
      const d = res.data;
      return (d?.results ?? (Array.isArray(d) ? d : [])) as Team[];
    },
  });

  const { data: clients } = useQuery({
    queryKey: ["clients-all"],
    queryFn: () => clientsApi.list({ page_size: "50" }),
    select: (res) => {
      const d = res.data;
      return (d?.results ?? (Array.isArray(d) ? d : [])) as Client[];
    },
  });

  // Server-side search callbacks for SearchableSelect
  const fetchTeamOptions = useCallback(
    async (search: string): Promise<SelectOption[]> => {
      const res = await teamsApi.list({ search, page_size: "50" });
      const d = res.data;
      const list = (d?.results ?? (Array.isArray(d) ? d : [])) as Team[];
      return list.filter((t) => t.active).map((t) => ({ value: t.id, label: t.name }));
    },
    [],
  );

  const fetchClientOptions = useCallback(
    async (search: string): Promise<SelectOption[]> => {
      const res = await clientsApi.list({ search, page_size: "50" });
      const d = res.data;
      const list = (d?.results ?? (Array.isArray(d) ? d : [])) as Client[];
      return list.map((c) => ({ value: c.id, label: `${c.name} (${c.zip_code})` }));
    },
    [],
  );

  const teamInitialOptions: SelectOption[] =
    teams?.filter((t) => t.active).map((t) => ({ value: t.id, label: t.name })) ?? [];

  const clientInitialOptions: SelectOption[] =
    clients?.map((c) => ({ value: c.id, label: `${c.name} (${c.zip_code})` })) ?? [];

  // Load existing order
  const { data: existingOrder } = useQuery({
    queryKey: ["order", Number(id)],
    queryFn: () => ordersApi.detail(Number(id)),
    select: (res) => res.data,
    enabled: isEdit,
  });

  useEffect(() => {
    if (existingOrder) {
      setForm({
        order_number: existingOrder.order_number,
        mandant: existingOrder.mandant,
        status: existingOrder.status,
        team_type: existingOrder.team_type || "By_assembly_crew",
        distrib_hub: existingOrder.distrib_hub,
        team: existingOrder.team,
        client: existingOrder.client,
        evidence_termin: existingOrder.evidence_termin || "",
        delivery_termin: existingOrder.delivery_termin || "",
        montage_termin: existingOrder.montage_termin?.slice(0, 16) || "",
        vynos: existingOrder.vynos || "",
        naklad: existingOrder.naklad || "",
        notes: existingOrder.notes || "",
      });
      setArticles(
        existingOrder.articles?.length
          ? existingOrder.articles.map((a) => ({
              id: a.id, name: a.name, quantity: a.quantity, note: a.note || "",
            }))
          : []
      );
      setClientMode("existing");
    }
  }, [existingOrder]);

  // Adviced validation
  const validateAdviced = (): Record<string, string> => {
    const errs: Record<string, string> = {};
    if (form.status !== "Adviced") return errs;

    const tt = form.team_type;
    if (tt === "By_customer") {
      errs.status = "Zakázka s typem 'Zákazníkem' nemůže být zatermínována.";
      return errs;
    }
    if (tt === "By_assembly_crew") {
      if (!form.client) {
        errs.client = "Vyžadován zákazník.";
      } else {
        const sel = clients?.find((c) => c.id === Number(form.client));
        if (sel?.incomplete) errs.client = "Zákazník má neúplné údaje, nelze zatermínovat.";
      }
      if (!form.team) errs.team = "Vyžadován tým.";
      if (!form.montage_termin) errs.montage_termin = "Vyžadován termín montáže.";
      if (!form.delivery_termin) errs.delivery_termin = "Vyžadován termín doručení.";
      if (!form.vynos) errs.vynos = "Vyžadován výnos.";
      if (!form.naklad) errs.naklad = "Vyžadován náklad.";
    }
    if (tt === "By_delivery_crew") {
      if (!form.client) {
        errs.client = "Vyžadován zákazník.";
      } else {
        const sel = clients?.find((c) => c.id === Number(form.client));
        if (sel?.incomplete) errs.client = "Zákazník má neúplné údaje, nelze zatermínovat.";
      }
      if (!form.delivery_termin) errs.delivery_termin = "Vyžadován termín doručení.";
      if (!form.vynos) errs.vynos = "Vyžadován výnos.";
      if (!form.naklad) errs.naklad = "Vyžadován náklad.";
      if (form.team) errs.team = "Dopravní zakázka nesmí mít přiřazený tým.";
      if (form.montage_termin) errs.montage_termin = "Dopravní zakázka nesmí mít termín montáže.";
    }
    return errs;
  };

  const mutation = useMutation({
    mutationFn: (payload: OrderWrite) =>
      isEdit ? ordersApi.update(Number(id), payload) : ordersApi.create(payload),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      addToast("success", isEdit ? "Zakázka aktualizována." : "Zakázka vytvořena.");
      const newId = res.data?.id ?? id;
      navigate(`/orders/${newId}`);
    },
    onError: (err: any) => {
      const detail = err?.response?.data;
      if (detail && typeof detail === "object") {
        const fieldErrors: Record<string, string> = {};
        for (const [key, val] of Object.entries(detail)) {
          fieldErrors[key] = Array.isArray(val) ? val.join(", ") : String(val);
        }
        setErrors(fieldErrors);
      }
      addToast("error", "Chyba při ukládání zakázky.");
    },
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === "order_number" ? value.toUpperCase() : value,
    }));
    setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const handleClientChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setClientForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleArticleChange = (idx: number, field: keyof ArticleInput, value: string | number) => {
    setArticles((prev) => prev.map((a, i) => (i === idx ? { ...a, [field]: value } : a)));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const advicedErrors = validateAdviced();
    if (Object.keys(advicedErrors).length > 0) {
      setErrors(advicedErrors);
      addToast("warning", "Formulář obsahuje chyby.");
      return;
    }
    const payload = {
      ...form,
      distrib_hub: form.distrib_hub || null,
      team: form.team || null,
      client: form.client || null,
      articles: articles.filter((a) => a.name.trim() && !a._delete),
      ...(clientMode === "new" && clientForm.name.trim() ? { client_data: clientForm } : {}),
    } as OrderWrite;
    mutation.mutate(payload);
  };

  const showTeamField = form.team_type === "By_assembly_crew";
  const showMontageTermin = form.team_type !== "By_delivery_crew";

  return (
    <div className="order-form-page">
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">
            {isEdit ? `Upravit zakázku ${form.order_number}` : "Nová zakázka"}
          </h1>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="form-grid">
        {/* Základní */}
        <fieldset className="form-section">
          <legend>Základní údaje</legend>
          <div className="form-row">
            <label className="form-label">
              Číslo zakázky *
              <input
                name="order_number"
                className={`input ${errors.order_number ? "input--error" : ""}`}
                value={form.order_number}
                onChange={handleChange}
                required
                disabled={isEdit}
                style={{ textTransform: "uppercase" }}
              />
              {errors.order_number && <span className="form-error">{errors.order_number}</span>}
            </label>
            <label className="form-label">
              Mandant
              <select name="mandant" className="input" value={form.mandant} onChange={handleChange}>
                {MANDANT_OPTIONS.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </label>
            <label className="form-label">
              Status
              <select name="status" className={`input ${errors.status ? "input--error" : ""}`}
                value={form.status} onChange={handleChange}>
                {STATUS_OPTIONS.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
              {errors.status && <span className="form-error">{errors.status}</span>}
            </label>
          </div>
          <div className="form-row">
            <label className="form-label">
              Typ realizace
              <select name="team_type" className="input" value={form.team_type} onChange={handleChange}>
                {TEAM_TYPE_OPTIONS.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </label>
            <label className="form-label">
              Distribuční hub
              <select name="distrib_hub" className="input"
                value={form.distrib_hub ?? ""} onChange={handleChange}>
                <option value="">— Vyberte —</option>
                {hubs?.map((h) => (
                  <option key={h.id} value={h.id}>{h.label}</option>
                ))}
              </select>
            </label>
          </div>
        </fieldset>

        {/* Přiřazení */}
        <fieldset className="form-section">
          <legend>Přiřazení</legend>
          <div className="form-row">
            {showTeamField && (
              <label className="form-label">
                Tým
                <SearchableSelect
                  name="team"
                  value={form.team}
                  onChange={(v) => setForm((f) => ({ ...f, team: v ? Number(v) : null }))}
                  fetchOptions={fetchTeamOptions}
                  initialOptions={teamInitialOptions}
                  placeholder="Vyberte tým…"
                  className={errors.team ? "input--error" : ""}
                />
                {errors.team && <span className="form-error">{errors.team}</span>}
              </label>
            )}
            <label className="form-label">
              Zákazník
              <div className="input-group">
                <select value={clientMode} onChange={(e) => setClientMode(e.target.value as "existing" | "new")}
                  className="input input--sm" style={{ maxWidth: "120px" }}>
                  <option value="existing">Existující</option>
                  <option value="new">Nový</option>
                </select>
                {clientMode === "existing" ? (
                  <SearchableSelect
                    name="client"
                    value={form.client}
                    onChange={(v) => setForm((f) => ({ ...f, client: v ? Number(v) : null }))}
                    fetchOptions={fetchClientOptions}
                    initialOptions={clientInitialOptions}
                    placeholder="Hledat zákazníka…"
                    className={errors.client ? "input--error" : ""}
                  />
                ) : null}
              </div>
              {errors.client && <span className="form-error">{errors.client}</span>}
            </label>
          </div>
        </fieldset>

        {/* Nový zákazník — inline form */}
        {clientMode === "new" && (
          <fieldset className="form-section form-section--highlight">
            <legend>Nový zákazník</legend>
            <div className="form-row">
              <label className="form-label">
                Jméno *
                <input name="name" className="input" value={clientForm.name}
                  onChange={handleClientChange} required={clientMode === "new"} />
              </label>
              <label className="form-label">
                PSČ *
                <input name="zip_code" className="input" value={clientForm.zip_code}
                  onChange={handleClientChange} maxLength={5} pattern="\d{5}" title="5 číslic" />
              </label>
            </div>
            <div className="form-row">
              <label className="form-label">
                Ulice
                <input name="street" className="input" value={clientForm.street} onChange={handleClientChange} />
              </label>
              <label className="form-label">
                Město
                <input name="city" className="input" value={clientForm.city} onChange={handleClientChange} />
              </label>
            </div>
            <div className="form-row">
              <label className="form-label">
                Telefon
                <input name="phone" className="input" type="tel" value={clientForm.phone} onChange={handleClientChange} />
              </label>
              <label className="form-label">
                Email
                <input name="email" className="input" type="email" value={clientForm.email} onChange={handleClientChange} />
              </label>
            </div>
          </fieldset>
        )}

        {/* Termíny */}
        <fieldset className="form-section">
          <legend>Termíny</legend>
          <div className="form-row">
            <label className="form-label">
              Termín evidence
              <input type="date" name="evidence_termin" className="input"
                value={form.evidence_termin} onChange={handleChange} />
            </label>
            <label className="form-label">
              Termín doručení
              <input type="date" name="delivery_termin"
                className={`input ${errors.delivery_termin ? "input--error" : ""}`}
                value={form.delivery_termin} onChange={handleChange} />
              {errors.delivery_termin && <span className="form-error">{errors.delivery_termin}</span>}
            </label>
            {showMontageTermin && (
              <label className="form-label">
                Termín montáže
                <input type="datetime-local" name="montage_termin"
                  className={`input ${errors.montage_termin ? "input--error" : ""}`}
                  value={form.montage_termin} onChange={handleChange} />
                {errors.montage_termin && <span className="form-error">{errors.montage_termin}</span>}
              </label>
            )}
          </div>
        </fieldset>

        {/* Finance */}
        <fieldset className="form-section">
          <legend>Finance</legend>
          <div className="form-row">
            <label className="form-label">
              Výnos (Kč)
              <input type="number" name="vynos"
                className={`input ${errors.vynos ? "input--error" : ""}`}
                step="1" value={form.vynos} onChange={handleChange} />
              {errors.vynos && <span className="form-error">{errors.vynos}</span>}
            </label>
            <label className="form-label">
              Náklad (Kč)
              <input type="number" name="naklad"
                className={`input ${errors.naklad ? "input--error" : ""}`}
                step="1" value={form.naklad} onChange={handleChange} />
              {errors.naklad && <span className="form-error">{errors.naklad}</span>}
            </label>
          </div>
        </fieldset>

        {/* Poznámky */}
        <fieldset className="form-section">
          <legend>Poznámky</legend>
          <textarea name="notes" className="input input--textarea" rows={4}
            value={form.notes} onChange={handleChange} />
        </fieldset>

        {/* Artikly */}
        <fieldset className="form-section">
          <legend>Artikly</legend>
          {articles.filter((a) => !a._delete).map((art, idx) => (
            <div key={idx} className="form-row form-row--article">
              <input className="input" placeholder="Název artiklu" value={art.name}
                onChange={(e) => handleArticleChange(idx, "name", e.target.value)} />
              <input type="number" className="input input--sm" min={1} max={999} value={art.quantity}
                onChange={(e) => handleArticleChange(idx, "quantity", Number(e.target.value))} />
              <input className="input" placeholder="Poznámka" value={art.note}
                onChange={(e) => handleArticleChange(idx, "note", e.target.value)} />
              <button type="button" className="btn btn--danger btn--icon"
                onClick={() => {
                  if (art.id) {
                    setArticles((p) => p.map((a, i) => i === idx ? { ...a, _delete: true } : a));
                  } else {
                    setArticles((p) => p.filter((_, i) => i !== idx));
                  }
                }}>
                <Trash2 size={16} />
              </button>
            </div>
          ))}
          <button type="button" className="btn btn--ghost"
            onClick={() => setArticles((p) => [...p, emptyArticle()])}>
            <Plus size={16} /> Přidat artikl
          </button>
        </fieldset>

        {/* Submit */}
        {mutation.isError && Object.keys(errors).length > 0 && (
          <div className="alert alert--danger">
            <AlertTriangle size={16} /> Opravte prosím chyby ve formuláři.
          </div>
        )}

        <div className="form-actions">
          <button type="submit" className="btn btn--primary btn--lg" disabled={mutation.isPending}>
            <Save size={16} /> {mutation.isPending ? "Ukládám..." : "Uložit"}
          </button>
          <button type="button" className="btn btn--ghost" onClick={() => navigate(-1)}>
            Zrušit
          </button>
        </div>
      </form>
    </div>
  );
}
