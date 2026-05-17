# 🔀 Pull Request

## 📌 Issue Reference
<!-- Link to the issue this PR addresses. PRs without an issue reference may not be merged. -->
Closes #<issue_number>
<!-- Replace <issue_number> with the actual issue number, e.g. Closes #42 -->

---

## 📝 Summary

**What issue does this fix?**

The Flask backend fails to deploy on Render because the `backend/Dockerfile` starts the server with `CMD ["python", "main.py"]`, which runs Flask's built-in **development server**. This server is too slow to bind to a port before Render's port scanner times out, causing repeated `==> No open ports detected` errors and ultimately a deployment timeout.

**What major changes were made?**

- **`backend/Dockerfile`** — Changed the `CMD` from Flask's dev server to Gunicorn:
  ```dockerfile
  # Before
  CMD ["python", "main.py"]

  # After
  CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120 main:app
  ```
  Gunicorn was already listed in `requirements.txt` (`gunicorn==23.0.0`) — this is a zero-dependency fix.

- **`render.yaml`** *(new)* — Added a Render Blueprint file at the project root for one-click deployment of both the backend (Web Service) and frontend (Static Site) with all settings pre-configured.

- **`DEPLOYMENT.md`** *(new)* — Added comprehensive deployment documentation covering the root cause, the fix applied, step-by-step Render deployment instructions (both Blueprint and manual), and local Docker testing instructions.

---

## 📸 Screenshots (if applicable)

**Before (Render logs — deployment failure):**
```
==> No open ports detected, continuing to scan...
==> No open ports detected, continuing to scan...
==> Port scan timeout reached, no open ports detected.
WARNING: This is a development server. Do not use it in a production deployment.
* Running on http://0.0.0.0:5000
==> Timed Out
```

**After (Gunicorn binds immediately on startup):**
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Worker booting (pid: ...)
```

---

## ✅ Checklist
- [x] My code follows the project's coding conventions
- [x] I have tested all impacted features
- [x] I have updated or added necessary documentation

**Testing details:**
- Built the Docker image locally: `docker build -t pdftopng-backend ./backend`
- Ran the container with `PORT=5000` simulating Render's environment
- Confirmed Gunicorn binds to port **immediately** at startup (no delay)
- Verified the `/` endpoint responds correctly with HTTP 200
- Confirmed no Flask development server warnings in output

---

## 🔗 Related Issues / PRs
<!-- List any related issues or PRs for context. -->
- Fixes the Render deployment timeout issue reported in #<issue_number>

---

## 🏅 Open Source Program Participation
<!-- If contributing under an open-source program, mention it here. -->
Program Name: C4GT <!-- Update if applicable: GSoC, Hacktoberfest, etc. -->

---

## 💬 Additional Notes

- The fix uses **shell form** for the CMD (`CMD gunicorn ...` not `CMD ["gunicorn", ...]`) — this is intentional so that `${PORT:-5000}` shell variable substitution works correctly at runtime.
- The `render.yaml` contains two placeholder values (`https://your-frontend.onrender.com` and `https://your-backend.onrender.com`) that deployers must replace with their actual Render service URLs. This is documented in both the file comments and `DEPLOYMENT.md`.
- No new dependencies were added — `gunicorn==23.0.0` was already present in `requirements.txt`.
