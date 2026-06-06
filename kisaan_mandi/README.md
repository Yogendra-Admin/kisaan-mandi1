# 🌿 Kisaan Mandi — किसान मंडी — किसान मण्डी

A full-featured **trilingual** agricultural marketplace built with Django.
Supports **English**, **Hindi (हिन्दी)**, and **Nepali (नेपाली)**.

## Tech Stack
| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | Python 3 + Django                   |
| Database | SQLite (built-in, zero config)      |
| Frontend | HTML5 + Bootstrap 5 + Font Awesome  |
| Languages| English + हिन्दी + नेपाली           |

## Features
- 👨‍🌾 **Farmers** — Register, list products (name in 3 languages), manage inventory, receive & update orders
- 🛒 **Buyers** — Browse, search/filter, cart, place orders, write reviews
- 📊 **Admin** — Django admin panel, manage all data, add mandi prices
- 💰 **Market Prices** — Mandi/bazar rates with trend indicators (▲▼━) in all 3 languages
- 🗣️ **Trilingual UI** — Every label, button, and message in English / हिन्दी / नेपाली
- 🇮🇳🇳🇵 **India & Nepal** — Farmers from both countries supported
- 🍃 **Organic Filter** — Mark and filter organic produce
- ⭐ **Reviews** — Star ratings on products

## Quick Start
```bash
# 1. Install dependencies
pip install django pillow

# 2. Navigate into project
cd kisaan_mandi

# 3. Run migrations
python manage.py migrate

# 4. Seed demo data (products, prices, users)
python manage.py seed_data

# 5. Start the server
python manage.py runserver
```
Open: **http://127.0.0.1:8000**

## Demo Accounts
| Role        | Username       | Password    | Notes                  |
|-------------|----------------|-------------|------------------------|
| Admin       | `admin`        | `admin123`  | Full access            |
| Farmer 🇮🇳  | `ramu_farmer`  | `farmer123` | Maharashtra, India     |
| Farmer 🇳🇵  | `ram_bahadur`  | `farmer123` | Kathmandu, Nepal       |
| Buyer       | `demo_buyer`   | `buyer123`  | Can browse & order     |

## Admin Panel
Visit `/admin/` with `admin / admin123` to manage everything.

## Project Structure
```
kisaan_mandi/
├── accounts/        # CustomUser — Farmer / Buyer / Admin roles
├── marketplace/     # Product, Category, Review models
├── orders/          # Order, Cart models
├── prices/          # MarketPrice (mandi bhav / bazar mulya)
├── core/            # Home, About pages + seed command
└── templates/       # All HTML — Bootstrap 5, trilingual labels
    ├── base.html
    ├── core/
    ├── accounts/
    ├── marketplace/
    ├── orders/
    └── prices/
```
