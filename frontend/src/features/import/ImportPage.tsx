/**
 * Import CSV — upload souboru na server.
 */
import { useState, useCallback, type ChangeEvent, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { importApi } from "../../api";
import { Upload, CheckCircle, AlertTriangle, FileText, Bot } from "lucide-react";

export default function ImportPage() {
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const { data: botInfo } = useQuery({
    queryKey: ["bot-token-info"],
    queryFn: () => importApi.botTokenInfo(),
    select: (res) => res.data,
  });

  const mutation = useMutation({
    mutationFn: (f: File) => {
      const fd = new FormData();
      fd.append("file", f);
      return importApi.upload(fd);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const handleFile = useCallback((f: File | null) => {
    if (f && !f.name.endsWith(".csv")) {
      alert("Podporován je pouze formát CSV.");
      return;
    }
    setFile(f);
    mutation.reset();
  }, [mutation]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragActive(false);
      const f = e.dataTransfer.files?.[0] ?? null;
      handleFile(f);
    },
    [handleFile]
  );

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    handleFile(e.target.files?.[0] ?? null);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (file) mutation.mutate(file);
  };

  return (
    <div className="import-page">
      <div className="page-header">
        <h1 className="page-title">
          <Upload size={24} /> Import CSV
        </h1>
      </div>

      <form onSubmit={handleSubmit} className="import-form">
        {/* Drop zone */}
        <div
          className={`drop-zone ${dragActive ? "drop-zone--active" : ""} ${
            file ? "drop-zone--has-file" : ""
          }`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          onClick={() => document.getElementById("csv-input")?.click()}
        >
          <input
            id="csv-input"
            type="file"
            accept=".csv"
            onChange={handleChange}
            style={{ display: "none" }}
          />
          {file ? (
            <div className="drop-zone__selected">
              <FileText size={32} />
              <span>{file.name}</span>
              <small>{(file.size / 1024).toFixed(1)} KB</small>
            </div>
          ) : (
            <div className="drop-zone__prompt">
              <Upload size={40} />
              <p>Přetáhněte CSV soubor sem</p>
              <small>nebo klikněte pro výběr souboru</small>
            </div>
          )}
        </div>

        <button
          type="submit"
          className="btn btn--primary btn--lg"
          disabled={!file || mutation.isPending}
        >
          {mutation.isPending ? "Nahrávám..." : "Importovat"}
        </button>
      </form>

      {/* Výsledek */}
      {mutation.isSuccess && (
        <div className="alert alert--success">
          <CheckCircle size={20} />
          <div>
            <strong>Import úspěšný!</strong>
            <p>
              Vytvořeno: {mutation.data?.data?.created ?? "?"}, Aktualizováno:{" "}
              {mutation.data?.data?.updated ?? "?"}, Přeskočeno:{" "}
              {mutation.data?.data?.skipped ?? "?"}
            </p>
          </div>
        </div>
      )}

      {mutation.isError && (
        <div className="alert alert--danger">
          <AlertTriangle size={20} />
          <div>
            <strong>Chyba importu</strong>
            <p>
              {(mutation.error as Error)?.message ||
                "Nepodařilo se nahrát soubor."}
            </p>
          </div>
        </div>
      )}

      {/* Bot info */}
      {botInfo && (
        <div className="detail-card" style={{ marginBottom: "1.5rem" }}>
          <h3 className="detail-card__title">
            <Bot size={16} /> Stav import bota
          </h3>
          {botInfo.configured ? (
            <dl className="detail-list">
              <dt>Bot uživatel</dt>
              <dd>{botInfo.bot_user}</dd>
              <dt>Stav účtu</dt>
              <dd>
                <span className={`badge badge--sm ${botInfo.is_active ? "badge--green" : "badge--red"}`}>
                  {botInfo.is_active ? "Aktivní" : "Neaktivní"}
                </span>
              </dd>
              <dt>Autentizace</dt>
              <dd>{botInfo.auth_method}</dd>
              <dt>Access token</dt>
              <dd>{botInfo.access_lifetime_minutes} min</dd>
              <dt>Refresh token</dt>
              <dd>{botInfo.refresh_lifetime_days} dní</dd>
              {botInfo.last_login && (
                <>
                  <dt>Poslední přihlášení</dt>
                  <dd>{new Date(botInfo.last_login).toLocaleString("cs-CZ")}</dd>
                </>
              )}
            </dl>
          ) : (
            <p className="text-muted">{botInfo.message}</p>
          )}
        </div>
      )}

      {/* Nápověda */}
      <div className="import-help">
        <h3>Formát CSV souboru</h3>
        <p>
          Soubor musí být v kódování UTF-8 s oddělovačem <code>;</code> (středník).
          Požadované sloupce se liší dle mandanta — systém automaticky rozpozná
          typ dat a provede import.
        </p>
        <p>
          Příklady souborů najdete ve složce <code>files/</code>.
        </p>
      </div>
    </div>
  );
}
