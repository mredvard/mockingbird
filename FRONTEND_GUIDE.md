# TTS Voice Cloning - Frontend Guide

## Overview

The frontend is a complete React application with TypeScript, providing a user-friendly interface for voice recording, TTS generation with real-time progress tracking, and audio playback.

## Tech Stack

- **React 19.2** - UI framework
- **TypeScript** - Type safety
- **React Router DOM 7.13** - Navigation
- **React Query 5.90** - Data fetching & caching
- **Tailwind CSS 4.1** - Styling
- **Vite 7.2** - Build tool & dev server

## Setup & Installation

```bash
cd frontend
npm install
```

## Running the Application

### Development Mode

```bash
# Terminal 1: Start backend
cd /Users/edricardo/Documents/coffeenights/TTS
uv run python -m backend.app.main

# Terminal 2: Start frontend
cd /Users/edricardo/Documents/coffeenights/TTS/frontend
npm run dev
```

The frontend will be available at: **http://localhost:5173**

### Production Build

```bash
npm run build
npm run preview
```

## Application Structure

```
frontend/src/
├── components/
│   ├── ui/                      # Base UI components
│   │   ├── Button.tsx           # Buttons with variants
│   │   ├── Card.tsx             # Card containers
│   │   ├── Input.tsx            # Text inputs
│   │   ├── Select.tsx           # Dropdowns
│   │   ├── Modal.tsx            # Modal dialogs
│   │   └── AudioPlayer.tsx      # Audio playback
│   ├── voice/                   # Voice components
│   │   ├── VoiceRecorder.tsx    # Recording interface
│   │   ├── VoiceCard.tsx        # Voice profile card
│   │   └── VoiceList.tsx        # Voice grid
│   └── generation/              # TTS components
│       ├── TextInput.tsx        # Text input for TTS
│       ├── ModelSelector.tsx    # Model selection
│       ├── GenerationCard.tsx   # Generated audio card
│       └── GenerationList.tsx   # Generation history
├── pages/
│   ├── Home.tsx                 # Dashboard
│   ├── VoiceLibrary.tsx         # Voice management
│   └── Generate.tsx             # TTS generation
├── hooks/
│   ├── useVoices.ts             # Voice CRUD hooks
│   ├── useGeneration.ts         # TTS generation hooks
│   └── useModels.ts             # Backend info hooks
├── services/
│   └── api.ts                   # API client
├── types/
│   └── index.ts                 # TypeScript types
├── App.tsx                      # Main app with routing
└── main.tsx                     # Entry point
```

## User Workflow

### 1. Record a Voice Sample

1. Navigate to **Voices** page
2. Click **"Record New Voice"**
3. Grant microphone permissions
4. Record 3-10 seconds of clear speech
5. Enter a name for your voice profile
6. Click **"Save Voice"**
7. The system automatically transcribes your audio

### 2. Generate TTS

1. Navigate to **Generate** page
2. Select a voice profile from the list
3. Enter the text you want to convert to speech
4. Choose a model (0.6B is faster, 1.7B is higher quality)
5. Click **"Generate Speech"**
6. Watch the progress bar (takes 40-60 seconds)
7. Play the generated audio or download it

### 3. Manage Voices & Generations

- **Voice Library**: View, play, or delete voice profiles
- **Generation History**: Access previous generations from the sidebar

## Key Features

### 🎤 Voice Recording

- Browser-based microphone recording
- Real-time recording timer
- Pause/resume functionality
- Waveform visualization (animated bars)
- Automatic transcription with Whisper AI

### 🔊 TTS Generation

- **Async generation with progress tracking**
  - Real-time progress bar (0-100%)
  - Status messages: "Initializing...", "Generating audio...", etc.
  - Takes 40-60 seconds for short text
  - No page freezing during generation

- Model selection (0.6B / 1.7B variants)
- Character limit (1000 chars)
- Success/error notifications

### 🎵 Audio Playback

- Play/pause controls
- Seek slider
- Volume control
- Time display (current/duration)
- Download as WAV

### 📊 Dashboard

- Quick stats (voices, generations, backend platform)
- Getting started guide
- Feature highlights

