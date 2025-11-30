# FiscalOptim Frontend

Modern Next.js frontend for the ComptabilityProject tax optimization platform.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui (Radix UI primitives)
- **Charts**: Recharts
- **Icons**: Lucide React

## Features

### 1. Landing Page (`/`)
- Hero section with gradient text
- Feature cards highlighting key benefits
- CTA sections
- Navigation to simulator and dashboard

### 2. Tax Simulator (`/simulator`)
- Comprehensive form for tax calculation inputs:
  - Personal information (name, status, nb_parts, tax year)
  - Income sources (professional, salary, rental, capital)
  - Deductions (PER, alimony, other)
  - Social contributions (URSSAF, PAS)
- Real-time results display:
  - Revenu imposable
  - Quotient familial
  - Impôt brut/net
  - TMI and taux effectif
  - Social charges
  - Total fiscal burden
- Integration with backend API
- Responsive sticky results column

### 3. Dashboard (`/dashboard`)
- Key metrics overview cards
- Interactive charts:
  - Pie chart for income breakdown
  - Pie chart for charges breakdown
  - Bar chart for monthly projections
- Insights and key information
- Quick actions to optimizations and chat

### 4. Optimizations Page (`/optimizations`)
- Profile input form
- AI-generated optimization recommendations
- Each recommendation shows:
  - Title and description
  - Category badge
  - Complexity level (1-3 stars)
  - Risk assessment
  - Estimated savings
- Total potential savings summary
- Link to AI chat for detailed advice

### 5. AI Chat Interface (`/chat`)
- Conversational UI with Claude 3 Haiku
- Message history with timestamps
- User and assistant message bubbles
- Loading states with animated dots
- Suggested starter questions
- Integration with `/api/v1/llm/analyze` endpoint
- Conversation ID tracking for context
- Auto-scroll to latest messages

## API Integration

All pages integrate with the backend API through the centralized client (`lib/api.ts`):

- `POST /api/v1/tax/calculate` - Tax calculations
- `POST /api/v1/optimization/run` - Generate optimizations
- `POST /api/v1/llm/analyze` - AI chat analysis
- `GET /health` - Health check

TypeScript interfaces ensure type safety across the entire application.

## Design System

### Colors
- Primary: Violet (#8B5CF6)
- Accent: Indigo (#6366F1) to Blue (#3B82F6)
- Success: Green
- Warning: Orange
- Error: Red

### Typography
- Font: Inter (system font stack)
- Headings: Bold with gradient text effects
- Body: Regular weight, slate colors

### Components
All UI components follow the shadcn/ui patterns:
- Consistent spacing and sizing
- Focus states with ring-offset
- Disabled states
- Hover effects
- Responsive design

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Landing page
│   ├── simulator/
│   │   └── page.tsx          # Tax simulator
│   ├── dashboard/
│   │   └── page.tsx          # Dashboard with charts
│   ├── optimizations/
│   │   └── page.tsx          # Optimization recommendations
│   └── chat/
│       └── page.tsx          # AI chat interface
├── components/
│   └── ui/
│       ├── button.tsx        # Button component
│       ├── card.tsx          # Card components
│       ├── input.tsx         # Input component
│       ├── label.tsx         # Label component
│       └── select.tsx        # Select component
├── lib/
│   ├── api.ts                # API client with TypeScript interfaces
│   └── utils.ts              # Utility functions (cn)
└── package.json              # Dependencies
```

## Setup

### Requirements
- Node.js >=20.9.0
- npm >=9.0.0

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Application will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

### Production

```bash
npm start
```

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

This configures the backend API URL. Default is `http://localhost:8000`.

## Deployment

The application is ready to deploy to Vercel:

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

Vercel will automatically:
- Install dependencies
- Build the application
- Deploy to production
- Provide a custom domain

## Features TODO

- [ ] Add authentication
- [ ] Persist calculation results in local storage
- [ ] Add export to PDF functionality
- [ ] Add comparison with previous years
- [ ] Add mobile app with React Native
- [ ] Add email notifications for optimization suggestions
- [ ] Add dark mode toggle
- [ ] Add multi-language support (English)

## Development Notes

- All pages use "use client" directive for client-side interactivity
- Forms use controlled components with React state
- API calls handle errors with try/catch
- Loading states provide user feedback
- Mock data is used for development when backend is unavailable
- Responsive design works on mobile, tablet, and desktop

## Known Issues

- Requires Node.js >=20.9.0 (Next.js 16 requirement)
- Node version warning can be ignored during development on older versions
