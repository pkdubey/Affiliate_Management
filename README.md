# Affiliate Management SaaS

A Django-based web application to streamline operations between advertisers and publishers. Features include AI-based offer matching, automated invoicing, campaign performance management, and affiliate validation.

## Features

- Dashboard with revenue and profit analytics
- Advertiser and Publisher management
- Offer Matcher (AI-powered)
- Invoicing system with PDF generation
- Daily Revenue Sheet (DRS)
- Validation module
- Role-based permissions

## Tech Stack

- Python (Django)
- MySQL
- scikit-learn (AI matching)
- WeasyPrint (PDF generation)
- Docker

## Setup

### Prerequisites

1. Python 3.9+
2. MySQL 8.0+
3. For PDF generation on:
   - **Windows**: GTK3 Runtime ([download here](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe))
   - **macOS**: Install Cairo with Homebrew: `brew install cairo pango gdk-pixbuf libffi`

### Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate    # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure MySQL in settings.py:

```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'your_db_name',
            'USER': 'your_db_user',
            'PASSWORD': 'your_db_password',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }
```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Docker Setup (Optional)

1. Build the Docker image:
   ```bash
   docker-compose build
   ```
2. Start the containers:
   ```bash
   docker-compose up
   ```
3. Access the application at `http://127.0.0.1:8000/panel/users/login/`.
4. For API access, use the endpoint `/api/get_amount/` to retrieve currency amounts.

```bash
python manage.py update_rates
```

### Platform-Specific Notes

## Windows Setup

1. Install GTK3 Runtime from this link
2. Add GTK3 to your system PATH:

```txt
Typically installed at: C:\Program Files\GTK3-Runtime Win64\bin
```

3. Restart your terminal/IDE after installation

## macOS Setup

1. Install Homebrew if not already installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install required libraries:

```bash
brew install cairo pango gdk-pixbuf libffi
```

### Folder Structure

```text
project/
├── apps/
│   ├── invoicing/          # Invoicing app
│   │   ├── models.py       # Invoice models
│   │   ├── views.py        # Invoice views
│   │   ├── templates/      # Invoice templates
│   │   └── ...
│   └── drs/                # Daily Revenue Sheets
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

### Troubleshooting

## PDF Generation Issues:

Windows: Ensure GTK3 is in your PATH
macOS: Verify Cairo installation with brew list cairo
Both: Check WeasyPrint installation with python -m weasyprint --info

## MySQL Issues:

Ensure MySQL service is running
Verify database credentials in settings.py
