/**
 * Admin — správa uživatelů: seznam, role, aktivace/deaktivace.
 */
import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { usersApi } from "../../api";
import type { User } from "../../types";
import { Shield, Search, UserPlus } from "lucide-react";

const ROLE_COLORS: Record<string, string> = {
  Admin: "badge--red",
  Manager: "badge--yellow",
  Operator: "badge--green",
  ReadOnly: "badge--gray",
};

export default function UsersPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["users", { search, page }],
    queryFn: () => usersApi.list({ search, page }),
    select: (res) => res.data,
  });

  const users: (User & { is_active?: boolean; date_joined?: string; last_login?: string | null })[] =
    data?.results ?? [];
  const count = data?.count ?? 0;
  const pageSize = 20;
  const totalPages = Math.max(1, Math.ceil(count / pageSize));

  return (
    <div className="users-page">
      <div className="page-header">
        <h1 className="page-title">
          <Shield size={24} /> Správa uživatelů
        </h1>
        <Link to="/users/new" className="btn btn--primary">
          <UserPlus size={16} /> Přidat uživatele
        </Link>
      </div>

      {/* Search */}
      <div className="filter-bar">
        <div className="filter-bar__search">
          <Search size={16} />
          <input
            type="text"
            className="input"
            placeholder="Hledat uživatele..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>
      </div>

      {/* Tabulka */}
      {isLoading ? (
        <div className="page-loading">Načítání...</div>
      ) : (
        <>
          <table className="data-table">
            <thead>
              <tr>
                <th>Uživatel</th>
                <th>Email</th>
                <th>Role</th>
                <th>Aktivní</th>
                <th>Poslední přihlášení</th>
                <th>Registrace</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className={u.is_active === false ? "row--muted" : ""}>
                  <td>
                    <strong>{u.username}</strong>
                    {u.first_name || u.last_name ? (
                      <span className="text-muted"> — {u.first_name} {u.last_name}</span>
                    ) : null}
                  </td>
                  <td>{u.email || <span className="text-muted">—</span>}</td>
                  <td>
                    <span className={`badge badge--sm ${ROLE_COLORS[u.role] || "badge--gray"}`}>
                      {u.role}
                    </span>
                  </td>
                  <td>
                    {u.is_active !== false ? (
                      <span className="text-success">Ano</span>
                    ) : (
                      <span className="text-danger">Ne</span>
                    )}
                  </td>
                  <td className="text-muted">
                    {u.last_login
                      ? new Date(u.last_login).toLocaleString("cs-CZ")
                      : "—"}
                  </td>
                  <td className="text-muted">
                    {u.date_joined
                      ? new Date(u.date_joined).toLocaleDateString("cs-CZ")
                      : "—"}
                  </td>
                  <td>
                    <Link to={`/users/${u.id}/edit`} className="btn btn--ghost btn--sm">
                      Upravit
                    </Link>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={7} className="text-muted" style={{ textAlign: "center" }}>
                    Žádní uživatelé.
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn btn--ghost btn--sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                ← Předchozí
              </button>
              <span className="pagination__info">
                {page} / {totalPages}
              </span>
              <button
                className="btn btn--ghost btn--sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Další →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
