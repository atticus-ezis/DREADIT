# DREADIT Backend

A Django REST API backend for a horror story sharing platform where users can create, share, and save short horror stories. The platform includes a curated database of 3,500+ existing stories sourced from CreepyPasta.

## 🎯 Features

### Authentication & User Management

- **JWT-based authentication** with refresh tokens
- **Social media login** (Google, Facebook, Twitter)
- **Email verification** and password reset functionality
- **OAuth2 provider** for third-party integrations
- **Custom user model** with extended fields

### API Features

- **RESTful API** built with Django REST Framework
- **CORS support** for frontend integration
- **Rate limiting** and API throttling
- **Token-based authentication** with multiple backends
- **Email backend** with Mailpit integration for development

### Development & Deployment

- **Docker containerization** with multi-stage builds
- **Environment-based configuration** using django-environ
- **Database flexibility** (SQLite for development, PostgreSQL for production)
- **Static file management** with WhiteNoise
- **Development tools** (django-extensions, pre-commit hooks)

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Docker & Docker Compose (optional)
- UV package manager

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd DREADIT/Backend
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:

   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   PRODUCTION=False
   USE_POSTGRES=False

   # Email Configuration (for development with Mailpit)
   EMAIL_HOST=localhost
   EMAIL_PORT=1025
   EMAIL_USE_TLS=False
   EMAIL_USE_SSL=False
   EMAIL_HOST_USER=""
   EMAIL_HOST_PASSWORD=""
   DEFAULT_FROM_EMAIL=noreply@localhost

   # Social Auth (optional)
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   FACEBOOK_CLIENT_ID=your-facebook-client-id
   FACEBOOK_CLIENT_SECRET=your-facebook-client-secret
   TWITTER_CLIENT_ID=your-twitter-client-id
   TWITTER_CLIENT_SECRET=your-twitter-client-secret
   ```

4. **Run database migrations**

   ```bash
   uv run python manage.py migrate
   ```

5. **Create a superuser**

   ```bash
   uv run python manage.py createsuperuser
   ```

6. **Start the development server**
   ```bash
   uv run python manage.py runserver
   ```

### Docker Development

1. **Start with Docker Compose**

   ```bash
   docker-compose up --build
   ```

2. **Run migrations in container**
   ```bash
   docker-compose exec web uv run python manage.py migrate
   ```

## 📧 Email Setup

### Development (Mailpit)

The project is configured to use Mailpit for email testing in development:

- Install Mailpit: `brew install mailpit` (macOS) or download from [GitHub](https://github.com/axllent/mailpit)
- Start Mailpit: `mailpit`
- Access web interface: http://localhost:8025
- All emails will be captured and viewable in the web interface

### Production (SMTP)

For production, configure real SMTP settings in your `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_USE_TLS=True
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🏗️ Project Structure

```
Backend/
├── dreadit/                 # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI application
├── users/                  # User management app
│   ├── models.py          # User model
│   ├── admin.py           # Admin interface
│   └── api/v1/            # API endpoints
├── templates/             # Email templates
├── staticfiles/           # Static files
├── docker-compose.yaml    # Development Docker setup
├── Dockerfile            # Production Docker image
└── pyproject.toml        # Dependencies and tools
```

## 🔧 API Endpoints

### Authentication

- `POST /api/v1/auth/registration/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `POST /api/v1/auth/password/reset/` - Password reset

### Social Authentication

- `GET /api/v1/auth/google/` - Google OAuth
- `GET /api/v1/auth/facebook/` - Facebook OAuth
- `GET /api/v1/auth/twitter/` - Twitter OAuth

## 🛠️ Technology Stack

- **Backend**: Django 5.2.6, Django REST Framework
- **Authentication**: JWT, OAuth2, django-allauth
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Email**: Mailpit (dev), SMTP (prod)
- **Containerization**: Docker, Docker Compose
- **Package Management**: UV
- **Code Quality**: Black, isort, flake8, pre-commit

## 📊 Data Source

The platform includes a curated database of 3,500+ horror stories sourced from the [CreepyPasta dataset](https://www.kaggle.com/datasets/thomaskonstantin/3500-popular-creepypastas) on Kaggle.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
