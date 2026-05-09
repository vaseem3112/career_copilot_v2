# CareerCopilot — Backend

AI-powered career portal backend. Flask + SQLAlchemy + Celery + Claude AI.

---

## Stack

| Layer         | Tech                                      |
|---------------|-------------------------------------------|
| Web framework | Flask 3.0                                 |
| Database      | SQLite (dev) / PostgreSQL (prod)          |
| AI Reasoning  | Claude claude-sonnet-4-20250514 (Anthropic)          |
| Embeddings    | sentence-transformers (all-MiniLM-L6-v2)  |
| ML Model      | scikit-learn GradientBoostingClassifier   |
| Resume Parse  | PyMuPDF (PDF) + python-docx (DOCX)        |
| Job Data      | Adzuna API + JSearch RapidAPI             |
| Auth          | JWT (Flask-JWT-Extended) + bcrypt         |
| Async Tasks   | Celery + Redis                            |
| Email         | Flask-Mail (Gmail SMTP)                   |

---

## Quick Start

### 1. Clone and install

```bash
git clone <your-repo>
cd ai_career_copilot_backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in:
#   ANTHROPIC_API_KEY
#   MAIL_USERNAME + MAIL_PASSWORD
#   ADZUNA_APP_ID + ADZUNA_APP_KEY  (optional)
#   JSEARCH_API_KEY                  (optional)
```

### 3. Train the ML model

```bash
python ml_models/trainer.py
# Outputs: ml_models/shortlist_model.pkl
```

### 4. Start Redis

```bash
# macOS
brew install redis && redis-server

# Ubuntu
sudo apt install redis-server && redis-server

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### 5. Start Celery worker

```bash
# Terminal 2
celery -A celery_worker.celery worker --loglevel=info

# For periodic job fetching (Terminal 3)
celery -A celery_worker.celery beat --loglevel=info
```

### 6. Start Flask

```bash
# Terminal 1
python run.py
# API running at http://localhost:5000
```

---

## API Reference

### Auth
| Method | Endpoint                       | Description                  |
|--------|--------------------------------|------------------------------|
| POST   | /api/v1/auth/register          | Create account               |
| POST   | /api/v1/auth/verify-otp        | Verify email OTP             |
| POST   | /api/v1/auth/resend-otp        | Resend OTP                   |
| POST   | /api/v1/auth/login             | Login → JWT token            |
| POST   | /api/v1/auth/logout            | Logout                       |
| POST   | /api/v1/auth/forgot-password   | Send reset link              |
| POST   | /api/v1/auth/reset-password    | Reset with token             |
| DELETE | /api/v1/auth/account           | Delete account               |

### Profile
| Method | Endpoint                       | Description                  |
|--------|--------------------------------|------------------------------|
| GET    | /api/v1/profile                | Get full profile             |
| PATCH  | /api/v1/profile                | Update profile               |
| GET    | /api/v1/profile/completion     | Get completion %             |

### Resume
| Method | Endpoint                       | Description                  |
|--------|--------------------------------|------------------------------|
| POST   | /api/v1/parser/upload          | Upload resume (multipart)    |
| POST   | /api/v1/parser/analyze/:id     | Re-trigger analysis          |
| GET    | /api/v1/resume/list            | List all resumes             |
| DELETE | /api/v1/resume/:id             | Delete resume                |

### Analysis
| Method | Endpoint                       | Description                  |
|--------|--------------------------------|------------------------------|
| GET    | /api/v1/analysis/:resume_id    | Get analysis result          |

### ATS
| Method | Endpoint                       | Description                  |
|--------|--------------------------------|------------------------------|
| POST   | /api/v1/ats/generate           | Generate ATS resume          |
| GET    | /api/v1/ats/score/:resume_id   | Get ATS score                |

### Jobs
| Method | Endpoint                       | Description                  |
|--------|--------------------------------|------------------------------|
| GET    | /api/v1/jobs                   | List jobs (paginated)        |
| GET    | /api/v1/jobs/saved             | Get saved jobs               |
| POST   | /api/v1/jobs/save/:job_id      | Save a job                   |
| DELETE | /api/v1/jobs/save/:job_id      | Unsave a job                 |
| GET    | /api/v1/match/jobs             | Get AI-matched jobs          |

### Dashboard
| Method | Endpoint                       | Description                  |
|--------|--------------------------------|------------------------------|
| GET    | /api/v1/dashboard/stats        | Get dashboard stats          |

### Notifications
| Method | Endpoint                           | Description              |
|--------|------------------------------------|--------------------------|
| GET    | /api/v1/notifications              | List notifications       |
| PATCH  | /api/v1/notifications/:id/read     | Mark one as read         |
| PATCH  | /api/v1/notifications/read-all     | Mark all as read         |

### Settings
| Method | Endpoint                       | Description                  |
|--------|--------------------------------|------------------------------|
| GET    | /api/v1/settings               | Get settings                 |
| PATCH  | /api/v1/settings               | Update settings              |
| PATCH  | /api/v1/settings/password      | Change password              |
| GET    | /api/v1/settings/export        | Download all user data       |

---

## How AI Works (No Hardcoding)

```
Resume Upload
     ↓
PyMuPDF / python-docx → raw text
     ↓
Claude sees ONLY the raw resume text
Claude extracts: skills, roles, domains, strengths, weaknesses
(Nothing is assumed or fabricated)
     ↓
ATS Score: keyword overlap algorithm (no AI)
     ↓
Shortlist Probability: ML model on real feature vectors
     ↓
Job Matching: cosine similarity on sentence-transformer embeddings
     ↓
All results stored in DB
```

---

## Production Deployment

1. Set `FLASK_ENV=production` in `.env`
2. Use PostgreSQL: `DATABASE_URL=postgresql://...`
3. Use Redis Cloud or Upstash for Celery
4. Deploy with Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```
5. Use Supervisor or systemd for Celery workers

---

## Frontend

Connect the React frontend (Lovable-generated + fixed) to:
```
VITE_API_URL=http://localhost:5000/api/v1   # dev
VITE_API_URL=https://your-api.com/api/v1   # prod
```

All endpoints are CORS-enabled for localhost:3000 and localhost:5173.
