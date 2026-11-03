# CivicConnect

## Local Civic Issue Reporting & Resolution System

CivicConnect is a beginner-friendly college mini-project prototype for reporting and tracking local civic issues in Mira-Bhayandar, Maharashtra, India. A citizen can register, submit a report, attach an optional photo and follow the report status. An administrator can review all reports, add remarks and update statuses.

> **Academic Mini-Project Prototype — Not an official MBMC service.**

This project is fictional and is not connected to MBMC systems or any government department. Reports are stored only inside this local academic prototype.

## Problem statement

Citizens often face difficulty reporting and tracking local civic issues such as potholes, garbage accumulation, damaged public infrastructure, broken streetlights and drainage problems. This project proposes a centralized web-based platform where citizens can report civic issues and track their progress, while administrators can manage and update reported complaints.

## Objectives

- Provide an easy way for citizens to report civic issues.
- Centralize civic complaint information.
- Allow citizens to track complaint status.
- Allow administrators to manage complaints.
- Provide basic complaint statistics.
- Demonstrate how a web-based civic reporting system can improve issue tracking.

## Features

- Citizen registration and login.
- Secure password hashing using Werkzeug.
- Citizen dashboard with report counts.
- Report creation with category, area, description and optional image upload.
- SQLite storage with automatically created tables.
- Citizen-only complaint list and detail pages.
- Complaint filters for category, status and area.
- Admin dashboard with status totals and simple area/category statistics.
- Admin search, filters, detail view, status update and remarks.
- Responsive HTML and CSS interface with small vanilla JavaScript interactions.
- User-friendly access errors, validation messages and a custom 404 page.

## Technologies used

- Python
- Flask
- SQLite
- HTML5
- CSS3
- Vanilla JavaScript
- Jinja2 templates

No React, Node.js, Django, MongoDB, blockchain, machine learning, AI, payment gateway or complex external API is needed for this project.

## Database structure

### `users`

| Field | Description |
| --- | --- |
| `id` | Primary key |
| `name` | User's full name |
| `email` | Unique login email |
| `password` | Werkzeug password hash |
| `role` | `citizen` or `admin` |
| `created_at` | Registration timestamp |

### `complaints`

| Field | Description |
| --- | --- |
| `id` | Primary key |
| `user_id` | Foreign key to `users.id` |
| `category` | Civic issue category |
| `title` | Short issue title |
| `description` | Full issue description |
| `area` | Mira-Bhayandar example area |
| `location` | More specific location |
| `image_filename` | Optional uploaded image filename |
| `status` | `Pending`, `Assigned`, `In Progress` or `Resolved` |
| `admin_remark` | Optional administrator update |
| `created_at` | Report timestamp |
| `updated_at` | Last update timestamp |

The database file and tables are created automatically when the application starts. Six fictional Mira-Bhayandar demo reports are added the first time the database is initialized.

## Project folder structure

```text
civicconnect/
├── app.py
├── database.db                 # created automatically on first run
├── requirements.txt
├── README.md
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   └── uploads/                # uploaded images
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── report.html
    ├── complaints.html
    ├── complaint_detail.html
    ├── admin_dashboard.html
    ├── admin_complaints.html
    ├── admin_complaint_detail.html
    └── 404.html
```

## Installation

From the project folder:

```bash
python3 -m pip install -r requirements.txt
```


## Run the Flask application

```bash
python3 app.py
```

The app uses the `PORT` environment variable when it is available and otherwise starts on port `5000`.

## Demo credentials

These accounts are for demonstration only:

**Admin**

- Email: `admin@civicconnect.local`
- Password: `Admin@123`
- Role: `admin`

**Citizen**

- Email: `citizen@civicconnect.local`
- Password: `Citizen@123`
- Role: `citizen`

Both passwords are stored as secure hashes, not plain text.

## Demonstration flow

1. Log in as the demo citizen.
2. Open **Report Issue** and submit a local issue.
3. Confirm the report appears under **My Complaints** with status **Pending**.
4. Log out and log in as the demo admin.
5. Open **All Complaints** and open the report.
6. Choose a new status, add an admin remark and update the complaint.
7. Log back in as the citizen and open the report to see the updated status and remark.

## Future improvements

These are intentionally not implemented in this beginner project:

- Interactive map integration.
- GPS-based location.
- Email or SMS notifications.
- Duplicate complaint detection.
- Mobile application.
- Advanced analytics.
- Real government department integration.
- Public complaint heatmaps.

## Academic disclaimer

CivicConnect is a mini project created by Zeeshan and Ashwin. It is not any official website. 
