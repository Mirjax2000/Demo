/**
 * Přehled montážních týmů s filtry a vyhledáváním.
 */
import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { teamsApi } from "../../api";
import type { Team } from "../../types";
import { Users, MapPin, Phone, Mail, Plus } from "lucide-react";

export default function TeamsPage() {
  const [search, setSearch] = useState("");
  const [activeOnly, setActiveOnly] = useState(true);
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["teams", { search, activeOnly, page }],
    queryFn: () =>
      teamsApi.list({
        search,
        active: activeOnly ? "true" : undefined,
        page,
      }),
    select: (res) => res.data,
  });

  const teams: Team[] = data?.results ?? (Array.isArray(data) ? data : []);
  const count = data?.count ?? 0;
  const pageSize = 25;
  const totalPages = Math.max(1, Math.ceil(count / pageSize));

  return (
    <div className="teams-page">
      <div className="page-header">
        <h1 className="page-title">
          <Users size={24} /> Montážní týmy
        </h1>
        <Link to="/teams/new" className="btn btn--primary">
          <Plus size={16} /> Nový tým
        </Link>
      </div>

      {/* Filtry */}
      <div className="filter-bar">
        <input
          type="text"
          className="input"
          placeholder="Hledat tým..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(e) => {
              setActiveOnly(e.target.checked);
              setPage(1);
            }}
          />
          Pouze aktivní
        </label>
      </div>

      {isLoading && <div className="page-loading">Načítání...</div>}

      {/* Card grid */}
      <div className="card-grid">
        {teams.map((team) => (
          <Link
            key={team.id}
            to={`/teams/${team.slug}`}
            className="team-card"
          >
            <div className="team-card__header">
              <h3 className="team-card__name">{team.name}</h3>
              <span
                className={`badge badge--sm ${
                  team.active ? "badge--green" : "badge--gray"
                }`}
              >
                {team.active ? "Aktivní" : "Neaktivní"}
              </span>
            </div>
            <div className="team-card__body">
              <p>
                <MapPin size={14} /> {team.city}
                {team.region && ` (${team.region})`}
              </p>
              {team.phone && (
                <p>
                  <Phone size={14} /> {team.phone}
                </p>
              )}
              {team.email && (
                <p>
                  <Mail size={14} /> {team.email}
                </p>
              )}
            </div>
          </Link>
        ))}
      </div>

      {teams.length === 0 && !isLoading && (
        <p className="text-muted text-center">Žádné týmy nalezeny.</p>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="btn btn--sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            ← Předchozí
          </button>
          <span className="pagination__info">
            Strana {page} / {totalPages}
          </span>
          <button
            className="btn btn--sm"
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
