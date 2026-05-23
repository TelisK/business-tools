# BizTools

A Django web application for managing store income and expenses with ML-powered predictions.

## About

This is my first real-life project. I've built several apps, but this is the first one I'm actually using and deploying. I created it to help my family businesses track their income and expenses efficiently, and add more features, which I will add as time goes. It's currently running on a small server in my living room and has a lot of room for improvement, but it's a solid foundation to build on.

**Note:** The application interface is in Greek, designed for Greek-speaking users.

## Features

- User authentication (register, login, password reset)
- Multi-store management
- Income and expense tracking
- Excel import/export
- Machine learning predictions (scikit-learn RandomForestRegressor)
- Simple web interface

## Future Features

- Automated AI model for tracking and saving to the database data from Invoices of the Business. (https://github.com/TelisK/invoice_reader_AI)
- API's for future mobile app
- Card with fixed expenses with options for the user
- Add more data for ML analysis (example: Cruise ships, day's weather, etc)
- Analyse more efficiently the income with economical values
- Registration with Gmail, Confirmation email
- And More...

## Tech Stack

- **Backend:** Django 6.0
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, Django Templates
- **ML:** scikit-learn, pandas
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

## Live Demo

https://tkoutsogiannakis.site/biztools/

**Demo account:** username: `demo` | password: `Demo2026!`

Or register your own account to test full functionality.

## Author

Tilemahos Koutsogiannakis  
GitHub: [@TelisK](https://github.com/TelisK)
