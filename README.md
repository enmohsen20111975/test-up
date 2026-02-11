# EngiSuite Analytics Pro

**Unified SaaS platform for engineering calculations and data analysis**

## Overview

EngiSuite Analytics Pro is a comprehensive SaaS platform that combines:

- **50 Engineering Calculators** (Electrical, Mechanical, Civil)
- **Data Analysis Module** (Excel/CSV/JSON upload, query builder, dashboarding)
- **AI Assistant** with DeepSeek-V3 primary and Qwen-Max fallback
- **Professional Report Generation**
- **Modern Arabic UI**

## Tech Stack

### Frontend
- HTML5 + Vanilla JavaScript
- Font Awesome 6.0.0
- Responsive design with CSS Grid and Flexbox
- RTL support for Arabic

### Backend
- Python 3.10 + FastAPI
- PostgreSQL with SQLAlchemy ORM
- JWT authentication
- Docker containers for easy deployment

### AI Services
- **DeepSeek-V3**: Primary AI model for engineering analysis
- **Qwen-Max**: Fallback AI model
- Custom Arabic prompts for Egyptian engineering context

### Storage
- Local file system
- Optional S3 integration

### Payment Gateways
- Stripe
- Paymob (Egyptian payments)

## Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.10+
- PostgreSQL 15+
- API keys for DeepSeek and Qwen (DashScope)

### Quick Start

1. **Clone and navigate to the project directory:**
   ```bash
   cd engisuite-analytics
   ```

2. **Create a `.env` file with your API keys:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Build and run the application:**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Installation

If you don't want to use Docker:

1. **Create virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. **Create PostgreSQL database:**
   ```sql
   CREATE DATABASE engisuite;
   ```

3. **Update database configuration:**
   Edit `backend/config.py` with your database credentials

4. **Run the backend:**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Serve the frontend:**
   Use any HTTP server like Python's built-in server:
   ```bash
   cd frontend
   python -m http.server 80
   ```

## Features

### Engineering Calculators (50 Total)

#### Electrical (20)
- Load Calculation, Cable Sizing, Transformer Sizing, Voltage Drop
- Short Circuit, Busbar Sizing, Motor Starting, Switchgear
- Grounding Grid, Earthing Conductor, Fire Alarm Cable
- UPS Sizing, Solar PV, Lighting Design, Harmonic Analysis
- Emergency Lighting, Cable Tray, Diversity Factor, Power Factor

#### Mechanical (15)
- HVAC Load, Chiller Selection, Cooling Tower, AHU Selection, Boiler Sizing
- Pump Sizing, Pipe Sizing, Duct Sizing, Fan Selection, Compressor Sizing
- Heat Transfer, Refrigeration, Psychrometric, Steam System, BMS Point Count

#### Civil (15)
- Concrete Volume, Steel Weight, Earthwork Volume, Bar Bending Schedule
- Beam Load, Column Design, Slab Design, Cantilever Beam, Deflection Check
- Foundation Area, Pile Foundation, Retaining Wall, Seismic Load, Wind Load, Water Tank Design

### Data Analytics Module

- Upload Excel/CSV/JSON files
- Visual query builder (drag-drop tables)
- Auto-generate KPIs from engineering data
- 8 chart types (bar, line, pie, scatter, etc.)
- Dashboard builder with drag-drop
- PDF report export
- Scheduled reports (cron jobs)

### AI Assistant

- Explain calculations with AI (DeepSeek integration)
- Analyze data and generate insights
- Generate professional reports with AI
- Chat in Arabic with engineering expertise

### Report Generation

- Professional Engineering Report (formal Arabic)
- Quick Summary (bullet points)
- Client Presentation (charts + summary)
- Compliance Certificate (pass/fail check)

## API Endpoints

### Auth
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user profile

### Calculators
- `GET /calculators/{discipline}` - List calculators by discipline
- `POST /calculators/{type}/calculate` - Perform calculation
- `GET /calculators/history` - Get calculation history

### Analytics
- `POST /analytics/upload` - Upload data files
- `POST /analytics/query` - Execute queries
- `GET /analytics/templates` - Get analysis templates

### AI
- `POST /ai/explain` - Explain calculation
- `POST /ai/analyze` - Analyze data
- `POST /ai/report` - Generate report
- `POST /ai/chat` - Chat with AI

## Database Schema

The database uses PostgreSQL and includes tables for:
- Users (authentication and profiles)
- Calculations (calculation history)
- Datasets (uploaded data)
- Reports (generated reports)
- AI Usage (tracking API calls)

## Configuration

### Environment Variables

Create a `.env` file with these variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/engisuite

# AI Services
DEEPSEEK_API_KEY=sk-your-deepseek-key
DASHSCOPE_API_KEY=sk-your-qwen-key

# JWT
JWT_SECRET=your-secret-key-here

# Stripe
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# Paymob
PAYMOB_API_KEY=your-paymob-api-key

# Environment
ENVIRONMENT=development
DEBUG=True
```

## Deployment

### Docker Compose (Recommended)

1. Ensure Docker and Docker Compose are installed
2. Update `.env` file with production settings
3. Run:
   ```bash
   docker-compose up -d
   ```

### VPS Deployment

1. SSH to your VPS
2. Install Docker and Docker Compose
3. Copy project files to VPS
4. Create and run containers
5. Set up Nginx as reverse proxy

## Cost Optimization

- **AI Costs**: Use DeepSeek instead of OpenAI for lower costs
- **Server**: Use a VPS with 2GB RAM and 8GB HD
- **Database**: Use PostgreSQL with proper indexing
- **Storage**: Store files locally or use S3 with lifecycle policies

## Performance Optimization

- Compress frontend assets
- Enable caching for static files
- Optimize database queries
- Use CDN for static resources
- Monitor and scale as needed

## Security

- JWT token authentication
- Password hashing with bcrypt
- CORS protection
- Input validation
- Rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file

## Support

For support:
1. Email: info@engisuite.com
2. Phone: +20 100 123 4567
3. Support portal: http://support.engisuite.com

## Changelog

### v1.0.0 (Initial Release)
- 50 engineering calculators
- Data analysis module
- AI assistant with DeepSeek and Qwen integration
- Arabic UI with RTL support