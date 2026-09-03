# ClickShop

![Django](https://img.shields.io/badge/Django-5.2-blue)
![Python](https://img.shields.io/badge/Python-3.12%20-lightgrey)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791)
![Render](https://img.shields.io/badge/Deployed%20on-Render-00c7b7)
![License](https://img.shields.io/badge/License-MIT-ff69b4)

A **Django‑based e‑commerce platform** with an **AI visual product search** powered by MobileNetV3-Small and FAISS.

> **Live demo:** <https://clickshop-1xn2.onrender.com>

---

## ✨ Key Features
- **User accounts** with profile management and secure authentication
- **Rich product catalog** – categories, image galleries, and admin media handling (Cloudinary)
- **Shopping cart & order workflow** with eSewa payment integration
- **AI visual search** – upload an image and instantly find similar items
- **Responsive UI** built with Django templates and Bootstrap
- **Admin honeypot** for added security

---

## 🛠️ Tech Stack
| Layer | Technology |
|------|------------|
| **Framework** | Django 5.2 |
| **Database** | PostgreSQL (Neon) |
| **Media Storage** | Cloudinary |
| **Static Files** | WhiteNoise |
| **AI Search** | ONNX Runtime (MobileNetV3) + FAISS |
| **Web Server** | Gunicorn |
| **Deployment** | Render.com |
| **Frontend** | Bootstrap 4, jQuery, Font Awesome, custom CSS/JS |


---

## 🚀 Quick Local Setup
```bash
# Clone the repository
git clone <repo-url>
cd "eproject"

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r eproject\requirements.txt

# Configure environment variables
# Copy .env.example → .env and fill in the required values (DB URL, Cloudinary keys, etc.)

# Apply migrations and start the dev server
python manage.py migrate
python manage.py runserver
```