## API Integration

The frontend communicates with the backend via REST API:

### Voice Endpoints
- `POST /api/voices` - Upload voice with auto-transcription
- `GET /api/voices` - List all voices
- `GET /api/voices/{id}` - Get voice details
- `DELETE /api/voices/{id}` - Delete voice

### Generation Endpoints (Async)
- `POST /api/generations/async` - Start async generation
- `GET /api/generations/tasks/{task_id}` - Check progress
- `DELETE /api/generations/tasks/{task_id}` - Clean up task
- `GET /api/generations` - List generations
- `DELETE /api/generations/{id}` - Delete generation

### Model Endpoints
- `GET /api/generations/models/info` - Backend info
- `GET /api/generations/models/list` - Available models

## Configuration

### Environment Variables

Create `frontend/.env` (optional):

```env
VITE_API_URL=http://localhost:8000
```

Default is `http://localhost:8000` if not set.

### Tailwind CSS

The project uses Tailwind CSS v4 with the PostCSS plugin:

- **Config**: `tailwind.config.js`
- **PostCSS**: `postcss.config.js`
- **Styles**: `src/index.css`

## Development Tips

### Hot Reload

Vite provides instant hot module replacement (HMR). Changes to components will reflect immediately in the browser.

### Type Checking

```bash
# Check TypeScript types without building
npm run tsc -- --noEmit
```

### Linting

```bash
npm run lint
```

### React Query DevTools

The app uses React Query for data fetching. You can add DevTools for debugging:

```bash
npm install @tanstack/react-query-devtools
```

Then in `App.tsx`:
```tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Inside QueryClientProvider
<ReactQueryDevtools initialIsOpen={false} />
```

## Browser Requirements

- Modern browser with ES6+ support
- MediaRecorder API for voice recording (Chrome, Firefox, Safari)
- Microphone access permission

### Testing Microphone Access

Open browser console and run:
```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(() => console.log('Microphone access granted'))
  .catch(err => console.error('Microphone access denied:', err));
```

## Troubleshooting

### Tailwind styles not loading

1. Check that `@tailwindcss/postcss` is installed:
   ```bash
   npm install @tailwindcss/postcss
   ```

2. Verify `postcss.config.js`:
   ```js
   export default {
     plugins: {
       '@tailwindcss/postcss': {},
       autoprefixer: {},
     },
   }
   ```

3. Restart dev server:
   ```bash
   npm run dev
   ```

### API calls failing

1. Ensure backend is running on port 8000
2. Check CORS is enabled in backend
3. Verify `VITE_API_URL` in `.env` (or defaults to localhost:8000)

### Microphone not working

1. Grant browser microphone permissions
2. Check browser console for errors
3. Try in a different browser (Chrome recommended)
4. Ensure no other app is using the microphone

### TypeScript errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for type errors
npx tsc --noEmit
```

## Performance Notes

### First Load

- First TTS generation downloads the model (~1.5-3.5 GB)
- Subsequent generations are faster (model cached)
- React Query caches API responses

### Optimization

- Components use React.memo where appropriate
- React Query deduplicates API calls
- Images and assets are lazy-loaded
- Production build is minified and tree-shaken

## Deployment

### Build for Production

```bash
npm run build
```

Output: `dist/` directory

### Serve Static Files

```bash
# Preview production build locally
npm run preview

# Or use any static file server
npx serve dist
```

### Deploy to Hosting

The `dist/` folder can be deployed to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages
- Any static hosting service

Update `VITE_API_URL` environment variable to point to your production backend.

## Future Enhancements

- [ ] Add voice profile export/import
- [ ] Add generation queue for multiple items
- [ ] Add real-time waveform during recording
- [ ] Add audio effects (speed, pitch)
- [ ] Add batch TTS generation
- [ ] Add generation templates
- [ ] Add voice profile tags/categories
- [ ] Add dark mode

## Support

For issues or questions:
- Check backend logs: Backend should be running on port 8000
- Check browser console for frontend errors
- Ensure microphone permissions are granted
- Verify network connectivity between frontend and backend

---

**Built with ❤️ using React + TypeScript + Tailwind CSS**
