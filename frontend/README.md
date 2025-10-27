# Marketing Tool Frontend

AI-powered pitch deck generator with React + Vite + Tailwind CSS.

## Quick Start

### Prerequisites
- Node.js 18+ installed
- Backend server running on `http://localhost:8000`

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Build for Production

```bash
npm run build
```

## Features

- **Pitch Deck Generator**: Create professional PowerPoint presentations from GitHub repositories
- **6 Target Audiences**: Predefined templates for different stakeholders
- **Real-time Generation**: AI-powered content creation with Dedalus
- **Download Support**: Export as PowerPoint or view presenter script
- **Modern UI**: Responsive design with Tailwind CSS

## API Integration

The frontend uses a Vite proxy to communicate with the backend:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Proxy: `/api/*` → `http://localhost:8000/*`

All API calls are handled through `src/lib/api.js`.

## Project Structure

```
src/
├── components/
│   └── PitchDeckGenerator.jsx  # Main pitch deck UI
├── lib/
│   ├── api.js                  # API client utilities
│   └── utils.js                # Helper functions
├── App.jsx                     # Root component
└── main.jsx                    # Entry point
```

## Available API Endpoints

- `GET /api/target-audiences` - List available audiences
- `POST /api/generate-pitch-deck` - Generate pitch deck
- `GET /api/download-pitch-deck/{filename}` - Download file
- `GET /api/health` - Health check

## Troubleshooting

### "Failed to load target audiences"
- Ensure backend is running: `cd ../backend && uvicorn main:app --reload`
- Check backend is accessible at `http://localhost:8000/health`

### CORS Errors
- The Vite proxy should handle CORS automatically
- If issues persist, check `vite.config.js` proxy settings

### API Timeouts
- Large repositories may take time to index
- First-time generation includes repository indexing
- Subsequent generations are faster (uses cached vector DB)

## Tech Stack

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Styling
- **Lucide React**: Icons (if needed)

## Development Notes

- Hot Module Replacement (HMR) is enabled
- ESLint configured for code quality
- Proxy configured for seamless API integration
