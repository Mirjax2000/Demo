/**
 * SearchableSelect — server-side searchable dropdown.
 *
 * Replaces plain <select> for large datasets. Uses debounced API queries
 * so we never need to fetch all records at once.
 */
import { useState, useRef, useEffect, useCallback } from "react";

export interface SelectOption {
  value: string | number;
  label: string;
}

interface Props {
  /** Currently selected value (id) */
  value: string | number | null | undefined;
  /** Callback when user picks an option */
  onChange: (value: string) => void;
  /** Async function that returns options for a search term */
  fetchOptions: (search: string) => Promise<SelectOption[]>;
  /** Placeholder when nothing selected */
  placeholder?: string;
  /** Extra CSS class on the wrapper */
  className?: string;
  /** Name attribute for form compatibility */
  name?: string;
  /** Disable the component */
  disabled?: boolean;
  /** Pre-loaded options (shown before any search, e.g. initial page) */
  initialOptions?: SelectOption[];
}

export default function SearchableSelect({
  value,
  onChange,
  fetchOptions,
  placeholder = "Hledat…",
  className = "",
  name,
  disabled,
  initialOptions = [],
}: Props) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [options, setOptions] = useState<SelectOption[]>(initialOptions);
  const [loading, setLoading] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Keep initialOptions in sync
  useEffect(() => {
    if (initialOptions.length && !options.length) {
      setOptions(initialOptions);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialOptions]);

  // Debounced fetch
  const doSearch = useCallback(
    (term: string) => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(async () => {
        setLoading(true);
        try {
          const result = await fetchOptions(term);
          setOptions(result);
        } finally {
          setLoading(false);
        }
      }, 300);
    },
    [fetchOptions],
  );

  // Search on input change
  useEffect(() => {
    if (open) doSearch(search);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [search, open, doSearch]);

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const selectedLabel = options.find((o) => String(o.value) === String(value))?.label;
  // If value is set but label not found in current options, show value
  const displayText = selectedLabel ?? (value ? `ID ${value}` : "");

  const handleSelect = (opt: SelectOption) => {
    onChange(String(opt.value));
    setSearch("");
    setOpen(false);
  };

  const handleClear = () => {
    onChange("");
    setSearch("");
    setOpen(false);
  };

  return (
    <div
      ref={wrapperRef}
      className={`searchable-select ${className}`}
      style={{ position: "relative" }}
    >
      {name && <input type="hidden" name={name} value={value ?? ""} />}

      {/* Trigger / display */}
      {!open ? (
        <button
          type="button"
          className="input searchable-select__trigger"
          onClick={() => {
            if (!disabled) {
              setOpen(true);
              setTimeout(() => inputRef.current?.focus(), 0);
            }
          }}
          disabled={disabled}
          style={{
            textAlign: "left",
            cursor: disabled ? "not-allowed" : "pointer",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            width: "100%",
          }}
        >
          <span style={{ opacity: displayText ? 1 : 0.5 }}>
            {displayText || placeholder}
          </span>
          {value ? (
            <span
              onClick={(e) => {
                e.stopPropagation();
                handleClear();
              }}
              style={{ cursor: "pointer", marginLeft: 8, opacity: 0.6 }}
              title="Vymazat"
            >
              ✕
            </span>
          ) : (
            <span style={{ opacity: 0.4 }}>▾</span>
          )}
        </button>
      ) : (
        <input
          ref={inputRef}
          type="text"
          className="input"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={placeholder}
          style={{ width: "100%" }}
        />
      )}

      {/* Dropdown */}
      {open && (
        <ul
          className="searchable-select__dropdown"
          style={{
            position: "absolute",
            top: "100%",
            left: 0,
            right: 0,
            zIndex: 50,
            maxHeight: 220,
            overflowY: "auto",
            background: "var(--color-surface, #fff)",
            border: "1px solid var(--color-border, #d1d5db)",
            borderRadius: "0 0 6px 6px",
            margin: 0,
            padding: 0,
            listStyle: "none",
            boxShadow: "0 4px 12px rgba(0,0,0,.12)",
          }}
        >
          {/* Empty option */}
          <li
            className="searchable-select__option"
            onClick={handleClear}
            style={{
              padding: "6px 10px",
              cursor: "pointer",
              opacity: 0.5,
              fontSize: "0.92em",
            }}
          >
            {placeholder}
          </li>

          {loading && (
            <li style={{ padding: "6px 10px", opacity: 0.5, fontSize: "0.92em" }}>
              Načítám…
            </li>
          )}

          {!loading && options.length === 0 && (
            <li style={{ padding: "6px 10px", opacity: 0.5, fontSize: "0.92em" }}>
              Žádné výsledky
            </li>
          )}

          {options.map((opt) => (
            <li
              key={opt.value}
              className={`searchable-select__option${String(opt.value) === String(value) ? " searchable-select__option--active" : ""}`}
              onClick={() => handleSelect(opt)}
              style={{
                padding: "6px 10px",
                cursor: "pointer",
                background:
                  String(opt.value) === String(value)
                    ? "var(--color-primary-light, #e0e7ff)"
                    : undefined,
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.background =
                  "var(--color-primary-light, #e0e7ff)")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.background =
                  String(opt.value) === String(value)
                    ? "var(--color-primary-light, #e0e7ff)"
                    : "transparent")
              }
            >
              {opt.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
