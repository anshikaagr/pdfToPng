# Deployment Guide — pdfToPng

> This document explains the Render deployment issue that was found, the fix applied, and how to deploy the full stack (Flask backend + Vite frontend) on Render.

---

## 🐛 Problem Summary

When the Flask backend was deployed as a **Web Service on Render**, the deployment consistently failed with the following output in the logs:

```
==> No open ports detected, continuing to scan...
==> No open ports detected, continuing to scan...
==> Port scan timeout reached, no open ports detected.
WARNING: This is a development server. Do not use it in a production deployment.
* Running on http://0.0.0.0:5000
==> Timed Out
```

Render's port scanner repeatedly found no open port and eventually timed out — even though Flask did eventually start. By the time the server was ready, Render had already killed the deployment.

---

## 🔍 Root Cause

The `backend/Dockerfile` was starting the server with:

```dockerfile
CMD ["python", "main.py"]
```

This launches **Flask's built-in development server**, which:
- Starts slowly and binds to the port **after** Render's scanner window closes
- Is not designed for production use (Render's own logs warn about this)
- Ignores Render's injected `PORT` environment variable correctly

`gunicorn` was already listed in `requirements.txt` (`gunicorn==23.0.0`) but was never being invoked.

---

## ✅ Fix Applied

### 1. `backend/Dockerfile` — CMD updated

**Before:**
```dockerfile
CMD ["python", "main.py"]
```

**After:**
```dockerfile
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 main:app
```

| Flag | Reason |
|---|---|
| `--bind 0.0.0.0:${PORT:-5000}` | Uses Render's `PORT` env var, falls back to 5000 |
| `--workers 1` | Essential for Free Tier (512MB RAM) to avoid OOM hangs |
| `--timeout 120` | Allows long-running PDF conversion tasks to complete |
| `main:app` | Points Gunicorn to the `app` object in `main.py` |

> **Shell form** (not exec/array form) is intentional — it allows `${PORT:-5000}` shell variable substitution to work correctly.

### 2. `render.yaml` — Added at project root

A `render.yaml` Blueprint file was added to enable one-click deployment of both the backend and frontend on Render with all settings pre-configured.

---

## 🚀 Render Deployment Guide

### Prerequisites
- A [Render](https://render.com) account
- This repository forked/pushed to your GitHub account

---

### Option A — One-Click via Blueprint (Recommended)

1. Go to your Render dashboard → **New → Blueprint**
2. Connect your GitHub repo
3. Render will auto-detect `render.yaml` and configure both services
4. **Before deploying**, update the two placeholder values in `render.yaml`:
   - `ALLOWED_ORIGINS` → your frontend Render URL
   - `VITE_API_URL` → your backend Render URL
5. Click **Apply**

---

### Option B — Manual Setup

#### Backend (Web Service)

1. Render Dashboard → **New → Web Service**
2. Connect your GitHub repo
3. Set the following:

| Setting | Value |
|---|---|
| **Root Directory** | `backend` |
| **Runtime** | `Python` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120 main:app` |

4. Add Environment Variables:

| Key | Value |
|---|---|
| `PORT` | `5000` |
| `ALLOWED_ORIGINS` | `https://your-frontend.onrender.com` |

5. Click **Create Web Service**

---

#### Frontend (Static Site)

1. Render Dashboard → **New → Static Site**
2. Connect your GitHub repo
3. Set the following:

| Setting | Value |
|---|---|
| **Root Directory** | `frontend` |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |

4. Add Environment Variables:

| Key | Value |
|---|---|
| `VITE_API_URL` | `https://your-backend.onrender.com` |

5. Click **Create Static Site**

---

## 🐳 Local Testing with Docker

Verify the fix locally before pushing:

```bash
# Build the backend image
docker build -t pdftopng-backend ./backend

# Run it with PORT set (simulating Render's environment)
docker run -p 5000:5000 -e PORT=5000 pdftopng-backend
```

**Expected output (Gunicorn, not Flask dev server):**
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Worker booting (pid: ...)
```

The port binds **immediately** — no scanner timeout.

---

## ⚡ Why Gunicorn over Flask's Dev Server?

Gunicorn is a production-grade WSGI server that binds to the port instantly on startup. For this deployment, we use **1 worker** to stay within the 512MB RAM limit mandated by Render's free tier, as the image-processing libraries (ONNX, NumPy) are memory-intensive.

---

## 📁 Files Changed

| File | Change |
|---|---|
| `backend/Dockerfile` | `CMD` updated to use Gunicorn |
| `render.yaml` | New — Render Blueprint for one-click deploy |
| `DEPLOYMENT.md` | New — This documentation file |
