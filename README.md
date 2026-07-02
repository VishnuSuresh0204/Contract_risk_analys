# 🤖 AI-Powered Contract Risk Analysis System

> A web-based application that automates the initial review of legal contracts using Natural Language Processing (NLP), rule-based risk analysis, and an offline AI assistant.

---

## 📋 Abstract

Organizations and individuals frequently rely on legal contracts to define responsibilities, protect business interests, and establish formal agreements. However, reviewing contracts manually is often a time-consuming process that requires legal expertise and increases the possibility of overlooking critical clauses or potential risks.

This project proposes the development of an **AI-Powered Contract Risk Analysis System** — a web-based application developed using Django that automates the initial review of legal contracts through a hybrid approach combining **Natural Language Processing (NLP)**, **rule-based risk analysis**, and an **offline AI assistant**.

---

## ✨ Features

### 📄 Contract Upload & Processing
- Upload contracts in **PDF**, **DOCX**, or **TXT** formats
- Automatic text extraction from uploaded documents
- Secure storage of all uploaded contracts and generated reports

### 🔍 AI Clause Detection
Automatically identifies essential legal clauses:
- ✅ Confidentiality
- ✅ Payment Terms
- ✅ Termination Conditions
- ✅ Liability
- ✅ Indemnification
- ✅ Dispute Resolution
- ✅ Force Majeure
- ✅ Intellectual Property
- ✅ Warranty
- ✅ Data Privacy

### ⚠️ Risk Assessment Engine
- Rule-based risk evaluation using predefined legal rules
- Assigns risk levels: **Low**, **Medium**, or **High**
- Identifies **missing or incomplete clauses** that may expose users to legal or financial risks

### 🤖 Offline AI Chatbot
- Operates **fully locally** — no paid cloud services required
- Explains legal terminology in plain language
- Answers user queries about contract clauses
- Summarizes contract content
- Provides recommendations based on risk analysis results

### 📊 Interactive Dashboard
- Contract summaries and clause-wise risk assessments
- Overall risk scores at a glance
- Downloadable analysis reports

### 👥 Role-Based Access
- **Admin Panel**: Manage users, view all contracts, manage clause rules, send notifications, review feedback & complaints
- **User Dashboard**: Upload contracts, view analysis results, interact with the AI chatbot

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| NLP | Natural Language Processing (spaCy / NLTK) |
| Database | SQLite (development) |
| Frontend | HTML5, Vanilla CSS, JavaScript |
| AI Chatbot | Offline AI (local inference) |
| File Handling | PDF, DOCX, TXT parsing |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/VishnuSuresh0204/Contract_risk_analys.git
cd Contract_risk_analys

# 2. Create and activate a virtual environment
python -m venv env
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Navigate to the Django project directory
cd contract

# 5. Apply database migrations
python manage.py migrate

# 6. Create a superuser (Admin)
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

Then open your browser and visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📁 Project Structure

```
AI_contract/
├── contract/                   # Django project root
│   ├── contract/               # Project settings & URLs
│   │   ├── settings.py
│   │   └── urls.py
│   ├── myapp/                  # Main application
│   │   ├── models.py           # Database models
│   │   ├── views.py            # View logic
│   │   ├── engine.py           # NLP + Risk Analysis Engine
│   │   └── migrations/
│   ├── templates/              # HTML templates
│   │   ├── base_public.html    # Base layout for public pages
│   │   ├── index.html          # Landing page
│   │   ├── login.html          # Login page
│   │   ├── user_register.html  # Registration page
│   │   ├── ADMIN/              # Admin panel templates
│   │   │   ├── base_admin.html
│   │   │   ├── admin_home.html
│   │   │   ├── view_users.html
│   │   │   ├── view_contracts.html
│   │   │   ├── contract_detail.html
│   │   │   ├── manage_rules.html
│   │   │   ├── send_notification.html
│   │   │   ├── view_feedback.html
│   │   │   └── view_complaints.html
│   │   └── USER/               # User dashboard templates
│   │       ├── base_user.html
│   │       ├── user_home.html
│   │       ├── upload_contract.html
│   │       ├── view_contracts.html
│   │       ├── contract_detail.html
│   │       ├── chatbot.html
│   │       ├── notifications.html
│   │       ├── feedback.html
│   │       └── complaints.html
│   └── static/                 # Static assets (CSS, JS, Images)
└── env/                        # Virtual environment
```

---

## 🔒 Key Design Principles

- **Offline First**: The AI chatbot and risk engine operate entirely locally, with no dependency on paid cloud APIs.
- **Data Privacy**: All contracts and reports are stored locally on your own server.
- **Transparency**: Risk analysis uses deterministic rule-based logic, making results consistent and auditable.
- **Cost-Effective**: Zero recurring subscription costs for AI features.

---

## 🎯 Use Cases

- 🏢 **Businesses** — Automate initial contract reviews before involving legal counsel
- 🎓 **Educational Institutions** — Teach contract law concepts with real-world analysis
- ⚖️ **Legal Professionals** — Speed up preliminary contract screening
- 👤 **Individuals** — Understand contracts before signing

---

## 📄 License

This project is developed for academic and educational purposes.

---

## 👨‍💻 Author

**Vishnu Suresh**  
[GitHub: VishnuSuresh0204](https://github.com/VishnuSuresh0204)
