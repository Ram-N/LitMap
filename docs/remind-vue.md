# Vue.js Version Quick Reference

## Running Locally

```bash
# Navigate to vue app
cd vue-app/

# Install dependencies (first time only)
npm install

# Start development server
npm run dev

# App runs at: http://localhost:5173
```

## Building for Production

```bash
# From vue-app/ directory
npm run build

# Preview production build locally
npm run preview
```

## Deploying to Vercel

### Option 1: Vercel CLI (Recommended)
```bash
# Install Vercel CLI globally (first time only)
npm install -g vercel

# From vue-app/ directory

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### Option 2: GitHub Integration
- Push changes to the connected GitHub branch
- Vercel auto-deploys on push (if configured)

## Project Structure
- **Framework**: Vue 3 + Vite
- **State Management**: Pinia
- **Styling**: TailwindCSS
- **Maps**: Google Maps API
- **Backend**: Firebase/Firestore
- **Build Output**: `vue-app/dist/`

## Common Issues

**Port already in use**: Kill the process or change port in vite.config.js

**Build fails**:
- Clear node_modules: `rm -rf node_modules package-lock.json && npm install`
- Check Node version: `node --version` (needs 18+)

**Vercel deployment fails**:
- Check vercel.json configuration
- Verify environment variables in Vercel dashboard
- Check build logs in Vercel console

## Environment Variables
Create `.env` file in `vue-app/` for local development:
```
VITE_FIREBASE_API_KEY=your_key_here
VITE_GOOGLE_MAPS_API_KEY=your_key_here
```

For Vercel, add these in the Vercel dashboard under Project Settings → Environment Variables.

## Quick Commands Cheat Sheet
```bash
cd vue-app/          # Navigate to Vue app
npm run dev          # Start dev server
npm run build        # Build for production
vercel --prod        # Deploy to Vercel production
```
