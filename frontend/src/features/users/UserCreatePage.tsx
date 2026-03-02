/**
 * Admin — vytvoření nového uživatele s přiřazením role.
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { usersApi } from "../../api";
import { useToast } from "../../components/Toast";
import { ArrowLeft, UserPlus, Shield } from "lucide-react";

const ROLE_OPTIONS = [
  { value: "ReadOnly", label: "ReadOnly", desc: "Pouze čtení" },
  { value: "Operator", label: "Operator", desc: "Vytváření a editace" },
  { value: "Manager", label: "Manager", desc: "CRUD bez mazání" },
  { value: "Admin", label: "Admin", desc: "Plný přístup — CRUD + mazání + správa uživatelů" },
];

export default function UserCreatePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [group, setGroup] = useState("ReadOnly");
  const [isActive, setIsActive] = useState(true);
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [errors, setErrors] = useState<Record<string, string[]>>({});

  const mutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => usersApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      addToast("success", "Uživatel úspěšně vytvořen.");
      navigate("/users");
    },
    onError: (err: unknown) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data = (err as any)?.response?.data;
      if (data && typeof data === "object") {
        setErrors(data as Record<string, string[]>);
      } else {
        addToast("error", "Chyba při vytváření uživatele.");
      }
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    // Client-side validation
    const clientErrors: Record<string, string[]> = {};
    if (!username.trim()) clientErrors.username = ["Uživatelské jméno je povinné."];
    if (!password) clientErrors.password = ["Heslo je povinné."];
    else if (password.length < 8) clientErrors.password = ["Heslo musí mít alespoň 8 znaků."];
    if (password !== password2) clientErrors.password2 = ["Hesla se neshodují."];

    if (Object.keys(clientErrors).length > 0) {
      setErrors(clientErrors);
      return;
    }

    mutation.mutate({
      username: username.trim(),
      email: email.trim(),
      first_name: firstName.trim(),
      last_name: lastName.trim(),
      group,
      is_active: isActive,
      password,
      password2,
    });
  };

  const fieldError = (field: string) => {
    const msgs = errors[field];
    if (!msgs || msgs.length === 0) return null;
    return (
      <span className="text-danger" style={{ fontSize: "0.75rem", display: "block", marginTop: "0.2rem" }}>
        {Array.isArray(msgs) ? msgs.join(" ") : String(msgs)}
      </span>
    );
  };

  return (
    <div className="user-edit-page">
      <div className="page-header">
        <div className="page-header__left">
          <button className="btn btn--ghost" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} />
          </button>
          <h1 className="page-title">
            <Shield size={20} /> Nový uživatel
          </h1>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="form-grid" style={{ maxWidth: 600 }}>
        <fieldset className="form-section">
          <legend>Přihlašovací údaje</legend>

          <div className="form-row">
            <label className="form-label">
              Uživatelské jméno *
              <input
                className={`input${errors.username ? " input--error" : ""}`}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoFocus
                autoComplete="off"
              />
              {fieldError("username")}
            </label>
          </div>

          <div className="form-row">
            <label className="form-label">
              Heslo *
              <input
                className={`input${errors.password ? " input--error" : ""}`}
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="new-password"
              />
              {fieldError("password")}
            </label>
          </div>

          <div className="form-row">
            <label className="form-label">
              Potvrzení hesla *
              <input
                className={`input${errors.password2 ? " input--error" : ""}`}
                type="password"
                value={password2}
                onChange={(e) => setPassword2(e.target.value)}
                autoComplete="new-password"
              />
              {fieldError("password2")}
            </label>
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Informace</legend>

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
                className={`input${errors.email ? " input--error" : ""}`}
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              {fieldError("email")}
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

        {/* General non-field errors */}
        {errors.non_field_errors && (
          <div className="text-danger" style={{ marginBottom: "1rem" }}>
            {errors.non_field_errors.join(" ")}
          </div>
        )}

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn--primary"
            disabled={mutation.isPending}
          >
            <UserPlus size={16} /> Vytvořit uživatele
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
