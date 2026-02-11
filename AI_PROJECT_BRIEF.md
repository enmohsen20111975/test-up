# EngiSuite Analytics Pro - AI Project Brief

Audience: LLM/AI model
Goal: Provide a compact but deep overview of the project so an AI assistant can understand context, data flow, and key modules quickly.

## 1) What this project is
EngiSuite Analytics Pro is a full-stack engineering platform that combines:
- Engineering calculators (electrical, mechanical, civil)
- Data analytics (file upload, query builder, summaries, reports)
- AI assistant (explain calculations, analyze data, generate reports, chat)
- Subscription and payments (Paymob)
- Multi-language frontend (Arabic default, English, French)

The frontend is static HTML/CSS/JS served directly by FastAPI. The backend is a FastAPI app with SQLAlchemy and Google OAuth login.

## 2) High-level architecture
- Frontend: static pages in frontend/, shared JS services in frontend/shared/js/.
- Backend: FastAPI app in backend/, with routers for auth, calculators, analytics, AI, and payments.
- Database: SQLAlchemy, default SQLite (users.db) with a User table.
- AI providers: DeepSeek is primary, Qwen is fallback (both OpenAI-compatible clients).
- Localization: frontend JSON bundles, backend error translation for API messages.

### Core data flow (typical)
1) User logs in via Google OAuth from frontend.
2) Backend issues JWT, stored in cookie and/or localStorage.
3) Frontend calls API routes with Bearer token.
4) Backend performs calculation / analytics / AI and returns JSON.
5) Frontend renders results and manages UI state.

## 3) Backend modules and functions

### backend/main.py
- Initializes FastAPI app and CORS.
- Loads translations for backend error messages.
- Includes routers:
  - auth.router
  - auth.google_oauth_routes
  - calculators.router
  - payments.router
- Mounts frontend/ as static content at root.

### backend/config.py
- Settings for database, JWT, AI keys, Paymob/Stripe, environment flags.

### backend/database.py
- SQLAlchemy engine, SessionLocal, Base.
- get_db() generator for dependency injection.

### Auth
- auth/models.py
  - User model: email, google_id, name, picture, tier, credits_remaining, login stats.
- auth/router.py
  - create_access_token(data, expires_delta)
  - get_current_user() from Bearer or cookie
  - GET /auth/me
  - POST /auth/logout
- auth/google_oauth_routes.py
  - /auth/google/login redirects to Google OAuth
  - /auth/callback exchanges code for token, stores user, sets cookie
  - /auth/check verifies session

### Calculators
- calculators/router.py
  - GET /calculators/{discipline} returns list of calculator IDs
  - POST /calculators/{type}/calculate routes to service methods by prefix
- calculators/services/electrical.py
  - load_calculation, cable_sizing, breaker_selection, transformer_sizing, power_factor_correction, and more
- calculators/services/mechanical.py
  - hvac_load, pump_sizing, pipe_sizing, duct_sizing, heat_transfer, chiller_selection, and more
- calculators/services/civil.py
  - concrete_volume, steel_weight, beam_load, column_design, foundation_area, and more

### Analytics
- analytics/router.py
  - POST /analytics/upload
  - POST /analytics/query
  - POST /analytics/summary
  - POST /analytics/distribution
  - GET /analytics/templates
- analytics/upload.py
  - FileUploadService.process_file() for CSV/XLSX/JSON
- analytics/query_builder.py
  - QueryBuilder.execute_query() supports filters, group_by, aggregates, order_by, calculated fields
  - get_data_summary()
  - get_column_distribution()
- analytics/report_generator.py
  - ReportGenerator.generate_pdf() uses pdfkit

### AI
- ai/router.py
  - POST /ai/explain, /ai/analyze, /ai/report, /ai/chat
  - get_ai_response() tries DeepSeek then Qwen
- ai/deepseek_client.py and ai/qwen_client.py
  - explain_calculation, analyze_data, generate_report, chat

### Payments
- payments/router.py
  - GET /payments/plans
  - POST /payments/initiate
  - POST /payments/subscribe
  - POST /payments/webhook
  - GET /payments/status/{order_id}
- payments/paymob_client.py
  - authenticate(), register_order(), get_payment_key(), verify_webhook(), process_callback()

## 4) Frontend modules and functions

### Pages (HTML)
- index.html (landing)
- login.html (Google OAuth login)
- register.html (redirects to login)
- dashboard.html (post-login overview)
- calculators.html (grid of calculators)
- analytics.html (query builder, upload, analysis)
- reports.html (report list)
- ai-assistant.html (chat UI)
- profile.html (user profile)
- visual-workflow.html (visual workflow UI for calculators)

### Shared JS services
- shared/js/auth.js
  - getToken, setToken, removeToken, loginWithGoogle, logout, getCurrentUser
- shared/js/i18n.js
  - loadTranslations, applyTranslations, setLanguage
  - handles lang, dir, and dispatches i18n:changed event
- shared/js/calculators.js
  - CalculatorService.calculate()
  - calculator metadata for grid and workflow
  - renderCalculators(), openCalculator(), viewCalculatorInfo()
- shared/js/analytics-service.js
  - uploadFile(), executeQuery(), getDataSummary(), getColumnDistribution(), getAnalyticsTemplates(), generateReport()
- shared/js/ai-service.js
  - explainCalculation(), analyzeData(), generateReport(), chat()
- shared/js/payment.js
  - getSubscriptionPlans(), initiatePayment(), subscribeToPlan(), getPaymentStatus(), createPaymentButton()

### Localization
- shared/js/i18n/*.json includes Arabic, English, French
- Arabic is default, RTL supported

## 5) Key API endpoints (summary)
- Auth:
  - GET /auth/me
  - POST /auth/logout
  - GET /auth/google/login
  - GET /auth/callback
  - GET /auth/check
- Calculators:
  - GET /calculators/{discipline}
  - POST /calculators/{type}/calculate
- Analytics:
  - POST /analytics/upload
  - POST /analytics/query
  - POST /analytics/summary
  - POST /analytics/distribution
  - GET /analytics/templates
- AI:
  - POST /ai/explain
  - POST /ai/analyze
  - POST /ai/report
  - POST /ai/chat
- Payments:
  - GET /payments/plans
  - POST /payments/initiate
  - POST /payments/subscribe
  - POST /payments/webhook
  - GET /payments/status/{order_id}

## 6) Notes and assumptions for AI use
- Backend analytics and AI routers are present, but check main.py to confirm if included.
- Frontend uses JWT in localStorage and cookie from Google OAuth.
- Some pages use mock data in JS for demo UI rendering.
- i18n uses data-i18n attributes for text and attributes.

## 7) Typical user flows
- Login: login.html -> Google OAuth -> JWT cookie -> dashboard.html
- Calculators: calculators.html -> pick calc -> POST /calculators/{type}/calculate
- Analytics: analytics.html -> upload file -> POST /analytics/upload -> build query -> POST /analytics/query
- AI: ai-assistant.html -> POST /ai/chat
- Payments: frontend payment service -> /payments/initiate or /payments/subscribe
