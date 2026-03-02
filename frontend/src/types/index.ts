/* ── API v1 TypeScript types ──
 * Generováno z Django modelů a serializátorů.
 */

// ── Auth ──
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  role: "Admin" | "Manager" | "Operator" | "ReadOnly";
}

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

// ── DistribHub ──
export interface DistribHub {
  id: number;
  code: string;
  city: string;
  slug: string;
  label: string;
}

// ── Team ──
export interface Team {
  id: number;
  name: string;
  city: string;
  region: string;
  phone: string;
  email: string;
  active: boolean;
  slug: string;
}

export interface TeamDetail extends Team {
  price_per_hour: string | null;
  price_per_km: string | null;
  notes: string;
  street?: string;
  zip_code?: string;
}

// ── Client ──
export interface Client {
  id: number;
  name: string;
  street: string;
  city: string;
  zip_code: string;
  phone: string;
  email: string;
  incomplete: boolean;
  slug: string;
  formatted_phone: string;
  formatted_psc: string;
}

export interface ClientDetail extends Client {
  order_count: number;
  call_logs?: CallLog[];
}

// ── Article ──
export interface Article {
  id: number;
  name: string;
  quantity: number;
  note: string;
}

// ── Finance ──
export interface FinanceRevenueItem {
  id: number;
  order: number;
  description: string;
  amount: string;
  created: string;
  updated: string;
}

export interface FinanceCostItem {
  id: number;
  order: number;
  team: number | null;
  team_name: string | null;
  description: string;
  amount: string;
  carrier_confirmed: boolean;
  created: string;
  updated: string;
}

// ── Order ──
export interface Order {
  id: number;
  order_number: string;
  mandant: string;
  status: OrderStatus;
  status_display: string;
  team_type: TeamType;
  team_type_display: string;
  distrib_hub: number;
  distrib_hub_label: string;
  client: number | null;
  client_name: string | null;
  client_incomplete: boolean | null;
  team: number | null;
  team_name: string | null;
  evidence_termin: string;
  delivery_termin: string | null;
  montage_termin: string | null;
  naklad: string | null;
  vynos: string | null;
  profit: string;
  has_pdf: boolean;
  has_back_protocol: boolean;
  montage_images_count: number;
  notes: string;
  mail_datum_sended: string | null;
  mail_team_sended: string;
}

export interface OrderDetail extends Order {
  articles: Article[];
  client_detail: Client | null;
  team_detail: Team | null;
  distrib_hub_detail: DistribHub;
  pdf: OrderPDF | null;
  back_protocol: OrderBackProtocol | null;
  montage_images: OrderMontazImage[];
  revenue_items: FinanceRevenueItem[];
  cost_items: FinanceCostItem[];
}

export interface OrderPDF {
  id: number;
  team: string;
  file: string;
  created: string;
}

export interface OrderBackProtocol {
  id: number;
  file: string;
  alt_text: string;
  created: string;
}

export interface OrderMontazImage {
  id: number;
  position: number;
  created: string;
  alt_text: string;
  image: string;
}

// ── Enums ──
export type OrderStatus =
  | "New"
  | "Adviced"
  | "Realized"
  | "Billed"
  | "Canceled"
  | "Hidden";

export type TeamType =
  | "By_customer"
  | "By_delivery_crew"
  | "By_assembly_crew";

// ── Dashboard ──
export interface DashboardData {
  open_orders: {
    nove: number;
    zaterminovane: number;
    realizovane: number;
  };
  closed_orders: {
    vyuctovane: number;
    zrusene: number;
  };
  adviced_type_orders: {
    montazni: number;
    dopravni: number;
  };
  count_all: number;
  hidden: number;
  no_montage_term_count: number;
  no_montage_total_count: number;
  has_no_montage_term: boolean;
  is_invalid: boolean;
  invalid_count: number;
  finance_summary: {
    vynos: number;
    naklad: number;
    profit: number;
  };
  new_issues_count: number;
  customer_r_count: number;
  new_issues_orders?: Order[];
  customer_r_orders?: Order[];
  mandant_options?: string[];
  year_options?: number[];
}

// ── Pagination ──
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ── History ──
export interface HistoryChange {
  field: string;
  old: string;
  new: string;
}

export interface HistoryRecord {
  history_id: number;
  history_date: string;
  history_type: string;
  history_user: string | null;
  model: "Order" | "Article";
  status: string;
  notes: string;
  article_name?: string;
  changes: HistoryChange[];
}

// ── CallLog ──
export interface CallLog {
  id: number;
  client: number;
  client_name: string;
  user: number;
  user_name: string;
  called_at: string;
  note: string;
  was_successful: string;
}

// ── Order write ──
export interface OrderWrite {
  order_number: string;
  mandant: string;
  status?: OrderStatus;
  team_type?: TeamType;
  distrib_hub: number;
  client?: number | null;
  team?: number | null;
  evidence_termin: string;
  delivery_termin?: string | null;
  montage_termin?: string | null;
  naklad?: string | null;
  vynos?: string | null;
  notes?: string;
  articles?: Omit<Article, "id">[];
}
