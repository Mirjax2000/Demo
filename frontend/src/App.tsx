import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider, useAuth } from "./auth";
import { ToastProvider } from "./components/Toast";
import SidebarLayout from "./layouts/SidebarLayout";
import LoginPage from "./auth/LoginPage";

// Lazy-loaded pages
import { lazy, Suspense, type ReactNode } from "react";

const DashboardPage = lazy(() => import("./features/dashboard/DashboardPage"));
const OrdersPage = lazy(() => import("./features/orders/OrdersPage"));
const OrderDetailPage = lazy(() => import("./features/orders/OrderDetailPage"));
const OrderFormPage = lazy(() => import("./features/orders/OrderFormPage"));
const OrderHistoryPage = lazy(() => import("./features/orders/OrderHistoryPage"));
const ProtocolPage = lazy(() => import("./features/orders/ProtocolPage"));
const FinancePage = lazy(() => import("./features/orders/FinancePage"));
const AssemblyDocsPage = lazy(() => import("./features/orders/AssemblyDocsPage"));
const TeamsPage = lazy(() => import("./features/teams/TeamsPage"));
const TeamDetailPage = lazy(() => import("./features/teams/TeamDetailPage"));
const TeamFormPage = lazy(() => import("./features/teams/TeamFormPage"));
const ClientsPage = lazy(() => import("./features/clients/ClientsPage"));
const ClientDetailPage = lazy(() => import("./features/clients/ClientDetailPage"));
const ClientFormPage = lazy(() => import("./features/clients/ClientFormPage"));
const ImportPage = lazy(() => import("./features/import/ImportPage"));
const ReportsPage = lazy(() => import("./features/reports/ReportsPage"));
const BackProtocolPage = lazy(() => import("./features/orders/BackProtocolPage"));
const UsersPage = lazy(() => import("./features/users/UsersPage"));
const UserCreatePage = lazy(() => import("./features/users/UserCreatePage"));
const UserEditPage = lazy(() => import("./features/users/UserEditPage"));
const PdfViewerPage = lazy(() => import("./features/orders/PdfViewerPage"));
const NotFoundPage = lazy(() => import("./features/NotFoundPage"));

import "./App.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function PageFallback() {
  return <div className="page-loading">Načítání stránky...</div>;
}

/** Wrapper – přesměruje na /login pokud uživatel není přihlášen. */
function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, isLoading } = useAuth();
  if (isLoading) return <PageFallback />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Suspense fallback={<PageFallback />}>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/back-protocol" element={<BackProtocolPage />} />

        {/* Protected — wrapped in SidebarLayout */}
        <Route
          element={
            <ProtectedRoute>
              <SidebarLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<DashboardPage />} />

          {/* Orders */}
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/orders/new" element={<OrderFormPage />} />
          <Route path="/orders/:id" element={<OrderDetailPage />} />
          <Route path="/orders/:id/edit" element={<OrderFormPage />} />
          <Route path="/orders/:id/history" element={<OrderHistoryPage />} />
          <Route path="/orders/:id/protocol" element={<ProtocolPage />} />
          <Route path="/orders/:id/finance" element={<FinancePage />} />
          <Route path="/orders/:id/assembly-docs" element={<AssemblyDocsPage />} />
          <Route path="/orders/:id/pdf" element={<PdfViewerPage />} />

          {/* Teams */}
          <Route path="/teams" element={<TeamsPage />} />
          <Route path="/teams/new" element={<TeamFormPage />} />
          <Route path="/teams/:slug" element={<TeamDetailPage />} />
          <Route path="/teams/:slug/edit" element={<TeamFormPage />} />

          {/* Clients */}
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/clients/:slug" element={<ClientDetailPage />} />
          <Route path="/clients/:slug/edit" element={<ClientFormPage />} />

          {/* Import */}
          <Route path="/import" element={<ImportPage />} />

          {/* Reports */}
          <Route path="/reports" element={<ReportsPage />} />

          {/* Users (Admin) */}
          <Route path="/users" element={<UsersPage />} />
          <Route path="/users/new" element={<UserCreatePage />} />
          <Route path="/users/:id/edit" element={<UserEditPage />} />
        </Route>

        {/* Default redirect for / */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <ToastProvider>
            <AppRoutes />
          </ToastProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
