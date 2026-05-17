# Hybrid Deployment

This project is set up for:

- Vercel: Django web app and API
- Neon Postgres: primary database
- Railway: Celery worker and Celery beat
- Railway Redis or Upstash Redis: Celery broker/result backend
- Resend SMTP or any SMTP provider: issue notification email

## Architecture

- Vercel serves the Django site and `/api/*` endpoints
- The database is shared by Vercel and Railway through `DATABASE_URL`
- Railway runs the long-lived processes:
  - `celery -A config worker -l INFO --pool=solo`
  - `celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler`
- Email notifications are sent when the crawler creates a new issue for a starred repository

## 1. Create external services

Create these first:

1. Neon Postgres database
2. Redis instance
   Use Railway Redis or Upstash Redis
3. SMTP provider
   Resend SMTP works with the existing Django email settings

Collect these values:

- `DATABASE_URL`
- `REDIS_URL`
- `DJANGO_SECRET_KEY`
- `GITHUB_TOKEN`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

## 2. Deploy web app to Vercel

### Vercel environment variables

Add these in the Vercel project settings:

```env
DJANGO_SETTINGS_MODULE=config.settings_prod
DJANGO_SECRET_KEY=replace-me
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
GITHUB_TOKEN=ghp_...
APP_BASE_URL=https://your-project.vercel.app
ALLOWED_HOSTS=.vercel.app,your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-project.vercel.app,https://your-domain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=replace-me
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
DEFAULT_FROM_EMAIL=RepoRadar <noreply@yourdomain.com>
```

### Deploy command

From the repo root:

```bash
vercel
```

For production:

```bash
vercel --prod
```

The project uses Vercel's zero-config Django support, so no `api/` wrapper is required.

## 3. Run migrations against production DB

Vercel does not run long-lived startup commands for Django migrations. Run migrations separately against the same production database.

Example from your local machine:

```bash
DJANGO_SETTINGS_MODULE=config.settings_prod \
DATABASE_URL=postgresql://... \
DJANGO_SECRET_KEY=replace-me \
venv/bin/python manage.py migrate
```

## 4. Deploy worker and beat to Railway

Create two Railway services from this same repository:

1. `worker`
2. `beat`

Both should use the same environment variables as Vercel for:

```env
DJANGO_SETTINGS_MODULE=config.settings_prod
DJANGO_SECRET_KEY=replace-me
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
GITHUB_TOKEN=ghp_...
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=replace-me
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
DEFAULT_FROM_EMAIL=RepoRadar <noreply@yourdomain.com>
ALLOWED_HOSTS=.vercel.app,your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-project.vercel.app,https://your-domain.com
APP_BASE_URL=https://your-project.vercel.app
```

### Railway service commands

Worker command:

```bash
celery -A config worker -l INFO --pool=solo
```

Beat command:

```bash
celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

If you prefer, you can also run migrations as a one-off Railway job before starting the worker services.

## 5. Verify deployment

Check these URLs:

- `/healthz/`
- `/api/auth/me/`
- `/admin/`

Expected behavior:

1. Users can register and log in on Vercel
2. Users can star repositories
3. Worker stays online
4. Beat triggers the crawler periodically
5. New issues in starred repos generate emails

## 6. Important operational note

Notifications only send when a newly discovered issue is created in the database during a crawler run. Existing issues are not re-sent to new watchers retroactively.
