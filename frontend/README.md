# Cyber Asset Management - Frontend

Frontend aplikasi Cyber Asset Management menggunakan React.js dan Tailwind CSS.

## Tech Stack

- **React 18** - UI Library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **Axios** - HTTP Client
- **Recharts** - Charts
- **Lucide React** - Icons

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

Aplikasi akan berjalan di `http://localhost:3000`

## Build

```bash
npm run build
```

## Environment Variables

Buat file `.env` berdasarkan `.env.example`:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Features

- ✅ Authentication (Login/Logout)
- ✅ Dashboard dengan statistik dan charts
- ✅ Asset Management (List, Create, Update, Delete)
- ✅ User Management (List, Create, Update, Delete, Activate/Deactivate)
- ✅ Loan Management (List, Create, Approve, Reject, Start, Return)
- ✅ Responsive Design
- ✅ Dark Theme
- ✅ Protected Routes

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable components
│   ├── contexts/       # React contexts (Auth)
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── package.json
└── vite.config.js
```

## API Integration

Frontend mengkonsumsi API dari backend yang berjalan di `http://localhost:8000/api/v1`.

Semua endpoint sudah terintegrasi:
- `/auth/*` - Authentication
- `/users/*` - User management
- `/assets/*` - Asset management
- `/loans/*` - Loan management

## Default Credentials

- **Super Admin:**
  - Email: `superadmin@example.com`
  - Password: `admin123`

- **User:**
  - Email: `user@example.com`
  - Password: `user123`

