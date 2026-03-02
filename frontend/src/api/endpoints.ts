/**
 * API endpointy — všechny volání na backend.
 */
import api from "./client";
import type {
  DashboardData,
  Order,
  OrderDetail,
  OrderWrite,
  PaginatedResponse,
  Team,
  TeamDetail,
  Client,
  ClientDetail,
  DistribHub,
  Article,
  FinanceRevenueItem,
  FinanceCostItem,
  HistoryRecord,
  CallLog,
  User,
} from "../types";

// ── Auth (cookies — tokeny jsou v httpOnly cookies) ──
export const authApi = {
  login: (username: string, password: string) =>
    api.post<{ detail: string }>("/auth/login/", { username, password }),

  refresh: () =>
    api.post<{ detail: string }>("/auth/refresh/", {}),

  logout: () =>
    api.post<{ detail: string }>("/auth/logout/", {}),

  register: (data: {
    username: string;
    email: string;
    password: string;
    password2: string;
  }) => api.post("/auth/register/", data),

  me: () => api.get<User>("/auth/me/"),
};

// ── Orders ──
export const ordersApi = {
  list: (params?: Record<string, string | number | undefined>) =>
    api.get<PaginatedResponse<Order>>("/orders/", { params }),

  autocompleteDelivery: (term: string) =>
    api.get<{ orders: string[] }>("/orders/autocomplete-delivery/", { params: { term } }),

  detail: (id: number) => api.get<OrderDetail>(`/orders/${id}/`),

  create: (data: OrderWrite) => api.post<Order>("/orders/", data),

  update: (id: number, data: Partial<OrderWrite>) =>
    api.patch<Order>(`/orders/${id}/`, data),

  delete: (id: number) => api.delete(`/orders/${id}/`),

  hide: (id: number) => api.post(`/orders/${id}/hide/`),

  switchToRealized: (id: number) =>
    api.post(`/orders/${id}/switch-to-realized/`),

  switchToAssembly: (id: number) =>
    api.post(`/orders/${id}/switch-to-assembly/`),

  generatePdf: (id: number) => api.post(`/orders/${id}/generate-pdf/`),

  downloadPdf: (id: number) =>
    api.get(`/orders/${id}/download-pdf/`, { responseType: "blob" }),

  viewPdf: (id: number) =>
    api.get(`/orders/${id}/view-pdf/`, { responseType: "blob" }),

  downloadMontageZip: (id: number) =>
    api.get(`/orders/${id}/download-montage-zip/`, { responseType: "blob" }),

  sendMail: (id: number) => api.post(`/orders/${id}/send-mail/`),

  history: (id: number) => api.get<HistoryRecord[]>(`/orders/${id}/history/`),

  uploadBackProtocol: (orderId: number, formData: FormData) =>
    api.post(`/orders/${orderId}/back-protocol/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),

  exportExcel: (params?: Record<string, string | number | undefined>) =>
    api.get("/orders/export-excel/", { params, responseType: "blob" }),

  // Nested: articles
  articles: (orderId: number) =>
    api.get<Article[]>(`/orders/${orderId}/articles/`),

  createArticle: (orderId: number, data: Omit<Article, "id">) =>
    api.post<Article>(`/orders/${orderId}/articles/`, data),

  updateArticle: (orderId: number, articleId: number, data: Partial<Article>) =>
    api.patch<Article>(`/orders/${orderId}/articles/${articleId}/`, data),

  deleteArticle: (orderId: number, articleId: number) =>
    api.delete(`/orders/${orderId}/articles/${articleId}/`),

  // Nested: montage images
  images: (orderId: number) =>
    api.get(`/orders/${orderId}/images/`),

  uploadImage: (orderId: number, formData: FormData) =>
    api.post(`/orders/${orderId}/images/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),

  deleteImage: (orderId: number, imageId: number) =>
    api.delete(`/orders/${orderId}/images/${imageId}/`),
};

// ── Teams ──
export const teamsApi = {
  list: (params?: Record<string, string | number | undefined>) =>
    api.get<PaginatedResponse<Team>>("/teams/", { params }),

  detail: (slug: string) => api.get<TeamDetail>(`/teams/${slug}/`),

  create: (data: Partial<TeamDetail>) => api.post<TeamDetail>("/teams/", data),

  update: (slug: string, data: Partial<TeamDetail>) =>
    api.patch<TeamDetail>(`/teams/${slug}/`, data),

  delete: (slug: string) => api.delete(`/teams/${slug}/`),
};

// ── Clients ──
export const clientsApi = {
  list: (params?: Record<string, string | number | undefined>) =>
    api.get<PaginatedResponse<Client>>("/clients/", { params }),

  detail: (slug: string) => api.get<ClientDetail>(`/clients/${slug}/`),

  update: (slug: string, data: Partial<Client>) =>
    api.patch<Client>(`/clients/${slug}/`, data),

  orders: (slug: string) => api.get<Order[]>(`/clients/${slug}/orders/`),

  exportData: (slug: string) => api.get(`/clients/${slug}/export-data/`),
};

// ── Dashboard ──
export const dashboardApi = {
  get: (params?: Record<string, string | number | undefined>) =>
    api.get<DashboardData>("/dashboard/", { params }),
};

// ── Finance ──
export const financeApi = {
  revenues: (orderId: number) =>
    api.get<PaginatedResponse<FinanceRevenueItem>>("/finance/revenue/", {
      params: { order: orderId },
    }),

  createRevenue: (data: Partial<FinanceRevenueItem>) =>
    api.post<FinanceRevenueItem>("/finance/revenue/", data),

  updateRevenue: (id: number, data: Partial<FinanceRevenueItem>) =>
    api.patch<FinanceRevenueItem>(`/finance/revenue/${id}/`, data),

  deleteRevenue: (id: number) => api.delete(`/finance/revenue/${id}/`),

  costs: (orderId: number) =>
    api.get<PaginatedResponse<FinanceCostItem>>("/finance/costs/", {
      params: { order: orderId },
    }),

  createCost: (data: Partial<FinanceCostItem>) =>
    api.post<FinanceCostItem>("/finance/costs/", data),

  updateCost: (id: number, data: Partial<FinanceCostItem>) =>
    api.patch<FinanceCostItem>(`/finance/costs/${id}/`, data),

  deleteCost: (id: number) => api.delete(`/finance/costs/${id}/`),
};

// ── DistribHubs ──
export const distribHubsApi = {
  list: () => api.get<DistribHub[]>("/distrib-hubs/"),
};

// ── CallLogs ──
export const callLogsApi = {
  list: (params?: Record<string, string | number | undefined>) =>
    api.get<PaginatedResponse<CallLog>>("/call-logs/", { params }),

  create: (data: Partial<CallLog>) => api.post<CallLog>("/call-logs/", data),

  delete: (id: number) => api.delete(`/call-logs/${id}/`),
};

// ── CSV Import ──
export const importApi = {
  upload: (formData: FormData) =>
    api.post("/import/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),

  botTokenInfo: () => api.get("/bot-token-info/"),
};

// ── Users (Admin) ──
export const usersApi = {
  list: (params?: Record<string, string | number | undefined>) =>
    api.get<PaginatedResponse<User>>("/users/", { params }),

  detail: (id: number) => api.get<User & { is_active: boolean; date_joined: string; last_login: string | null }>(`/users/${id}/`),

  create: (data: Record<string, unknown>) =>
    api.post<User>("/users/", data),

  update: (id: number, data: Record<string, unknown>) =>
    api.patch<User>(`/users/${id}/`, data),
};

// ── Health ──
export const healthApi = {
  check: () => api.get("/health/"),
};
