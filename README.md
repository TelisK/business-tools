# BizTools

A Django web application for managing store income and expenses with ML-powered predictions.

## About

This is my first real-life project. I've built several apps, but this is the first one I'm actually using and deploying. I created it to help my family businesses track their income and expenses efficiently, and add more features, which I will add as time goes. It's currently running on a small server in my living room and has a lot of room for improvement, but it's a solid foundation to build on.

**Note:** The application interface is in Greek, designed for Greek-speaking users.

## Features

- Financial Tracking: management of daily income and business expenses.
- Simple web interface
- User authentication (register, login, password reset)
- Multi-store management
- Excel import/export
- Machine learning income predictions (scikit-learn RandomForestRegressor)
- Fixed expenses automation with Celery
- AI invoice analysis with Gemini
- Interactive Data Analytics: Full income and expense analysis
- Automated testing suite (Models, Views, Forms)


## Future Features

- API's for future mobile app
- Add more data for ML analysis (example: Cruise ships, day's weather, etc)
- Analyse more efficiently the income with economical values
- Registration with Gmail, Confirmation email
- UI Redesign
- And More...

## Celery Tasks
- **generate_fixed_expenses:** daily at 1 AM
- **store_predicted_income:** daily at 2 AM

## AI Invoice Features
- Automatic invoice text extraction
- Automatic data extraction to the database
- Duplicate detection
- Monthly usage limits per store (customizable)

## Tech Stack

- **Backend:** Django 6.0
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, Django Templates, Plotly
- **Task Queue & Automation:** Celery, Redis
- **AI & Machine Learning:** Google Gemini API, scikit-learn, pandas
- **Server:** Ubuntu, Nginx + Gunicorn
- **Deployment:** Docker Compose, Cloudflare Tunnel

## Setup

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in your values
3. Run migrations

### Local Development

```bash
git clone https://github.com/TelisK/business-tools.git
cd business-tools
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Visit: http://127.0.0.1:8000/biztools/

### Docker

```bash
docker compose up -d --build
docker compose exec web python manage.py migrate
```

## Project Structure

- `income_expenses/` - Main app for tracking
- `accounts/` - User authentication
- `business_tools/` - Project settings
- `static/` - CSS, JS, images
- `templates/` - HTML templates

## Testing

Run all tests:
```bash
python manage.py test
```

Run specific test file:
```bash
python manage.py test income_expenses.tests.test_models
python manage.py test income_expenses.tests.test_views
python manage.py test income_expenses.tests.test_forms
```

Docker:
```bash
docker compose exec web python manage.py test
docker compose exec web python manage.py test income_expenses.tests.test_models
docker compose exec web python manage.py test income_expenses.tests.test_views
docker compose exec web python manage.py test income_expenses.tests.test_forms
```

### Test Coverage

- **Models:** Income, Store
- **Views:** Authentication, Login, Security
- **Forms:** Registration, Income creation and Expenses creation validation

All critical features are tested.

## Live Demo

https://tkoutsogiannakis.site/biztools/

**Demo account:** username: `demo` | password: `Demo2026!`

Or register your own account to test full functionality.

## Privacy & Security
- Data isolation (users only see their own data)
- Privacy policy at /privacy-policy/
- Sensitive financial data excluded from admin panel

## Author

Tilemachos Koutsogiannakis  
GitHub: [@TelisK](https://github.com/TelisK)
