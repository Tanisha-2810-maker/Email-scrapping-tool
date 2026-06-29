# 🚀 Lead Extractor Pro

Lead Extractor Pro is a Streamlit app that extracts public business emails from websites, saves leads in SQLite, exports CSV files, and sends outreach campaigns using Gmail SMTP.

## Features

- Extract public email addresses from website pages
- Detect company / website title
- Save leads in a local SQLite database
- Search and delete saved leads
- Send email campaigns to saved leads
- View email activity logs and dashboard metrics
- Export extracted results as CSV
- Optional Hunter email verification using `HUNTER_API_KEY`

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```env
EMAIL_ADDRESS=yourgmail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
HUNTER_API_KEY=optional_hunter_api_key
```

For Gmail, use a Gmail App Password, not your normal Gmail password.

## Run

```bash
streamlit run app.py
```

## Important Notes

- Some websites hide emails or only use contact forms, so no email may be found.
- The app extracts only public emails from website HTML.
- Hunter verification is optional. Without `HUNTER_API_KEY`, emails are saved as `Not verified`.
- Follow-up scheduling works locally while the app process is running. For real production follow-ups, use a database-backed scheduler or cron job.
