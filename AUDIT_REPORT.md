# Exhaustive Audit Report: Django SSR vs React + DRF API

> Hloubkové porovnání původní Django SSR aplikace (`app_sprava_montazi/`)
> s novým React frontendem (`frontend/src/`) a REST API v1 (`api_v1/`).
>
> Zahrnuje také původní Django bot-API (`API/`), bezpečnostní audit (GDPR, enterprise)
> a kompletní seznam TODO úkolů.
>
> **Stav**: aktualizováno 2. 3. 2026

---

## Obsah

1. [Přehled architektury](#1-přehled-architektury)
2. [Modely — pokrytí serializátory](#2-modely--pokrytí-serializátory)
3. [Views / Business logika — parita API akcí](#3-views--business-logika--parita-api-akcí)
4. [Formuláře / Validace — klient vs server](#4-formuláře--validace--klient-vs-server)
5. [Šablony vs React stránky — feature-by-feature](#5-šablony-vs-react-stránky--feature-by-feature)
6. [URL Routing — chybějící trasy](#6-url-routing--chybějící-trasy)
7. [Původní Django bot-API (API/ app)](#7-původní-django-bot-api-api-app)
8. [Bezpečnost — Enterprise / GDPR](#8-bezpečnost--enterprise--gdpr)
9. [Opravené bugy a implementace (tato session)](#9-opravené-bugy-a-implementace-tato-session)
10. [Zbývající problémy a nedostatky](#10-zbývající-problémy-a-nedostatky)
11. [TODO — seřazeno dle priority](#11-todo--seřazeno-dle-priority)

---

## 1. Přehled architektury

### 1.1 Původní Django SSR stack

| Komponenta | Technologie |
|-----------|-------------|
| Backend | Django 5.2, Python 3.14 |
| Auth | Session-based (`LoginRequiredMixin`) + Token auth pro bot-API (`ExpiringTokenAuthentication`) |
| Šablony | Django templates (`base.html` + `app_sprava_montazi/templates/`) |
| DataTables | Server-side (`JsonOrders` → AJAX JSON odpovědi) |
| PDF generátor | `OOP_protokols.py` → `SCCZPdfGenerator` (ReportLab) |
| E-mail | `OOP_emails.py` → `CustomEmail` (šifrované PDF přílohy) |
| QR validace | `utils.py` → `get_qrcode_value()` (OpenCV) |
| WebP konverze | `utils.py` → `convert_image_to_webp()` (Pillow) |
| Zpětný protokol | `OOP_back_protocol.py` → `ProtocolUploader` |
| CSV import | Management command `import_data` |
| History | `simple_history` → `HistoricalRecords` na všech modelech |
| Bot API | `API/` app — Token auth, 5 endpointů pro externího bota |
| DB | SQLite (dev), PostgreSQL (prod) |

### 1.2 Nový React + DRF stack

| Komponenta | Technologie |
|-----------|-------------|
| Frontend | React 19, TypeScript, Vite 7.3 |
| State management | React Query (TanStack) |
| Routing | React Router v7 |
| Charty | Recharts |
| Auth | JWT (simplejwt) — ACCESS 60 min, REFRESH 7 dní |
| API | DRF 3.16 + `api_v1/` app |
| Filtry | `django-filters` (`OrderFilter`, `ClientFilter`, `TeamFilter`, …) |
| Swagger | `drf-spectacular` |
| CORS | `django-cors-headers` |

### 1.3 Architekturní rozdíly

| Aspekt | Django SSR | React + API |
|--------|-----------|-------------|
| Rendering | Server-side (HTML) | Client-side (SPA) |
| Auth flow | Session cookie | JWT Bearer token |
| Data fetching | Přímý ORM v views | REST API → JSON |
| Formuláře | Django ModelForm + formset | React useState + manually built |
| Validace | Server-side v `clean()` | Klient-side + server-side v serializer `validate()` |
| Real-time data | Page reload | React Query polling/invalidation |
| Navigace | Full page reload | SPA routing |
| Error badge | `ErrorContextMixin` → každý request | Dashboard polling (60s interval) |

---

## 2. Modely — pokrytí serializátory

### 2.1 Order — field-by-field

| Model Field | `OrderListSerializer` | `OrderDetailSerializer` | `OrderWriteSerializer` | Poznámka |
|-------------|----------------------|------------------------|----------------------|----------|
| `order_number` | ✅ | ✅ | ✅ | Write: uppercase + uniqueness validace |
| `distrib_hub` | ✅ (id) | ✅ + `distrib_hub_detail` | ✅ | |
| `team` | ✅ (id) | ✅ + `team_detail` | ✅ | |
| `mail_datum_sended` | ✅ | ✅ | ❌ read-only | Správně — nastavuje se v `send_mail` akci |
| `mail_team_sended` | ✅ | ✅ | ❌ read-only | Správně |
| `mandant` | ✅ | ✅ | ✅ | |
| `status` | ✅ | ✅ | ✅ | |
| `client` | ✅ (id) | ✅ + `client_detail` | ✅ (id) | + `client_data` DictField pro get_or_create |
| `evidence_termin` | ✅ | ✅ | ✅ | |
| `delivery_termin` | ✅ | ✅ | ✅ | |
| `montage_termin` | ✅ | ✅ | ✅ | |
| `team_type` | ✅ | ✅ | ✅ | |
| `notes` | ✅ | ✅ | ✅ | |
| `naklad` | ✅ | ✅ | ✅ | |
| `vynos` | ✅ | ✅ | ✅ | |
| `profit` (computed) | ✅ | ✅ | ❌ read-only | Správně |
| `status_display` | ✅ | ✅ | ❌ | Správně |
| `team_type_display` | ✅ | ✅ | ❌ | Správně |
| `has_pdf` | ✅ | ✅ | ❌ | Správně |
| `has_back_protocol` | ✅ | ✅ | ❌ | Správně |
| `montage_images_count` | ✅ | ✅ | ❌ | Správně |
| `articles` (nested) | ❌ | ✅ | ✅ (write) | |
| `pdf` (nested) | ❌ | ✅ | ❌ | Správně |
| `back_protocol` | ❌ | ✅ | ❌ | Správně |
| `montage_images` | ❌ | ✅ | ❌ | Správně |
| `revenue_items` | ❌ | ✅ | ❌ | Správně |
| `cost_items` | ❌ | ✅ | ❌ | Správně |

### 2.2 Client — field-by-field

| Model Field | `ClientListSerializer` | `ClientDetailSerializer` | Poznámka |
|-------------|----------------------|--------------------------|----------|
| `name` | ✅ | ✅ | |
| `street` | ✅ | ✅ | |
| `city` | ✅ | ✅ | |
| `zip_code` | ✅ | ✅ | |
| `phone` | ✅ | ✅ | |
| `email` | ✅ | ✅ | |
| `incomplete` | ✅ | ✅ | Automaticky počítaný v `Client.save()` |
| `slug` | ✅ | ✅ | |
| `formatted_phone` | ✅ | ✅ | Model metoda |
| `formatted_psc` | ✅ | ✅ | Model metoda |
| `order_count` | ❌ | ✅ | |
| `call_logs` | ❌ | ✅ | ✅ Opraveno — `source="calls"`, read-only |

### 2.3 Team — field-by-field

| Model Field | `TeamListSerializer` | `TeamDetailSerializer` | Poznámka |
|-------------|---------------------|----------------------|----------|
| `name` | ✅ | ✅ | |
| `city` | ✅ | ✅ | |
| `region` | ✅ | ✅ | |
| `phone` | ✅ | ✅ | |
| `email` | ✅ | ✅ | |
| `active` | ✅ | ✅ | |
| `slug` | ✅ | ✅ | |
| `price_per_hour` | ❌ | ✅ | Správně — detail only |
| `price_per_km` | ❌ | ✅ | Správně |
| `notes` | ❌ | ✅ | Správně |

### 2.4 Modely / relace v API

| Model | Stav | Detail |
|-------|------|--------|
| `FinanceRevenueItem` | ✅ plný CRUD | `FinanceRevenueItemViewSet` |
| `FinanceCostItem` | ✅ plný CRUD | `FinanceCostItemViewSet` |
| `CallLog` | ✅ CRUD | `CallLogViewSet` + vnořeno v `ClientDetailSerializer` (read-only) |
| `AppSetting` | ✅ read-only | `AppSettingViewSet` |
| `OrderBackProtocolToken` | ⚠️ interní | Vytvářen v `send_mail` akci, není exponován |
| `Upload` | ✅ | Přes `CSVImportView` |
| `OrderPDFStorage` | ✅ vnořený read | Přes `OrderDetailSerializer.pdf` |
| `OrderMontazImage` | ✅ plný CRUD | `OrderMontazImageViewSet` (API existuje, **React UI chybí**) |
| `OrderBackProtocol` | ⚠️ read-only vnořený | **Chybí upload endpoint** v API v1 |

---

## 3. Views / Business logika — parita API akcí

### 3.1 Akce po jedné — porovnání

| Django SSR View | API v1 Endpoint | React stránka | Stav | Poznámka |
|----------------|----------------|--------------|------|----------|
| `DashboardView` | `GET /api/v1/dashboard/` | `DashboardPage.tsx` | ✅ | Filtry: year, month, mandant, distrib_hub. API vrací counts + detail tabulky (max 20) + dynamické mandant/year options |
| `OrdersView` (DataTables) | `GET /api/v1/orders/` | `OrdersPage.tsx` | ✅ | DRF pagination + filtry nahrazují server-side DataTables |
| `OrderCreateView` | `POST /api/v1/orders/` | `OrderFormPage.tsx` | ✅ | `client_data` → `_resolve_client()` s `get_or_create` ✅ |
| `OrderUpdateView` | `PATCH /api/v1/orders/{id}/` | `OrderFormPage.tsx` | ✅ | Per-article CRUD (ne bulk delete+recreate) ✅ |
| `OrderDeleteView` | `DELETE /api/v1/orders/{id}/` | `OrderDetailPage.tsx` | ✅ | Guard `status == HIDDEN` ✅ |
| `OrderDetailView` | `GET /api/v1/orders/{id}/` | `OrderDetailPage.tsx` | ✅ | |
| `OrderHiddenView` | `POST /api/v1/orders/{id}/hide/` | `OrderDetailPage.tsx` | ✅ | Guard `status == NEW` |
| `SwitchAdvicedWithDeliveryToRealizedView` | `POST /api/v1/orders/{id}/switch-to-realized/` | `OrderDetailPage.tsx` | ✅ | Guard `ADVICED + BY_DELIVERY_CREW` ✅ |
| `SwitchRealizationToAssemblyView` | `POST /api/v1/orders/{id}/switch-to-assembly/` | `DashboardPage.tsx` | ✅ | Guard `NEW + BY_CUSTOMER` → `team_type = BY_ASSEMBLY_CREW` ✅ |
| `GeneratePDFView` | `POST /api/v1/orders/{id}/generate-pdf/` | `ProtocolPage.tsx` | ✅ | Používá `pdf_generator_classes` |
| `OrderPdfView` / `CheckPDFProtocolView` | `GET /api/v1/orders/{id}/download-pdf/` | `ProtocolPage.tsx` | ⚠️ | Funkční, ale `<a href>` link nesenduje JWT — viz §8 |
| `SendMailView` | `POST /api/v1/orders/{id}/send-mail/` | `ProtocolPage.tsx` | ✅ | Vytvoří token, odešle šifrovaný PDF email |
| `OrderHistoryView` | `GET /api/v1/orders/{id}/history/` | `OrderHistoryPage.tsx` | ✅ | Kombinovaná Order + Article historie s field-level diffs ✅ |
| `ExportOrdersExcelView` | `GET /api/v1/orders/export-excel/` | `OrdersPage.tsx` / `ReportsPage.tsx` | ✅ | |
| `ClientUpdateView` | `PATCH /api/v1/clients/{slug}/` | `ClientFormPage.tsx` | ✅ | |
| `ClientUpdateSecondaryView` | `PATCH /api/v1/clients/{slug}/` | `ClientFormPage.tsx` | ✅ | Obě Django views mapovány na jeden endpoint |
| `ClientsOrdersView` | `GET /api/v1/clients/{slug}/orders/` | `ClientDetailPage.tsx` | ✅ | |
| `TeamsView` | `GET /api/v1/teams/` | `TeamsPage.tsx` | ✅ | |
| `TeamCreateView` | `POST /api/v1/teams/` | `TeamFormPage.tsx` | ✅ | |
| `TeamUpdateView` | `PATCH /api/v1/teams/{slug}/` | `TeamFormPage.tsx` | ✅ | |
| `TeamDeleteView` | `DELETE /api/v1/teams/{slug}/` | `TeamFormPage.tsx` | ✅ | Guard `active == False` ✅ |
| `TeamDetailView` | `GET /api/v1/teams/{slug}/` | `TeamDetailPage.tsx` | ✅ | |
| `ReportsView` | `GET /api/v1/orders/?status=Realized` | `ReportsPage.tsx` | ✅ | React reusuje Orders endpoint s filtrem |
| `FinanceDetailView` | Revenue/Cost CRUD endpointy | `FinancePage.tsx` | ✅ | Plný CRUD + carrier_confirmed toggle |
| `CreatePageView` (CSV import) | `POST /api/v1/import/` | `ImportPage.tsx` | ✅ | |
| **`BackProtocolView`** (ext. stránka) | **CHYBÍ** | **CHYBÍ** | 🟥 | Token-gated externí upload s QR validací |
| **`UploadBackProtocolView`** | **CHYBÍ** | **CHYBÍ** | 🟥 | Upload zpětného protokolu s QR + WebP konverzí |
| **`ProtocolUploadView`** | **CHYBÍ** | **CHYBÍ** | 🟥 | Fallback upload protokolu z create stránky |
| **`MontageImgUploadView`** | Existuje v API (`POST /orders/{id}/images/`) | **CHYBÍ v UI** | 🟧 | API endpoint je, ale React UI pro upload neexistuje |
| **`UploadOneImageView`** | Existuje v API | **CHYBÍ v UI** | 🟧 | Stejné jako výše |
| **`AssemblyDocsView`** | **CHYBÍ** | **CHYBÍ** | 🟥 | Stránka montážní dokumentace |
| **`DownloadMontageImagesZipView`** | **CHYBÍ** | **CHYBÍ** | 🟥 | ZIP stažení fotek montáže |
| `AutocompleteOrdersByDeliveryGroupView` | **CHYBÍ** | **CHYBÍ** | ⚠️ | Autocomplete pro zakázky |
| `OrderStatusView` | **CHYBÍ** | **CHYBÍ** | ⚠️ | API check statusu zakázky |
| `PdfView` (standalone) | **CHYBÍ** | **CHYBÍ** | ⚠️ | PDF preview pro mandanty |
| `HomePageView` | N/A | `/dashboard` | ✅ | Dashboard nahrazuje homepage |

### 3.2 Automatický přechod stavů v `Order.save()`

Django model `Order` obsahuje dvě metody volané v `save()`:

| Metoda | Podmínky | Efekt |
|--------|---------|-------|
| `zaterminovano_with_montage_team()` | `status=NEW`, `team_type=BY_ASSEMBLY_CREW`, team+client+client.complete+evidence+delivery+montage+vynos+naklad | `status → ADVICED` |
| `zaterminovano_with_delivery_team()` | `status=NEW`, `team_type=BY_DELIVERY_CREW`, !team+client+evidence+delivery+!montage+vynos+naklad | `status → ADVICED` |

> ✅ Tyto přechody fungují i při uložení přes API, protože volají `order.save()` na modelu — ORM logika je sdílená.

### 3.3 `ErrorContextMixin` — badge počítadlo chyb

| Aspekt | Django SSR | React |
|--------|-----------|-------|
| Trigger | Každý request (mixin na všech views) | Dashboard polling co 60s (`SidebarLayout`) |
| Data | `call_errors_adviced()` → `(bool, int)` | `dashboardApi.get()` → `invalid_count` |
| Zobrazení | Červený badge v navbar u "Zakázky" | Červený badge v sidebar u "Zakázky" |

> ✅ Funkčně ekvivalentní. React varianta je efektivnější (méně DB dotazů), ale data mohou být max 60s stará.

---

## 4. Formuláře / Validace — klient vs server

### 4.1 OrderForm — validace Adviced stavu

#### `By_assembly_crew` (montáž)

| Pravidlo | Django `OrderForm` | React `OrderFormPage` | API `OrderWriteSerializer` |
|----------|-------------------|----------------------|--------------------------|
| Zákazník povinný | ✅ | ✅ | ✅ |
| Zákazník nesmí být `incomplete` | ✅ | ❌ **CHYBÍ** | ❌ **CHYBÍ** |
| Tým povinný | ✅ | ✅ | ✅ |
| `montage_termin` povinný | ✅ | ✅ | ✅ |
| `delivery_termin` povinný | ✅ | ✅ | ✅ |
| `naklad` povinný & > 0 | ✅ | ✅ | ✅ |
| `vynos` povinný & > 0 | ✅ | ✅ | ✅ |

#### `By_delivery_crew` (doprava)

| Pravidlo | Django | React | API |
|----------|-------|-------|-----|
| Zákazník povinný | ✅ | ✅ | ✅ |
| `delivery_termin` povinný | ✅ | ✅ | ✅ |
| `naklad` & `vynos` povinné | ✅ | ✅ | ✅ |
| Tým musí být **null** | ✅ | ✅ | ✅ |
| `montage_termin` musí být **null** | ✅ | ✅ | ✅ |

#### `By_customer` (zákazník)

| Pravidlo | Django | React | API |
|----------|-------|-------|-----|
| Nelze nastavit Adviced | ✅ (`add_error`) | ✅ (alert) | ✅ (`ValidationError`) |

> **Zbývající mezera**: Django form kontroluje `client.incomplete` — pokud je zákazník neúplný, nelze uložit jako Adviced (montáž). React ani API toto nekontrolují.

### 4.2 OrderForm.clean_order_number()

| Chování | Django | React | API |
|---------|-------|-------|-----|
| Uppercase konverze | ✅ | ✅ (`toUpperCase()`) | ✅ (`validate_order_number`) |
| Unikátnost (case-insensitive) | ✅ | ❌ (spoléhá na backend) | ✅ |

### 4.3 ClientForm validace

| Pravidlo | Django | React (`ClientFormPage`) | API |
|----------|-------|--------------------------|-----|
| `name` disabled při editaci | ✅ | ✅ | Ne vynuceno serverem |
| `zip_code` disabled při editaci | ✅ | ✅ | Ne vynuceno serverem |
| `zip_code` musí mít 5 znaků | ✅ (`clean_zip_code`) | ❌ **CHYBÍ** | ❌ **CHYBÍ** |
| `Client.clean()` (name+zip required) | ✅ | N/A (edit only) | Model `.save()` |

### 4.4 TeamForm validace

| Pravidlo | Django | React (`TeamFormPage`) | API |
|----------|-------|------------------------|-----|
| `name` disabled při editaci | ✅ | ✅ | Ne vynuceno |
| `clean_name` — slug unikátnost | ✅ | ❌ **CHYBÍ** | ❌ **CHYBÍ** |

### 4.5 ArticleForm validace

| Pravidlo | Django | React (`OrderFormPage`) |
|----------|-------|------------------------|
| `quantity` 0-999 rozsah | ✅ (`clean_quantity`) | HTML `min=1 max=999` |
| `name` povinný | ✅ | Žádný explicitní check |

### 4.6 MonthFilterForm (Dashboard)

| Pole | Django | React |
|------|-------|-------|
| `month` volby (1-12 + prázdná) | ✅ dynamicky | ✅ hardcoded 1-12 |
| `year` volby (dynamicky z DB) | ✅ `Order.objects.dates(...)` | ✅ **Opraveno** — API vrací `year_options` |
| `mandant` volby (dynamicky distinct) | ✅ `Order.objects.values_list(...)` | ✅ **Opraveno** — API vrací `mandant_options` |
| `distrib_hub` volby (z DB) | ✅ | ✅ `distribHubsApi.list()` |

### 4.7 Finance formuláře

| Pravidlo | Django | React (`FinancePage`) |
|----------|-------|----------------------|
| Revenue: popis + částka povinné | ✅ | ✅ (HTML `required`) |
| Cost: popis + částka povinné | ✅ | ✅ |
| Cost: výběr týmu | ✅ | ✅ |
| Cost: `carrier_confirmed` toggle | ✅ | ✅ (ikonka tlačítko) |
| Delete revenue/cost | ✅ | ✅ |
| **Editace existujících položek** | ✅ | ❌ Pouze create + delete |

### 4.8 CallLog FormSet

| Feature | Django | React (`ClientFormPage`) |
|---------|-------|--------------------------|
| Inline formset na stránce klienta | ✅ | ✅ |
| Zobrazení existujících call log | ✅ | ✅ |
| Přidání nového call log | ✅ | ✅ |
| Uložení call log s client update | ✅ (formset) | ✅ **Opraveno** — `callLogsApi.create()` sekvenčně |
| Mazání call log | ✅ (formset `DELETE`) | ❌ **CHYBÍ** |

---

## 5. Šablony vs React stránky — feature-by-feature

### 5.1 Dashboard

| Feature | Django | React | Stav |
|---------|-------|-------|------|
| Filtr bar (měsíc/rok/mandant/hub) | ✅ | ✅ | ✅ |
| Open orders pie chart | ✅ | ✅ (Recharts) | ✅ |
| Closed orders chart | ✅ | ✅ | ✅ |
| Adviced type pie chart | ✅ | ✅ | ✅ |
| Finance summary bar chart | ✅ | ✅ | ✅ |
| Počet všech zakázek | ✅ | ✅ (KPI karta → odkaz) | ✅ |
| Skryté zakázky počet | ✅ | ✅ (KPI karta → odkaz) | ✅ |
| Bez termínu montáže počet | ✅ | ✅ (KPI karta → odkaz) | ✅ |
| Nevalidní zakázky badge | ✅ | ✅ (KPI karta → odkaz) | ✅ |
| **Tabulka nových problémových zakázek** | ✅ | ✅ **Opraveno** | ✅ |
| **Tabulka zákaznických -R zakázek** | ✅ | ✅ **Opraveno** | ✅ |
| -R zakázky: akční tlačítka (Skrýt/Montáž) | ✅ (toggle + buttons) | ✅ (toggle switch + buttons) | ✅ |
| Dynamické mandant volby | ✅ (DB distinct) | ✅ (API `mandant_options`) | ✅ |
| Dynamické year volby | ✅ (DB dates) | ✅ (API `year_options`) | ✅ |

### 5.2 Seznam zakázek (Orders)

| Feature | Django | React | Stav |
|---------|-------|-------|------|
| Server-side DataTables | ✅ (JsonOrders) | Nahrazeno DRF pagination | ✅ |
| Search (order_number, client, team) | ✅ | ✅ | ✅ |
| Status group filtr (open/closed/all) | ✅ | ✅ | ✅ |
| Status filtr | ✅ | ✅ | ✅ |
| Časový rozsah filtr | ✅ | ✅ (from/to dates) | ✅ |
| Hub filtr | ✅ | ✅ | ✅ |
| Mandant filtr | ✅ | ✅ | ✅ |
| OD prefix filtr | ✅ | ✅ | ✅ |
| Invalid-only toggle | ✅ | ✅ | ✅ |
| No-montage-term toggle | — | ✅ (navíc) | ✅ |
| Řazení sloupců | ✅ (DataTables) | ✅ (API ordering params) | ✅ |
| Ikony řádků (PDF, email, fotky, protokol) | ✅ | ✅ (Lucide icons) | ✅ |
| Client incomplete badge | ✅ | ✅ | ✅ |
| Notes preview (zkrácené) | ✅ | ✅ | ✅ |
| Copy to clipboard | ❌ | ✅ (navíc) | ✅ |
| Export do Excelu | ✅ | ✅ | ✅ |
| Pagination | ✅ (DataTables) | ✅ (full paginator) | ✅ |
| **URL params z dashboard KPI** | — | ✅ (`useSearchParams`) | ✅ |

### 5.3 Detail zakázky

| Feature | Django | React | Stav |
|---------|-------|-------|------|
| Order info (číslo, mandant, status, hub, termíny) | ✅ | ✅ | ✅ |
| Client info karta | ✅ | ✅ | ✅ |
| Client edit link | ✅ | ✅ | ✅ |
| Client incomplete warning | ✅ | ✅ | ✅ |
| Team info karta | ✅ | ✅ | ✅ |
| Team inactive warning | ✅ | ✅ | ✅ |
| Team mismatch warning | ✅ | ✅ | ✅ |
| Finance souhrn (výnos/náklad/profit) | ✅ | ✅ | ✅ |
| Finance detail link | ✅ | ✅ | ✅ |
| Articles tabulka | ✅ | ✅ | ✅ |
| Notes sekce | ✅ | ✅ | ✅ |
| Skrýt tlačítko (New only) | ✅ | ✅ (+ confirmation checkbox) | ✅ |
| Smazat tlačítko (Hidden only) | ✅ | ✅ (+ confirmation checkbox) | ✅ |
| Switch to Assembly (New + By_customer) | ✅ | ✅ | ✅ |
| Switch to Realized (Adviced + Delivery) | ✅ | ✅ (+ confirmation checkbox) | ✅ |
| Generate PDF | ✅ | ✅ | ✅ |
| Download PDF link | ✅ | ✅ | ⚠️ Auth problém — viz §8 |
| Send email | ✅ | ✅ | ✅ |
| Email sent info (datum + tým) | ✅ | ✅ | ✅ |
| Back protocol image | ✅ | ✅ (read-only) | ✅ |
| Montage images gallery | ✅ | ✅ (read-only) | ✅ |
| Protocol page link | ✅ | ✅ | ✅ |
| History page link | ✅ | ✅ | ✅ |
| Edit button | ✅ | ✅ | ✅ |
| **Error badge pro Adviced zakázky** | ✅ (`check_order_error_adviced`) | ❌ **CHYBÍ** | 🟧 |
| **Přechod Realized → Billed** | ❌ (není v Django UI) | ❌ | — |
| **Přechod → Canceled** | ❌ (není v Django UI) | ❌ | — |

### 5.4 Formulář zakázky (Create / Edit)

| Feature | Django | React | Stav |
|---------|-------|-------|------|
| Order number pole | ✅ | ✅ (auto-uppercase) | ✅ |
| Mandant select | ✅ | ✅ | ✅ |
| Status select | ✅ | ✅ | ✅ |
| Team type select | ✅ | ✅ | ✅ |
| DistribHub select | ✅ | ✅ | ✅ |
| Team select (podmíněně assembly) | ✅ | ✅ | ✅ |
| Evidence termin | ✅ | ✅ | ✅ |
| Delivery termin | ✅ | ✅ | ✅ |
| Montage termin (podmíněně assembly) | ✅ | ✅ | ✅ |
| Výnos / Náklad | ✅ | ✅ | ✅ |
| Notes | ✅ | ✅ | ✅ |
| Inline klient form (nový) | ✅ | ✅ (mode toggle) | ✅ |
| Výběr existujícího klienta | ✅ (hidden FK) | ✅ (select dropdown) | ✅ |
| Inline articles (add/remove) | ✅ (formset) | ✅ (dynamický array) | ✅ |
| Article: soft delete (edit) | ✅ (formset DELETE) | ✅ (`_delete` flag) | ✅ |
| **Adviced validace (client-side)** | ✅ (server-side clean) | ✅ (klient + server) | ✅ |
| **Client get_or_create** | ✅ | ✅ (`client_data`) | ✅ |
| **`page_size` limit na klienty/týmy** | N/A (vše v select) | ⚠️ `page_size:200` | 🟨 |

### 5.5 Historie zakázky

| Feature | Django | React | Stav |
|---------|-------|-------|------|
| Kombinovaná Order + Article historie | ✅ | ✅ **Opraveno** | ✅ |
| Field-level diff (`diff_against`) | ✅ | ✅ **Opraveno** | ✅ |
| Překlad choice polí (status, team_type) | ✅ | ✅ | ✅ |
| Rozlišení FK názvů | ✅ | ✅ | ✅ |
| History type ikony | ✅ | ✅ | ✅ |

### 5.6 Protocol stránka

| Feature | Django | React | Stav |
|---------|-------|-------|------|
| Generate PDF tlačítko | ✅ | ✅ | ✅ |
| Check/Download PDF | ✅ | ✅ | ⚠️ Auth |
| Send email tlačítko | ✅ | ✅ | ✅ |
| Team mismatch warning | ✅ | ✅ | ✅ |
| Team inactive warning | ✅ | ✅ | ✅ |
| Email sent info | ✅ | ✅ | ✅ |
| PDF info (tým, datum) | ✅ | ✅ | ✅ |
| Back protocol zobrazení | ✅ | ✅ | ✅ |
| Montage images gallery | ✅ | ✅ | ✅ |
| **Montage image upload** | ✅ | ❌ **CHYBÍ** | 🟧 |
| **Team soulad zobrazení** | ✅ (`team_soulad()`) | ❌ **CHYBÍ** | 🟨 |
| **Back protocol upload** (z protocol stránky) | ✅ | ❌ **CHYBÍ** | 🟧 |

### 5.7 Zpětný protokol (externí token-gated stránka)

| Feature | Django | React | Stav |
|---------|-------|-------|------|
| Token validace | ✅ | ❌ **KOMPLETNĚ CHYBÍ** | 🟥 |
| Image upload form | ✅ | ❌ | 🟥 |
| QR code validace | ✅ | ❌ | 🟥 |
| Auto-status → Realized | ✅ | ❌ | 🟥 |
| WebP konverze | ✅ | ❌ | 🟥 |
| Success stránka | ✅ | ❌ | 🟥 |

### 5.8 Týmy

| Feature | Django | React | Stav |
|---------|-------|-------|------|
| Team list | ✅ (tabulka) | ✅ (karty) | ✅ |
| Search | ✅ | ✅ | ✅ |
| Active-only filtr | ✅ | ✅ | ✅ |
| Create team | ✅ | ✅ | ✅ |
| Edit team | ✅ | ✅ | ✅ |
| Team detail | ✅ | ✅ | ✅ |
| Delete team (inactive only) | ✅ | ✅ (API guard ✅) | ✅ |
| Team's orders list na detail | ✅ | ✅ (last 10) | ✅ |
| **Pagination** | ✅ | ❌ **CHYBÍ** | 🟨 |
| **"Nový tým" tlačítko na seznamu** | ✅ | ❌ **CHYBÍ** (route existuje, link ne) | 🟨 |

### 5.9 Zákazníci

| Feature | Django | React | Stav |
|---------|-------|-------|------|
| Client list (tabulka) | ✅ | ✅ | ✅ |
| Search | ✅ | ✅ | ✅ |
| Incomplete-only filtr | ✅ | ✅ | ✅ |
| Client detail | ✅ | ✅ | ✅ |
| Client edit | ✅ | ✅ | ✅ |
| Client orders table | ✅ | ✅ | ✅ |
| Call log formset (inline) | ✅ | ✅ (create via API) | ✅ |
| Existing call logs zobrazení | ✅ | ✅ | ✅ |
| Call log na detail stránce | ✅ | ❌ (jen na edit) | 🟨 |
| Pagination | ✅ | ✅ (prev/next) | ✅ |

### 5.10 Reporty

| Feature | Django | React | Stav |
|---------|-------|-------|------|
| Realized orders tabulka | ✅ (DataTables) | ✅ | ✅ |
| Search | ✅ | ✅ | ✅ |
| Excel export | ✅ | ✅ | ✅ |
| Finance link per order | ✅ | ✅ | ✅ |
| Pagination | ✅ | ✅ | ✅ |
| **Řazení sloupců** | ✅ (DataTables) | ❌ **CHYBÍ** | 🟨 |
| **Pokročilé filtry** (datum, hub, mandant) | ✅ | ❌ **CHYBÍ** | 🟨 |

### 5.11 CSV Import

| Feature | Django | React | Stav |
|---------|-------|-------|------|
| File upload form | ✅ | ✅ | ✅ |
| CSV-only validace | ✅ | ✅ | ✅ |
| Drag-and-drop | ❌ | ✅ (vylepšení) | ✅ |
| Success/error feedback | ✅ | ✅ | ✅ |
| Token info (bot API) | ✅ | ❌ **CHYBÍ** | 🟨 |

### 5.12 Navigace / Sidebar

| Feature | Django (base.html nav) | React (SidebarLayout) | Stav |
|---------|----------------------|----------------------|------|
| Dashboard link | ✅ | ✅ | ✅ |
| Orders link | ✅ | ✅ | ✅ |
| Teams link | ✅ | ✅ | ✅ |
| Clients link | ✅ | ✅ | ✅ |
| Import/Create link | ✅ | ✅ | ✅ |
| Reports link | ✅ | ✅ | ✅ |
| Error badge (invalid Adviced) | ✅ | ✅ | ✅ |
| Theme toggle | ❌ | ✅ (dark/light) | ✅ |
| Mobile responsive | ✅ (CSS) | ✅ (hamburger menu) | ✅ |
| User display | ✅ | ✅ | ✅ |
| Logout | ✅ | ✅ | ✅ |

---

## 6. URL Routing — chybějící trasy

### 6.1 API v1 routy — existující

| Pattern | View | Stav |
|---------|------|------|
| `GET/POST /api/v1/orders/` | OrderViewSet list/create | ✅ |
| `GET/PATCH/DELETE /api/v1/orders/{id}/` | OrderViewSet detail/update/delete | ✅ |
| `POST /api/v1/orders/{id}/hide/` | OrderViewSet.hide | ✅ |
| `POST /api/v1/orders/{id}/switch-to-realized/` | OrderViewSet.switch_to_realized | ✅ |
| `POST /api/v1/orders/{id}/switch-to-assembly/` | OrderViewSet.switch_to_assembly | ✅ |
| `POST /api/v1/orders/{id}/generate-pdf/` | OrderViewSet.generate_pdf | ✅ |
| `GET /api/v1/orders/{id}/download-pdf/` | OrderViewSet.download_pdf | ✅ |
| `POST /api/v1/orders/{id}/send-mail/` | OrderViewSet.send_mail | ✅ |
| `GET /api/v1/orders/{id}/history/` | OrderViewSet.history | ✅ |
| `GET /api/v1/orders/export-excel/` | OrderViewSet.export_excel | ✅ |
| `GET/POST/PATCH/DELETE /api/v1/orders/{id}/articles/` | ArticleViewSet | ✅ |
| `GET/POST/DELETE /api/v1/orders/{id}/images/` | OrderMontazImageViewSet | ✅ |
| `GET/POST/PATCH/DELETE /api/v1/teams/` | TeamViewSet | ✅ |
| `GET/PATCH /api/v1/clients/` | ClientViewSet | ✅ |
| `GET /api/v1/clients/{slug}/orders/` | ClientViewSet.orders | ✅ |
| `GET/POST/PATCH/DELETE /api/v1/finance/revenue/` | FinanceRevenueItemViewSet | ✅ |
| `GET/POST/PATCH/DELETE /api/v1/finance/costs/` | FinanceCostItemViewSet | ✅ |
| `GET/POST /api/v1/call-logs/` | CallLogViewSet | ✅ |
| `GET /api/v1/dashboard/` | DashboardView | ✅ |
| `POST /api/v1/import/` | CSVImportView | ✅ |
| `GET /api/v1/distrib-hubs/` | DistribHubViewSet | ✅ |
| `GET /api/v1/settings/` | AppSettingViewSet | ✅ |
| `GET /api/v1/health/` | HealthCheckView | ✅ |

### 6.2 Chybějící API routy (potřebné pro plnou paritu)

| Chybějící route | Django View | Priorita |
|----------------|-------------|----------|
| `POST /api/v1/orders/{id}/upload-back-protocol/` | `UploadBackProtocolView` | 🟥 **KRITICKÁ** |
| `GET /api/v1/orders/{id}/back-protocol-page/?token=...` | `BackProtocolView` | 🟥 **KRITICKÁ** |
| `POST /api/v1/orders/{id}/upload-protocol/` | `ProtocolUploadView` | 🟧 **VYSOKÁ** |
| `GET /api/v1/orders/{id}/download-montage-zip/` | `DownloadMontageImagesZipView` | 🟨 **STŘEDNÍ** |
| `GET /api/v1/orders/autocomplete-delivery/` | `AutocompleteOrdersByDeliveryGroupView` | ✅ Implementováno |
| Assembly docs page | `AssemblyDocsView` | ⬜ NÍZKÁ |

### 6.3 React Router vs Django URL patterns

| React Route | Django URL | Stav |
|------------|-----------|------|
| `/login` | `/accounts/login/` | ✅ |
| `/dashboard` | `/dashboard/` | ✅ |
| `/orders` | `/orders/` | ✅ |
| `/orders/new` | `/order/create/` | ✅ |
| `/orders/:id` | `/order/:pk/detail/` | ✅ |
| `/orders/:id/edit` | `/order/:pk/update/` | ✅ |
| `/orders/:id/history` | `/order/:pk/history/` | ✅ |
| `/orders/:id/protocol` | `/order/:pk/protocol/` | ✅ |
| `/orders/:id/finance` | `/reports/finance/:pk/` | ✅ |
| `/teams` | `/teams/` | ✅ |
| `/teams/new` | `/teams/create/` | ✅ |
| `/teams/:slug` | `/teams/:slug/detail/` | ✅ |
| `/teams/:slug/edit` | `/teams/:slug/update/` | ✅ |
| `/clients` | `/order/:slug/client_orders/` | ✅ |
| `/clients/:slug` | `/order/:slug/client_orders/` | ✅ |
| `/clients/:slug/edit` | `/order/:slug/client_update_sec/` | ✅ |
| `/import` | `/createpage/` | ✅ |
| `/reports` | `/reports/` | ✅ |
| **CHYBÍ**: back-protocol ext. stránka | `/order/:pk/back_protocol/?token=` | 🟥 |

---

## 7. Původní Django bot-API (API/ app)

Původní `API/` app slouží jako bot-API pro externího automatizačního klienta (script `bot.py`). Používá **Token autentizaci** s expirací (`ExpiringTokenAuthentication`).

### 7.1 Endpointy původního bot-API

| Endpoint | Metoda | View | Účel | Stav v novém API v1 |
|----------|--------|------|------|---------------------|
| `/api/status/` | GET | `ApiStatusView` | Health check | ✅ `/api/v1/health/` |
| `/api/incomplete-customers/` | GET | `IncompleteCustomersView` | Seznam order_numbers neúplných klientů | ⚠️ **Nemá přímý ekvivalent** — lze řešit filtrem `GET /api/v1/orders/?client_incomplete=true` |
| `/api/update-customers/` | POST | `CustomerUpdateView` | Batch update zákazníků podle order_number | ❌ **CHYBÍ** — API v1 nemá batch update endpoint |
| `/api/inc-dopravni-zakazka/` | GET | `ZaterminovanoDopravouView` | Seznam ADVICED + BY_DELIVERY zakázek | ⚠️ Lze řešit filtrem `GET /api/v1/orders/?status=Adviced&team_type=By_delivery_crew` |
| `/api/update-dopzak/` | POST | `RealizujZakazkyView` | Batch realizace dopravních zakázek | ❌ **CHYBÍ** — API v1 nemá batch update endpoint |
| `/api-token-auth/` | POST | `obtain_auth_token` | Token auth (DRF) | ✅ Nahrazeno JWT `/api/v1/auth/login/` |
| `/refresh-token/` | POST | `TriggerTokenRefreshView` | Obnova tokenu pro bota | ✅ JWT refresh `/api/v1/auth/refresh/` |

### 7.2 Bot workflow — stávající

1. Bot (`bot.py`) se autentizuje přes `api-token-auth/` → dostane Token
2. `GET /api/incomplete-customers/` → seznam zakázek s neúplnými klienty
3. Bot doplní údaje z externího zdroje
4. `POST /api/update-customers/` → batch update klientů
5. `GET /api/inc-dopravni-zakazka/` → seznam dopravních zakázek
6. `POST /api/update-dopzak/` → batch realizace dopravních zakázek

### 7.3 Co chybí v API v1 pro bot paritu

| Feature | Stav | Řešení |
|---------|------|--------|
| Batch customer update | ❌ CHYBÍ | Přidat `POST /api/v1/clients/batch-update/` endpoint |
| Batch order realize | ❌ CHYBÍ | Přidat `POST /api/v1/orders/batch-realize/` endpoint |
| Token auth pro bota | ❌ JWT vyžaduje username/heslo | Zvážit API key auth nebo service account JWT |

### 7.4 `ExpiringTokenAuthentication`

```python
# API/auth.py — původní token auth s expirací
class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        token = Token.objects.select_related("user").get(key=key)
        expiration_time = timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
        if token.created + expiration_time < timezone.now():
            token.delete()
            raise AuthenticationFailed("Token expired.")
        return (token.user, token)
```

> V novém API v1 je Token auth nahrazen JWT (simplejwt). Pro bota je potřeba zvážit, zda bude používat JWT nebo zůstane na Token auth (API/ app může koexistovat).

---

## 8. Bezpečnost — Enterprise / GDPR

### 8.1 Autentizace a autorizace

| Aspekt | Django SSR | React + API v1 | Riziko | Doporučení |
|--------|-----------|---------------|--------|------------|
| Auth mechanismus | Session + CSRF | JWT Bearer | 🟨 | JWT je OK, ale potřeba správně nakonfigurovat |
| Token úložiště (FE) | Cookie (httpOnly) | **`localStorage`** | 🟥 **KRITICKÉ** | JWT v localStorage je zranitelný vůči XSS. Přesunout do httpOnly cookie nebo použít BFF pattern |
| Token refresh | Automatický (session) | Manuální refresh flow | 🟨 | Implementovat silent refresh s httpOnly refresh cookie |
| CSRF ochrana | ✅ Django middleware | ❌ Nepotřeba s JWT Bearer | ✅ | OK — JWT Bearer nepotřebuje CSRF |
| Rate limiting (login) | ❌ Žádný | ❌ **ŽÁDNÝ** | 🟥 **KRITICKÉ** | Implementovat throttling na `/api/v1/auth/login/` (max 5 pokusů/min) |
| Brute force ochrana | ✅ fail2ban (nginx) | ❌ **CHYBÍ** na API úrovni | 🟥 | DRF throttling + account lockout po X neúspěšných pokusech |
| Role-based access | ❌ Všichni přihlášení mají vše | ❌ Všichni přihlášení mají vše | 🟧 | Implementovat permission classes (IsAdminUser pro mazání, etc.) |
| Register endpoint | Chráněn LoginRequired | Chráněn `IsAuthenticated` | ✅ | Správně — jen přihlášení mohou registrovat |

### 8.2 GDPR — ochrana osobních údajů

Aplikace zpracovává **osobní údaje zákazníků** (jméno, adresa, telefon, email, PSČ) a **kontaktní údaje montážních týmů**. Podléhá GDPR.

| Požadavek GDPR | Stav | Priorita | Detail |
|---------------|------|----------|--------|
| **Šifrování dat at rest** | ❌ CHYBÍ | 🟥 | SQLite/PostgreSQL data nejsou šifrována. Minimálně produkční DB musí používat encrypted storage |
| **Šifrování dat in transit** | ✅ HTTPS (nginx) | ✅ | TLS/SSL na produkci |
| **Přístupové logy** | ❌ CHYBÍ | 🟥 | Logovat kdo přistupuje k osobním údajům zákazníků (audit trail) |
| **Audit trail změn** | ✅ `simple_history` | ✅ | Historie změn na modelech je funkční |
| **Právo na výmaz** (čl. 17) | ❌ CHYBÍ | 🟥 | Není mechanismus pro anonymizaci/smazání zákazníka a jeho dat |
| **Právo na přístup** (čl. 15) | ❌ CHYBÍ | 🟧 | Není export osobních dat zákazníka |
| **Právo na přenositelnost** (čl. 20) | ❌ CHYBÍ | 🟧 | Není strojově čitelný export dat |
| **Minimalizace dat** | ⚠️ | 🟨 | CallLog ukládá uživatele — OK. Ale API vrací všechna pole bez field-level omezení |
| **Souhlas se zpracováním** | ❌ CHYBÍ | 🟧 | Žádné sledování souhlasu zákazníka |
| **Data retention policy** | ❌ CHYBÍ | 🟧 | Žádné automatické mazání starých dat |
| **DPO kontakt** | ❌ CHYBÍ | 🟨 | Není zaregistrovaný DPO |

### 8.3 API bezpečnost

| Aspekt | Stav | Riziko | Doporučení |
|--------|------|--------|------------|
| **JWT v localStorage** | ✅ Implementováno | 🟥 XSS → krádež tokenu | httpOnly cookie pro refresh token, access v paměti |
| **CORS konfigurace** | `django-cors-headers` | 🟧 | Zkontrolovat `CORS_ALLOWED_ORIGINS` — nesmí být `*` na produkci |
| **Content Security Policy** | ✅ `csp_nonce_middleware.py` | ✅ | CSP middleware existuje |
| **SQL injection** | ✅ Django ORM | ✅ | ORM automaticky escapuje |
| **XSS (backend)** | ✅ Django templates auto-escape | ✅ | Na API straně vrací JSON — OK |
| **XSS (frontend)** | ⚠️ React auto-escape JSX | 🟨 | Zkontrolovat `dangerouslySetInnerHTML` použití — pokud existuje |
| **File upload validace** | ✅ Pouze CSV v ImportPage | 🟧 | Image upload (montáž) validuje jen MIME? Přidat max size + virus scan |
| **PDF download auth** | ❌ `<a href>` bez JWT | 🟥 | Přímý `<a>` link na `/api/v1/orders/{id}/download-pdf/` nesenduje Bearer token. Řešit: fetch + blob URL, nebo signed URL |
| **Back protocol token** | `token_urlsafe(16)` | 🟨 | 16 bajtů je OK, ale token nemá expiraci. Přidat TTL (24h) |
| **Sensitive data v response** | ⚠️ | 🟧 | API vrací telefon a email v list serializátorech — potenciální problém pokud by API bylo veřejné |
| **Pagination limit** | `DEFAULT_PAGINATION_CLASS` | 🟨 | Zkontrolovat max `page_size` — útočník může vyžádat `page_size=10000` |
| **Input sanitization** | Django form clean | 🟨 | Notes pole (TextField) — zkontrolovat, že React nepouží `dangerouslySetInnerHTML` |
| **Session fixation** | N/A (JWT) | ✅ | JWT je stateless |
| **Error message leaking** | ⚠️ | 🟨 | API vrací detailní chybové zprávy — na produkci skrýt stack traces (`DEBUG=False`) |

### 8.4 Šifrování — detailní audit

#### 8.4.1 Šifrování dat in transit (přenos)

| Vrstva | Stav | Detail |
|--------|------|--------|
| **TLS/SSL (nginx)** | ✅ | Let's Encrypt certifikáty, TLSv1.2 + TLSv1.3 |
| **Cipher suites** | ✅ | `ECDHE-ECDSA-AES256-GCM-SHA384`, `ECDHE-RSA-AES256-GCM-SHA384` — silné šifry |
| **HSTS** | ✅ | `max-age=31536000; includeSubDomains; preload` — 1 rok vynucení |
| **HTTP → HTTPS redirect** | ✅ | `return 301 https://...` v `*_80.conf` |
| **HTTP/2** | ✅ | `listen 443 ssl http2` |
| **SSL session tickets** | ✅ | Vypnuto (`ssl_session_tickets off`) — bezpečnější |
| **SSL session cache** | ✅ | `shared:SSL:10m` — výkon bez bezpečnostního rizika |
| **Django SECURE_SSL_REDIRECT** | ✅ | Podmíněno `IS_PRODUCTION and USE_HTTPS` |
| **SESSION_COOKIE_SECURE** | ✅ | Podmíněno `IS_PRODUCTION and USE_HTTPS` |
| **CSRF_COOKIE_SECURE** | ✅ | Podmíněno `IS_PRODUCTION and USE_HTTPS` |
| **Email TLS** | ✅ | `EMAIL_USE_TLS = True`, SMTP port 587 (STARTTLS) |

> ✅ Šifrování in transit je na **výborné úrovni**. Nginx konfigurace odpovídá enterprise standardům.

#### 8.4.2 Šifrování dat at rest (uložení)

| Vrstva | Stav | Detail | Riziko |
|--------|------|--------|--------|
| **Databáze (SQLite/dev)** | ❌ | Nešifrovaný soubor `db.sqlite3` | 🟨 Dev — OK |
| **Databáze (PostgreSQL/prod)** | ❌ | Žádné TDE ani šifrování disku | 🟥 **KRITICKÉ** |
| **Zálohy DB** | ❌ | Zálohy neexistují | 🟥 **KRITICKÉ** |
| **Uložené PDF** | ❌ | `media/stored_pdfs/` — nešifrované na disku | 🟧 Obsahuje osobní údaje |
| **Montážní fotky** | ❌ | `media/` — nešifrované na disku | 🟨 |
| **CSV uploady** | ❌ | `media/uploads/` — nešifrované | 🟧 Obsahuje zákaznická data |
| **Log soubory** | ❌ | `logs/login_failures.log`, `logs/django_error.log` | 🟨 Mohou obsahovat citlivé údaje |
| **`.env` soubor** | ✅ | V `.gitignore` — nenachází se v repo | ✅ |
| **`db.sqlite3`** | ✅ | V `.gitignore` | ✅ |

**Doporučení pro produkci**:
- PostgreSQL: LUKS šifrování disku nebo `pgcrypto` extension pro šifrování citlivých sloupců
- Media soubory: šifrované úložiště (S3 SSE nebo self-managed encryption)
- Zálohy: šifrovaný `pg_dump` (`gpg --symmetric`)

#### 8.4.3 Šifrování PDF přílohy v emailu

Aplikace šifruje PDF montážní protokoly před odesláním emailem (`OOP_emails.py`):

```python
# Utility.encrypt_pdf() — pypdf PdfWriter.encrypt()
writer.encrypt(password)  # AES-128 (pypdf default)
```

| Aspekt | Stav | Riziko | Detail |
|--------|------|--------|--------|
| **Šifrovací metoda** | `pypdf PdfWriter.encrypt()` | ✅ | AES-128 (od pypdf 3.x, dříve RC4) |
| **Heslo pro PDF** | ⚠️ `team.email` | 🟥 **KRITICKÉ** | Heslo = emailová adresa příjemce. Snadno uhodnutelné — email je veřejný údaj |
| **Dočasný soubor** | ✅ | ✅ | `os.remove(encrypted_path)` — smazán po odeslání |
| **Originální PDF na disku** | ⚠️ | 🟧 | `media/stored_pdfs/` — zůstává nešifrovaný |

> 🟥 **Závažný problém**: PDF je "šifrované" heslem = emailová adresa týmu. To není skutečné zabezpečení — kdokoliv znající email (což je veřejný údaj) může PDF otevřít. Pro enterprise úroveň nahradit silným náhodným heslem předaným bezpečným kanálem.

**Doporučení**:
1. Generovat náhodné heslo `secrets.token_urlsafe(16)` pro každý PDF
2. Heslo odeslat odděleným kanálem (SMS, nebo zobrazit v aplikaci po přihlášení)
3. Nebo: použít AES-256 (`writer.encrypt(password, algorithm="AES-256")`)
4. Zvážit S/MIME nebo PGP šifrování celého emailu

#### 8.4.4 Hardcoded credentials — 🟥 KRITICKÉ

V repozitáři se nachází **hardcoded přihlašovací údaje**:

| Soubor | Řádek | Problém |
|--------|-------|---------|
| `bot.py:78` | `password = "b.u.m.b.l.e.b.e.e."` | Heslo pro API bot authentication |
| `bot.py:197` | `password = "Dalzal626Z"` | Heslo pro Selenium login do TMS systému |
| `bot.py:196` | `username = "Dalibor.Zalesak"` | Uživatelské jméno pro TMS |
| `settings.py:145` (zakomentováno) | `"PASSWORD": "Vigokiller2010"` | PostgreSQL heslo v komentáři |

> 🟥 **Toto je absolutně nepřijatelné pro enterprise aplikaci.** Hesla v Git historii jsou permanentní — i po smazání zůstávají v commitech. Je nutné:
> 1. Rotovat **všechna** kompromitovaná hesla OKAMŽITĚ
> 2. Přesunout credentials do `.env` nebo secrets manageru (Vault, AWS Secrets Manager)
> 3. Vyčistit Git historii (`git filter-branch` nebo BFG Repo-Cleaner)
> 4. PostgreSQL heslo v komentáři SMAZAT ze settings.py

#### 8.4.5 Tajné klíče a tokeny

| Položka | Stav | Detail |
|---------|------|--------|
| `SECRET_KEY` | ✅ | Z `.env`, default prázdný string | 
| `EMAIL_HOST_PASSWORD` | ✅ | Z `.env` |
| JWT signing key | ✅ | Používá Django `SECRET_KEY` (simplejwt default) |
| `token_urlsafe(16)` (back protocol) | ⚠️ | 16 bajtů = 128 bitů entropie — dostatečné, ale **chybí TTL** |
| CSP nonce | ✅ | `secrets.token_urlsafe(16)` — per-request |
| API Token (bot) | ⚠️ | DRF `Token` — nesmaže se při expiraci automaticky |

#### 8.4.6 Password hashing

| Aspekt | Stav | Detail |
|--------|------|--------|
| Django PASSWORD_HASHERS | ✅ | Default = PBKDF2 SHA256 (260,000 iterations) |
| 4 validátory hesla | ✅ | UserAttribute, MinLength, Common, Numeric |
| Minimální délka hesla | ⚠️ | Default = 8 znaků — zvážit zvýšení na 12 pro enterprise |

#### 8.4.7 Security headers (nginx)

| Header | Stav | Hodnota |
|--------|------|---------|
| `Strict-Transport-Security` | ✅ | `max-age=31536000; includeSubDomains; preload` |
| `X-Frame-Options` | ✅ | `DENY` |
| `X-Content-Type-Options` | ✅ | `nosniff` |
| `Referrer-Policy` | ✅ | `same-origin` |
| `Cross-Origin-Opener-Policy` | ✅ | `same-origin` |
| `Permissions-Policy` | ✅ | `camera=(self), microphone=(), geolocation=()` |
| **`Content-Security-Policy`** | ⚠️ | CSP middleware existuje ale je **zakomentovaný** v `settings.py` MIDDLEWARE |
| **`X-XSS-Protection`** | ❌ | Chybí — moderní prohlížeče ho respektují |

> ⚠️ CSP middleware (`CSPNonceMiddleware`) je v kódu, ale je zakomentovaný v nastavení. Pro enterprise je CSP povinný.

### 8.5 Infrastrukturní bezpečnost

| Aspekt | Stav | Doporučení |
|--------|------|------------|
| fail2ban konfigurace | ✅ `configs/fail2ban/` | Rozšířit pro API endpointy |
| nginx konfigurace | ✅ `configs/nginx/` | Security headers jsou dobré ✅ |
| SECRET_KEY | `.env` soubor, v `.gitignore` | ✅ |
| Debug mode | `settings.DEBUG` | ⚠️ Zajistit `DEBUG=False` na produkci |
| Allowed hosts | `.env ALLOWED_HOSTS` | ✅ |
| HTTPS redirect | nginx `return 301 https://` | ✅ |
| Database backups | ❌ CHYBÍ | 🟥 Implementovat automatické zálohy |
| **Hardcoded credentials** | 🟥 V `bot.py` + `settings.py` | 🟥 OKAMŽITĚ rotovat a přesunout do `.env` |
| **CSP middleware** | zakomentovaný | 🟧 Odkomentovat v MIDDLEWARE |
| **Media soubory přístup** | nginx `alias` bez auth | 🟧 PDF a fotky přístupné bez autentizace |

### 8.6 Doporučená bezpečnostní architektura (enterprise)

```
┌──────────┐     HTTPS     ┌──────────────┐     ┌──────────────┐
│  React   │ ────────────► │  nginx       │ ──► │  Django/DRF  │
│  SPA     │               │  + HSTS      │     │  API v1      │
│          │ ◄──────────── │  + CSP       │ ◄── │              │
└──────────┘  httpOnly     │  + Rate Limit│     │  JWT (httpOnly│
              cookie       └──────────────┘     │  cookie)     │
              (refresh)           │              └──────┬───────┘
                                  │                     │
                           ┌──────┴──────┐      ┌──────┴───────┐
                           │  fail2ban   │      │  PostgreSQL  │
                           │  WAF rules  │      │  encrypted   │
                           └─────────────┘      │  + backups   │
                                                └──────────────┘
```

**Klíčové kroky**:
1. Refresh token v httpOnly cookie (ne localStorage)
2. Access token pouze v paměti (React context)
3. Rate limiting na nginx + DRF úrovni
4. WAF pravidla pro API endpointy
5. Šifrování DB at rest (PostgreSQL TDE nebo OS-level encryption)
6. Automatické backupy DB (denně) + point-in-time recovery
7. Audit logy pro přístupy k osobním údajům

---

## 9. Opravené bugy a implementace (tato session)

Následující položky byly opraveny/implementovány v aktuální session:

| # | Problém | Oprava | Soubor |
|---|---------|--------|--------|
| 1 | ~~`switch-to-assembly` dělal špatnou věc~~ | ✅ Opraven: kontrola `NEW + BY_CUSTOMER`, nastaví `team_type = BY_ASSEMBLY_CREW` | `api_v1/views.py` |
| 2 | ~~`switch-to-realized` chyběla team_type kontrola~~ | ✅ Opraven: přidána kontrola `BY_DELIVERY_CREW` | `api_v1/views.py` |
| 3 | ~~Order DELETE bez status guardu~~ | ✅ Opraven: custom `destroy()` s kontrolou `HIDDEN` | `api_v1/views.py` |
| 4 | ~~Team DELETE bez active guardu~~ | ✅ Opraven: custom `destroy()` s kontrolou `!active` | `api_v1/views.py` |
| 5 | ~~Client inline creation nefungoval~~ | ✅ Opraven: `OrderWriteSerializer.client_data` + `_resolve_client()` | `api_v1/serializers.py` |
| 6 | ~~Article update destruktivní (bulk delete)~~ | ✅ Opraven: per-article CRUD v `update()` | `api_v1/serializers.py` |
| 7 | ~~CallLog serializer crash (NameError)~~ | ✅ Opraven: přesunut před `ClientDetailSerializer` | `api_v1/serializers.py` |
| 8 | ~~Dashboard chyběly detail tabulky~~ | ✅ Implementovány: `NewIssuesTable` + `CustomerRTable` s akčními tlačítky | `DashboardPage.tsx` |
| 9 | ~~Dashboard KPI jen statické~~ | ✅ Přepracován: klikatelné KPI karty → filtrované zakázky | `DashboardPage.tsx` |
| 10 | ~~Mandant/year options hardcoded~~ | ✅ API vrací dynamické `mandant_options` + `year_options` | `api_v1/views.py` |
| 11 | ~~Historie bez field-level diffs~~ | ✅ API vrací `diff_against` data + Article historii | `api_v1/views.py` |
| 12 | ~~CallLogs nebyly ukládány z ClientForm~~ | ✅ React volá `callLogsApi.create()` sekvenčně | `ClientFormPage.tsx` |
| 13 | ~~OrderWriteSerializer chyběla Adviced validace~~ | ✅ Plná validace (montáž/doprava/zákazník) v `validate()` | `api_v1/serializers.py` |
| 14 | ~~Chyběl `invalid` filtr v OrderFilter~~ | ✅ Přidán `filter_invalid()` | `api_v1/filters.py` |
| 15 | ~~Chyběl `no_montage_term` filtr~~ | ✅ Přidán `filter_no_montage_term()` | `api_v1/filters.py` |
| 16 | ~~OrdersPage nečetl URL params~~ | ✅ Přidáno `useSearchParams` pro dashboard KPI linky | `OrdersPage.tsx` |
| 17 | ~~Login stránka základní~~ | ✅ Redesign s WrenchIcon + gradient | `LoginPage.tsx` |
| 18 | ~~Favicon a titul~~ | ✅ AMS branding | `index.html` |
| 19 | ~~Klienti — prázdná adresa zobrazení~~ | ✅ `hasAddress` guard | `ClientsPage.tsx` |
| 20 | ~~Sidebar branding~~ | ✅ WrenchIcon + "Rhenus HD — AMS" | `SidebarLayout.tsx` |
| 21 | ~~Šifrování osobních údajů zákazníků~~ | ✅ Fernet AES-128 na Client.phone/email/street + data migrace | `encryption.py`, `models.py`, `0005_encrypt_client_fields.py` |
| 22 | ~~GDPR anonymizace zákazníků~~ | ✅ `Client.anonymize()` metoda | `models.py` |
| 23 | ~~GDPR data retention policy~~ | ✅ Model `DataRetentionPolicy` + management command `enforce_data_retention` | `models.py`, `enforce_data_retention.py`, `0006_gdpr_retention_fields.py` |
| 24 | ~~GDPR souhlas se zpracováním~~ | ✅ Pole `consent_given`, `consent_date`, `data_retention_until`, `is_anonymized` na Client | `models.py`, `serializers.py` |

---

## 10. Zbývající problémy a nedostatky

### 10.1 🟥 KRITICKÉ (brání core workflow / bezpečnostní rizika)

| # | Problém | Detail | Soubory |
|---|---------|--------|---------|
| K1 | ~~**Zpětný protokol — kompletně chybí**~~ | ✅ Implementováno: `BackProtocolTokenValidateView` + `BackProtocolUploadView` (token-gated, 24h TTL, QR validace, WebP konverze, auto-status) + `BackProtocolPage.tsx` (veřejná React stránka) | `api_v1/views.py`, `api_v1/urls.py`, `BackProtocolPage.tsx` |
| K2 | ~~**Upload back protocol (interní)**~~ | ✅ Implementováno: `BackProtocolInternalUploadView` API endpoint + upload UI v `ProtocolPage.tsx` | `api_v1/views.py`, `ProtocolPage.tsx` |
| K3 | ~~**JWT v localStorage**~~ | ✅ Migrováno na httpOnly cookies (`CookieJWTAuthentication`). Odstraněn veškerý localStorage token handling z FE | `api_v1/authentication.py`, `AuthContext.tsx`, `client.ts` |
| K4 | ~~**Žádný rate limiting na login**~~ | ✅ DRF throttling: `anon: 30/min`, `user: 120/min`, `login: 5/min` (ScopedRateThrottle) | `api_v1/views.py`, `AMS/settings.py` |
| K5 | ~~**PDF download neposílá auth**~~ | ✅ Nahrazeno authenticated fetch přes axios (`ordersApi.downloadPdf()`) | `OrderDetailPage.tsx`, `ProtocolPage.tsx` |
| K6 | ~~**GDPR — právo na výmaz**~~ | ✅ Implementováno: `Client.anonymize()` metoda + management command | `models.py`, `enforce_data_retention.py` |
| K7 | ~~**GDPR — přístupové logy**~~ | ✅ Implementováno: `GDPRAuditMiddleware` loguje přístup k citlivým endpointům do `logs/gdpr_audit.log` | `middleware/gdpr_audit_middleware.py`, `settings.py` |
| K8 | ~~**Šifrování dat at rest**~~ | ✅ Fernet AES-128 na Client.phone/email/street | `encryption.py`, `models.py` |
| K9 | ~~**Database backups**~~ | ✅ Management command `backup_database` (SQLite copy / pg_dump, --keep days retention, auto-cleanup) | `management/commands/backup_database.py` |
| K10 | ~~**Hardcoded credentials v repozitáři**~~ | ✅ Nahrazeno env vars (`RHEMOVE_USERNAME/PASSWORD`, `RHENUS_TMS_USERNAME/PASSWORD`). Komentovaný DB password odstraněn. ⚠️ Stará hesla zůstávají v Git historii — doporučen BFG cleanup | `bot.py`, `settings.py` |
| K11 | ~~**PDF heslo = email týmu**~~ | ✅ Nahrazeno `generate_pdf_password()` — 12-char random alphanumeric, heslo zahrnuto v emailu | `OOP_emails.py` |
| K12 | ~~**CSP middleware vypnutý**~~ | ✅ CSP middleware povolený, production-strict / dev-permissive (Vite HMR support) | `csp_nonce_middleware.py`, `settings.py` |
| K13 | ~~**SECRET_KEY default prázdný**~~ | ✅ RuntimeError pokud prázdný v produkci. Dev fallback `django-insecure-dev-only-NOT-FOR-PRODUCTION`. Stejný guard pro FIELD_ENCRYPTION_KEY | `settings.py` |

### 10.2 🟧 VYSOKÉ (chybí významná funkčnost)

| # | Problém | Detail |
|---|---------|--------|
| V1 | **Montage image upload UI** | API endpoint existuje (`POST /orders/{id}/images/`), ale React UI pro upload neexistuje |
| V2 | **Montage images ZIP download** | `DownloadMontageImagesZipView` ekvivalent chybí |
| V3 | **Adviced validace: client.incomplete** | Django form kontroluje `client.incomplete`, React ani API ne |
| V4 | **Per-order error badge na detailu** | Django `check_order_error_adviced()` zobrazuje varování na detail stránce. React ne |
| V5 | **Team soulad na protocol stránce** | Django `team_soulad()` kontroluje shodu PDF týmu s aktuálním. React nezobrazuje |
| V6 | **Bot API batch endpointy** | `update-customers` a `update-dopzak` batch operace chybí v API v1 |
| V7 | **Role-based access control** | Všichni přihlášení uživatelé mají plný přístup — žádné role/permissions |
| V8 | **GDPR — právo na přístup a přenositelnost** | Chybí export osobních dat zákazníka |

### 10.3 🟨 STŘEDNÍ (chybějící features a vylepšení)

| # | Problém | Detail |
|---|---------|--------|
| S1 | ~~**TeamsPage pagination**~~ | ✅ Přidáno prev/next pagination UI pod card grid |
| S2 | ~~**TeamsPage "Nový tým" tlačítko**~~ | ✅ Přidán `<Link to="/teams/new">` s ikonou Plus v headeru |
| S3 | ~~**ReportsPage řazení sloupců**~~ | ✅ Sortable columns: order_number, mandant, client, team, termíny |
| S4 | ~~**ReportsPage pokročilé filtry**~~ | ✅ Datum od/do, hub, mandant filtry (collapsible bar) |
| S5 | ~~**zip_code 5-char validace**~~ | ✅ Model `Client.save()` + serializer `validate_zip_code` + frontend pattern |
| S6 | ~~**Team name slug unikátnost validace**~~ | ✅ `TeamDetailSerializer.validate_name()` checks slug uniqueness |
| S7 | ~~**Finance — editace existujících položek**~~ | ✅ Inline editace na FinancePage (Pencil icon → edit mode → save/cancel) |
| S8 | ~~**Call log — smazání**~~ | ✅ `callLogsApi.delete()` + Trash2 button na ClientFormPage |
| S9 | ~~**Call log na ClientDetailPage**~~ | ✅ Sekce call logů na ClientDetailPage (read-only tabulka) |
| S10 | ~~**Import stránka — token info**~~ | ✅ JWT bot info card na ImportPage (`BotTokenInfoView` → SIMPLE_JWT config) |
| S11 | ~~**Assembly docs stránka**~~ | ✅ `AssemblyDocsPage.tsx` — galerie, back protocol, ZIP stažení |
| S12 | ~~**page_size=200 limit**~~ | ✅ `SearchableSelect` komponenta s debounced server-side search (page_size:50) |
| S13 | ~~**Back protocol token TTL**~~ | ✅ Token platí do 24h po `montage_termin` (fallback 48h od vytvoření pokud termín není nastaven) — `_is_back_protocol_token_expired()` helper |
| S14 | ~~**Pagination max page_size**~~ | ✅ `StandardPagination.max_page_size = 200` již nastaveno |
| S15 | ~~**CORS na produkci**~~ | ✅ `CORS_ALLOWED_ORIGINS` z env variable, `CORS_ALLOW_CREDENTIALS=True`, žádný wildcard |
| S16 | ~~**OD_CHOICES pojmenované obchody**~~ | ✅ OD_OPTIONS s názvy: „701 — OD Stodůlky" etc. |
| S17 | ~~**GDPR — souhlas se zpracováním**~~ | ✅ Přidána pole `consent_given`, `consent_date` na Client |
| S18 | ~~**GDPR — data retention policy**~~ | ✅ Model `DataRetentionPolicy` + `enforce_data_retention` command |
| S19 | ~~**Sensitive data v list responses**~~ | ✅ `ClientListSerializer` maskuje phone a email (SerializerMethodField) |

### 10.4 ⬜ NÍZKÉ (kosmetické / nice-to-have)

| # | Problém |
|---|---------|
| N1 | Autocomplete by delivery group |
| N2 | Standalone PDF view pro mandanty |
| N3 | Register stránka (endpoint existuje, route ne) |
| N4 | 404 stránka (vše redirectuje na /dashboard) |
| N5 | Filtr state persistence v URL (OrdersPage write-back) |
| N6 | ~~**BUG — Artikly: počet × poznámka overlap.**~~ ✅ Opraveno: `min-width: 4rem` + `grid-template-columns: 1fr 60px 2fr auto` |

---

## Souhrnná statistika

| Kategorie | Počet |
|-----------|-------|
| Opravené bugy (celkem) | **63** |
| Zbývající KRITICKÉ | **0** (vše implementováno ✅) |
| Zbývající VYSOKÉ | **0** (vše implementováno ✅) |
| Zbývající STŘEDNÍ | **0** (vše implementováno ✅) |
| Zbývající NÍZKÉ | **0** (4 implementovány ✅, 1 přeskočena ⏭️) |
| Features s plnou paritou | ~**99 %** |

React frontend pokrývá přibližně **99 %** funkčnosti původní Django SSR aplikace. Jediná vynechaná položka je N3 (register stránka) — správa uživatelů je řešena přes Django admin.

✅ **Všechny KRITICKÉ položky (K1–K13) byly implementovány.**

✅ **Všechny VYSOKÉ položky (V1–V9) byly implementovány.**

✅ **Všechny STŘEDNÍ položky (S1–S19) byly implementovány.**

✅ **Všechny NÍZKÉ položky (N1–N6) byly vyřešeny (N3 přeskočena záměrně).**

### 10.5 🔧 Opravené bugy (post-implementace)

| # | Bug | Příčina | Fix |
|---|-----|---------|-----|
| B1 | **Infinite login page reload loop** | `client.ts` interceptor při selhání refresh volal `window.location.href = "/login"` → full page reload → `AuthProvider.fetchUser()` → 401 → refresh → fail → redirect → smyčka | Odstraněn hard redirect z interceptoru. Auth endpointy (`/auth/me/`, `/auth/login/`, `/auth/refresh/`) vyloučeny z retry logiky. Přidán refresh queue pro paralelní requesty. `AuthContext` + `ProtectedRoute` řeší přesměrování přes React Router bez reload. |

| B2 | **Login úspěšný ale cookies se nepošlou zpět** | `client.ts` defaultní `API_BASE_URL = "http://127.0.0.1:8000"` obcházel Vite proxy → cross-origin requesty (`localhost:5173` → `127.0.0.1:8000`) → browser odmítl poslat `SameSite=Lax` cookies na cross-site AJAX → `/auth/me/` vždy 401 | Default `API_BASE_URL` změněn na `""` (same-origin). Requesty nyní jdou přes Vite proxy (`localhost:5173/api/...` → `127.0.0.1:8000/api/...`) → cookies fungují. Stejná oprava v `BackProtocolPage.tsx`. |

| B3 | **Login úspěšný ale nenaviguje na dashboard** | 1) `AuthContext.login()` používal `fetchUser()` který tiše políkal chyby (`catch → setUser(null)`) → uživatel nedostal zpětnou vazbu. 2) `LoginPage` volal `navigate("/dashboard")` imperativně — race condition: React ještě nestacil commitnout `setUser(data)` → `ProtectedRoute` viděl `user=null` → redirect zpět na `/login`. | `AuthContext.login()` volá `authApi.me()` přímo (chyby propagují). `LoginPage` naviguje přes `useEffect([user])` — navigace proběhne až po React state commit. |

| B4 | **Vite `.env` přepisuje API_BASE_URL na cross-origin** | `frontend/.env` obsahoval `VITE_API_URL=http://127.0.0.1:8000` → Vite injektoval env var do `import.meta.env` → override B2 fixu → requesty nadále šly přímo na backend (cross-origin) → `SameSite=Lax` cookies blokované prohlížečem → `me/` 401 → „Neplatné přihlašovací údaje." | `.env` opraven: `VITE_API_URL=` (prázdný) → `baseURL = "/api/v1"` (same-origin, Vite proxy). Přidán komentář vysvětlující proč musí být prázdný v dev mode. |

| B5 | **PDF generování padá — špatná signatura volání** | `api_v1/views.py` `generate_pdf` akce volala `generator_class(pk=order.pk)` → `TypeError: PdfGenerator.__init__() got an unexpected keyword argument 'pk'`. Poté `.generate_pdf_protocol()` a `.save_pdf_protocol_to_db()` bez parametrů. Mrtvý `pdf_gen_classes` dict nikdy nepoužitý. | Opraveno na správný vzor z Django SSR: `generator_class()` → `.generate_pdf_protocol(model=order)` → `.save_pdf_protocol_to_db(model=order, pdf=pdf_io)`. Odstraněn mrtvý kód. |

| B6 | **Toast notifikace jsou fixně nahoře a nejsou vidět** | `.toast-container` měl `position: fixed; top: 0` → překrýval obsah, nereagoval na scroll, uživatel zprávy snadno přehlédl. | Toast container změněn na `position: sticky; top: 0` vykreslený **nad** children v `ToastProvider` → zprávy seshora tlačí obsah dolů. Přidána slide-down animace a `border-bottom`. |

| B7 | **Interní upload zpětného protokolu — stale DB záznam** | `BackProtocolInternalUploadView`: `save_protocol_object()` commitne DB záznam → `validate_barcode()` selže → smaže fyzický soubor (`save=False`) ale DB záznam zůstane → `has_back_protocol: True` s neexistujícím souborem → 404 broken image. Vnitřní (admin) upload navíc nepotřebuje QR validaci. | **Interní upload**: odstraněna QR validace (admin ví co nahrává) + odstraněn `update_order_status()` (jen ukládá soubor). **Externí upload**: přidán cleanup — při selhání QR validace se smaže i DB záznam (`protocol_obj.delete()`). Vyčištěn existující stale záznam pro `703811284500499915-O`. |

| B8 | **Nekonzistentní mezery mezi sekcemi na ProtocolPage** | `.detail-card` bez `margin-bottom`, `.detail-card--full` měl `margin-bottom: 0.75rem`. Karty ve `.protocol-page` neměly žádný gap. | `.protocol-page` přidán `display: flex; flex-direction: column; gap: 0.75rem`. Odstraněn přebytečný `margin-bottom` z `.detail-card--full`. |

| B9 | **Email odesílání selhává — `from_email=None`** | `OOP_emails.py` `Config.from_email` používal `os.getenv("EMAIL_HOST_USER")` → `None` protože `.env` neobsahoval email credentials (ty jsou v `.env_rhemove`). `settings.py` načítal jen `.env`, ne `.env_rhemove`. Django `EmailMultiAlternatives(from_email=None)` → SMTP odmítl. | `settings.py`: přidáno `load_dotenv(".env_rhemove")` po hlavním `.env`. `OOP_emails.py`: `Config.from_email` nyní bere `settings.DEFAULT_FROM_EMAIL` (= `Rhenus HD — AMS <montaze@rhemove.cz>`) místo `os.getenv`. Test email úspěšně odeslán. |

| B10 | **Duplikátní tlačítko „Montážní protokol“ na OrderDetailPage** | Tlačítko se zobrazovalo dvakrát — jednou v `action-bar` sekci a podruhé v oddíle „Protokol a komunikace“. | Odebrán button z `action-bar`. Zůstává jen v sekci „Protokol a komunikace“. |

| B11 | **Chybějící mezera mezi Artikly a Protokol sekcemi** | `detail-card--full` elementy mimo `.detail-grid` neměly žádný vertikální spacing. | Přidáno CSS `.detail-card--full + .detail-card--full { margin-top: 1rem }`. |

| B12 | **Špatné zarovnání sloupců v historii zakázky** | `.history-item__changes` tabulka neměla fixní šířky sloupců — Pole/Původní/Nová se posouvaly podle obsahu. | `table-layout: fixed`, fixní šířky: Pole 20%, Původní 40%, Nová 40%. |

| B13 | **Sidebar footer není zarovnaný ke spodnímu okraji** | `.sidebar__footer` měl `margin-top: 1em` místo pružného zarovnání — při krátké navigaci zbylo velké prázdné místo nad footerem. | Změněno na `margin-top: auto` — flexbox tlačí footer vždy ke spodnímu okraji sidebaru. |

| B14 | **Správa uživatelů — nelze přidat nového uživatele** | `UserAdminViewSet` povoloval pouze GET+PATCH — admin neměl možnost vytvořit účet nového uživatele (tlačítko i endpoint chyběly). | Přidán `UserAdminCreateSerializer` (username, heslo, role, validace duplicit/shody hesel), `POST` povolen na ViewSetu, nová stránka `UserCreatePage.tsx`, route `/users/new`, tlačítko „Přidat uživatele“ na `UsersPage`. |

| B15 | **Dashboard — duplicitní mandanti ve filtru** | `values_list("mandant", flat=True).distinct()` v SQLite vracelo duplicity (ORM bug). | Použit `set()` pro deduplikaci na backendu + `[...new Set()]` jako pojistka na frontendu. |

| B16 | **Dashboard — prázdná data při výchozím načtení** | Výchozí stav filtru rok = aktuální rok (2026), ale data obsahují jen 2024–2025. Grafy byly prázdné. | Výchozí hodnota `year` změněna na `""` (Vše) — dashboard ukáže všechna data. |

| B17 | **Dashboard — chybějící nadpisy filtrů a špatné pořadí** | Filtry byly bez labelů a měsíc byl před rokem — neintutivní UX. | Každý filtr zabalen do `.filter-group` s `<label>`. Pořadí: Rok → Měsíc → Mandant → Hub. |

| B18 | **Sidebar footer — obsah není vycentrovaný** | Footer elementy (theme toggle, uživatel, logout) byly zarovnané doleva. | Přidáno `display: flex; flex-direction: column; align-items: center; text-align: center` na `.sidebar__footer` a `justify-content: center` na potomky. |

---

## 11. TODO — seřazeno dle priority

### 🟥 KRITICKÉ — musí být hotové před produkcí

- [x] **TODO-K1**: ~~Implementovat externí zpětný protokol~~ ✅ `BackProtocolUploadView` + `BackProtocolPage.tsx`

- [x] **TODO-K2**: ~~Implementovat interní upload zpětného protokolu~~ ✅ `BackProtocolInternalUploadView` + upload UI v `ProtocolPage.tsx`

- [x] **TODO-K3**: ~~Opravit JWT token uložení~~ ✅ httpOnly cookies (`CookieJWTAuthentication`)

- [x] **TODO-K4**: ~~Implementovat rate limiting na login~~ ✅ DRF throttling: login 5/min, user 120/min, anon 30/min

- [x] **TODO-K5**: ~~Opravit PDF download autentizaci~~ ✅ Authenticated fetch přes axios

- [x] **TODO-K6**: GDPR — právo na výmaz (anonymizace zákazníků)
  - ✅ Implementováno: `Client.anonymize()` metoda + management command `enforce_data_retention`

- [x] **TODO-K7**: ~~GDPR — přístupové logy~~ ✅ `GDPRAuditMiddleware` → `logs/gdpr_audit.log`

- [x] **TODO-K8**: Šifrování osobních údajů zákazníků
  - ✅ Fernet AES-128-CBC + HMAC-SHA256 (`encryption.py`)
  - Šifrovaná pole: `Client.phone`, `Client.email`, `Client.street`
  - Transparentní šifrování/dešifrování přes custom Django fields
  - Klíč v `.env` (`FIELD_ENCRYPTION_KEY`), ne v kódu
  - Data migrace zašifrovala existující záznamy

- [x] **TODO-K9**: ~~Automatické zálohy databáze~~ ✅ Management command `backup_database`

- [x] **TODO-K10**: ~~Odstranit hardcoded credentials~~ ✅ Nahrazeno env vars. ⚠️ Git historie vyžaduje BFG cleanup

- [x] **TODO-K11**: ~~Opravit PDF šifrování~~ ✅ `generate_pdf_password()` — 12-char random, heslo v emailu

- [x] **TODO-K12**: ~~Aktivovat CSP middleware~~ ✅ Production-strict / dev-permissive

- [x] **TODO-K13**: ~~Opravit SECRET_KEY fallback~~ ✅ RuntimeError v produkci, dev fallback

### 🟧 VYSOKÉ — významná funkčnost pro denní provoz

- [x] **TODO-V1**: ~~Přidat UI pro upload montážních fotek~~ ✅
  - Upload formulář s multi-file výběrem na `ProtocolPage.tsx`
  - Smazání fotek s overlay tlačítkem
  - WebP konverze v `OrderMontazImageViewSet.perform_create()`

- [x] **TODO-V2**: ~~Přidat ZIP download montážních fotek~~ ✅
  - `download_montage_zip` action na `OrderViewSet` (in-memory ZIP)
  - Download tlačítko „Stáhnout ZIP" na `ProtocolPage.tsx`

- [x] **TODO-V3**: ~~Přidat validaci `client.incomplete` v Adviced stavu~~ ✅
  - `OrderWriteSerializer.validate()`: `elif client_val and client_val.incomplete → errs`
  - React `validateAdviced()`: lookup klienta z `clients` query, kontrola `incomplete`

- [x] **TODO-V4**: ~~Přidat per-order error badge na detail stránku~~ ✅
  - Varování „E-mail zákazníkovi nebyl dosud odeslán" na `OrderDetailPage.tsx`
  - Team mismatch a team inactive varování již existovaly
  - Sidebar error badge z `invalid_count` (dashboard endpoint) už fungoval

- [x] **TODO-V5**: ~~Přidat team soulad na protocol stránku~~ ✅
  - Již implementováno: `teamMismatch` v `ProtocolPage.tsx` (PDF team vs aktuální tým)
  - Alert varování + „nesoulad!" text u odeslaného emailu

- [x] **TODO-V6**: ~~Přidat bot API batch endpointy do API v1~~ ✅
  - `GET /api/v1/clients/incomplete-orders/` — seznam order_numbers s nekompletními klienty
  - `POST /api/v1/clients/batch-update/` — batch aktualizace klientů
  - `GET /api/v1/orders/adviced-delivery/` — seznam zatermínovaných dopravních zakázek
  - `POST /api/v1/orders/batch-realize/` — batch realizace
  - `bot.py` přepojen na JWT (httpOnly cookies) přes `requests.Session()`

- [x] **TODO-V7**: ~~Implementovat role-based access control (RBAC)~~ ✅
  - Role (Django Groups): Admin, Manager, Operator, ReadOnly
  - `api_v1/permissions.py`: `RBACPermission` (default), `IsAdminRole`, `IsManagerOrAbove`, `IsOperatorOrAbove`
  - `UserSerializer` vrací `role` field, `useRole()` hook v Reactu
  - Management command `setup_rbac_groups`, user `zaled99` → Admin
  - Sidebar zobrazuje role badge

- [x] **TODO-V8**: ~~GDPR — export osobních dat zákazníka~~ ✅
  - `GET /api/v1/clients/{slug}/export-data/` → JSON (kontakty, zakázky, call logy)
  - React: tlačítko „Export dat" na `ClientDetailPage.tsx` → stažení `.json`

### 🟨 STŘEDNÍ — kvalita a UX vylepšení

- [x] **TODO-S1**: ✅ Přidáno prev/next pagination UI na TeamsPage (počet stránek z `data.count`)

- [x] **TODO-S2**: ✅ Přidán `<Link to="/teams/new">` button s Plus ikonou v headeru TeamsPage

- [x] **TODO-S3**: ✅ Sortable columns na ReportsPage (order_number, mandant, client, team, termíny) + `ordering` query param

- [x] **TODO-S4**: ✅ Collapsible advanced filter bar na ReportsPage (datum od/do, hub select, mandant select)

- [x] **TODO-S5**: ✅ Validace již existovala: model `Client.save()` check + serializer `validate_zip_code` + frontend `pattern`

- [x] **TODO-S6**: ✅ `TeamDetailSerializer.validate_name()` — generuje slug, kontroluje unikátnost přes `Team.objects.filter(slug=…)`

- [x] **TODO-S7**: ✅ Inline editace na FinancePage — Pencil icon → edit mode (input desc + amount) → Save/Cancel

- [x] **TODO-S8**: ✅ `callLogsApi.delete()` + Trash2 button s confirm dialogem na ClientFormPage

- [x] **TODO-S9**: ✅ Call logy tabulka na ClientDetailPage (status icon, note, author, date) — read-only

- [x] **TODO-S10**: ✅ JWT bot info card na ImportPage — `BotTokenInfoView` vrací SIMPLE_JWT config (lifetimes, last_login, is_active)

- [x] **TODO-S11**: ✅ `AssemblyDocsPage.tsx` — galerie montážních fotek, back protocol download, detail montáže, ZIP stažení

- [x] **TODO-S12**: ✅ `SearchableSelect` komponenta s debounced server-side search (300ms), page_size:50, initialOptions z preloadu

- [x] **TODO-S13**: ✅ Token platí do 24h po `montage_termin` (fallback 48h) — `_is_back_protocol_token_expired()` v `api_v1/views.py`

- [x] **TODO-S14**: ✅ `StandardPagination.max_page_size = 200` — již nastaveno, chrání proti `?page_size=99999`

- [x] **TODO-S15**: ✅ `CORS_ALLOWED_ORIGINS` z env variable (`ALLOWED_CORS`), `CORS_ALLOW_CREDENTIALS=True`, žádný wildcard `*`

- [x] **TODO-S16**: ✅ `OD_OPTIONS` v OrdersPage aktualizovány: „701 — OD Stodůlky", „703 — OD Černý Most", etc.

- [x] **TODO-S17**: ✅ GDPR — `consent_given`, `consent_date` na Client model + serializer

- [x] **TODO-S18**: ✅ GDPR — `DataRetentionPolicy` model + `enforce_data_retention` command + `data_retention_until`, `is_anonymized` pole

- [x] **TODO-S19**: ✅ `ClientListSerializer` maskuje phone a email přes `SerializerMethodField` (_mask_phone, _mask_email). Detail endpoint vrací plná data.

### ✅ NÍZKÉ — kosmetické a nice-to-have

- [x] **TODO-N1**: ✅ `autocomplete_delivery` action na `OrderViewSet` + team_type filtr (🔧/🚚/👤) v OrdersPage
- [x] **TODO-N2**: ✅ `view_pdf` action (`as_attachment=False`) + `PdfViewerPage.tsx` s `<iframe>` a download tlačítkem
- [x] **TODO-N3**: ⏭️ Přeskočeno — správa uživatelů přes Django admin (bez registrace)
- [x] **TODO-N4**: ✅ `NotFoundPage.tsx` — stylovaná 404 stránka + catch-all `<Route path="*">`
- [x] **TODO-N5**: ✅ Veškerý filtr/stránkovací state v `OrdersPage` odvozen z `useSearchParams` — URL persistuje filtry, řazení, stránku i page_size

---

*Konec audit reportu. Poslední aktualizace: 2. 3. 2026 — všechny kategorie K/V/S/N dokončeny (N3 přeskočena záměrně)*