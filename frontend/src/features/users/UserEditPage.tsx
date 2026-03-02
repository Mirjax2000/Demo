/**
 * Admin — úprava uživatele: změna role, aktivace/deaktivace.
 */
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usersApi } from "../../api";
import { useToast } from "../../components/Toast";
import { ArrowLeft, Save, Shield } from "lucide-react";

const ROLE_OPTIONS = [
  { value: "Admin", label: "Admin", desc: "Plný přístup — CRUD + mazání + správa uživatelů" },
  { value: "Manager", label: "Manager", desc: "CRUD bez mazání" },
  { value: "Operator", label: "Operator", desc: "Vytváření a editace" },
  { value: "ReadOnly", label: "ReadOnly", desc: "Pouze čtení" },
];

export default function UserEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const userId = Number(id);

  const [group, setGroup] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");

  const { data: user, isLoading } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => usersApi.detail(userId),
    select: (res) => res.data,
    enabled: !!userId,
  });

  useEffect(() => {
    if (user) {
      setGroup(user.role || "ReadOnly");
      setIsActive(user.is_active !== false);
      setEmail(user.email || "");
      setFirstName(user.first_name || "");
      setLastName(user.last_name || "");
    }
  }, [user]);

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      usersApi.update(userId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      queryClient.invalidateQueries({ queryKey: ["user", userId] });
      addToast("success", "Uživatel aktualizován.");
      navigate("/users");
    },
    onError: () => addToast("error", "Chyba při ukládání."),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      group,
      is_active: isActive,
      email,
      first_name: firstName,
      last_name: lastName,
    });
  };

  if (isLoading) return <div className="page-loading">Načítání...</div>;
  if (!user) return <div className="page-error">Uživatel nenalezen.</div>;

  return (
    <div className="user-edit-page">
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">
            <Shield size={20} /> Upravit uživatele: {user.username}
          </h1>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="form-grid" style={{ maxWidth: 600 }}>
        <fieldset className="form-section">
          <legend>Informace</legend>

          <div className="form-row">
            <label className="form-label">
              Uživatelské jméno
              <input className="input" value={user.username} disabled />
            </label>
          </div>

          <div className="form-row">
            <label className="form-label">
              Jméno
              <input
                className="input"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </label>
          </div>

          <div className="form-row">
            <label className="form-label">
              Příjmení
              <input
                className="input"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </label>
          </div>

          <div className="form-row">
            <label className="form-label">
              Email
              <input
                className="input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Role a přístup</legend>

          <div className="form-row">
            <label className="form-label">
              Role (skupina)
              <select
                className="input"
                value={group}
                onChange={(e) => setGroup(e.target.value)}
              >
                {ROLE_OPTIONS.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label} — {r.desc}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="form-row">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
              />
              Aktivní účet
            </label>
            {!isActive && (
              <p className="text-danger" style={{ fontSize: "0.75rem", marginTop: "0.3rem" }}>
                Deaktivovaný uživatel se nemůže přihlásit.
              </p>
            )}
          </div>
        </fieldset>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn--primary"
            disabled={mutation.isPending}
          >
            <Save size={16} /> Uložit změny
          </button>
          <button
            type="button"
            className="btn btn--ghost"
            onClick={() => navigate(-1)}
          >
            Zrušit
          </button>
        </div>
      </form>
    </div>
  );
}
