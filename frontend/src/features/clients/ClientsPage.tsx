/**
 * Přehled zákazníků s vyhledáváním a filtry.
 */
import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { clientsApi } from "../../api";
import type { Client } from "../../types";
import { User, MapPin, Phone, Mail, AlertTriangle } from "lucide-react";

export default function ClientsPage() {
  const [search, setSearch] = useState("");
  const [incompleteOnly, setIncompleteOnly] = useState(false);
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["clients", { search, incompleteOnly, page }],
    queryFn: () =>
      clientsApi.list({
        search,
        incomplete: incompleteOnly ? "true" : undefined,
        page,
      }),
    select: (res) => res.data,
  });

  const clients: Client[] = data?.results ?? [];
  const totalPages = data?.count ? Math.ceil(data.count / 25) : 1;

  return (
    <div className="clients-page">
      <div className="page-header">
        <h1 className="page-title">
          <User size={24} /> Zákazníci
        </h1>
        {data?.count !== undefined && (
          <span className="page-header__count">
            Celkem: {data.count}
          </span>
        )}
      </div>

      {/* Filtry */}
      <div className="filter-bar">
        <input
          type="text"
          className="input"
          placeholder="Hledat jméno, město, PSČ..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={incompleteOnly}
            onChange={(e) => {
              setIncompleteOnly(e.target.checked);
              setPage(1);
            }}
          />
          <AlertTriangle size={14} /> Pouze neúplné
        </label>
      </div>

      {isLoading && <div className="page-loading">Načítání...</div>}

      {/* Tabulka */}
      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>Jméno</th>
              <th>Adresa</th>
              <th>PSČ</th>
              <th>Telefon</th>
              <th>Email</th>
              <th>Stav</th>
            </tr>
          </thead>
          <tbody>
            {clients.map((client) => {
              const hasAddress = client.street || client.city;
              const addressParts = [client.street, client.city].filter(Boolean);
              return (
              <tr key={client.id}>
                <td>
                  <Link to={`/clients/${client.slug}`}>{client.name}</Link>
                </td>
                <td>
                  {hasAddress ? (
                    <>
                      <MapPin size={12} /> {addressParts.join(", ")}
                    </>
                  ) : (
                    <span className="text-muted">-</span>
                  )}
                </td>
                <td>{client.formatted_psc || client.zip_code || "-"}</td>
                <td>
                  {client.formatted_phone ? (
                    <>
                      <Phone size={12} /> {client.formatted_phone}
                    </>
                  ) : (
                    <span className="text-muted">-</span>
                  )}
                </td>
                <td>
                  {client.email ? (
                    <>
                      <Mail size={12} /> {client.email}
                    </>
                  ) : (
                    <span className="text-muted">-</span>
                  )}
                </td>
                <td>
                  {client.incomplete ? (
                    <span className="badge badge--red badge--sm">
                      <AlertTriangle size={12} /> Neúplný
                    </span>
                  ) : (
                    <span className="badge badge--green badge--sm">OK</span>
                  )}
                </td>
              </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {clients.length === 0 && !isLoading && (
        <p className="text-muted text-center">Žádní zákazníci nenalezeni.</p>
      )}

      {/* Stránkování */}
      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="btn btn--primary btn--sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            ← Předchozí
          </button>
          <span className="pagination__info">
            Strana {page} z {totalPages}
          </span>
          <button
            className="btn btn--primary btn--sm"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Další →
          </button>
        </div>
      )}
    </div>
  );
}
