import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css' // Basic global styles
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import { prefixer } from 'stylis';
import rtlPlugin from 'stylis-plugin-rtl';

// Configure Vazirmatn font and RTL for MUI
const theme = createTheme({
  direction: 'rtl', // Enable RTL direction for MUI components
  typography: {
    fontFamily: '"Vazirmatn", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  // Add other theme customizations here if needed
});

// Configure stylis-plugin-rtl for emotion (MUI's styling engine)
const cacheRtl = createCache({
  key: 'muirtl',
  stylisPlugins: [prefixer, rtlPlugin],
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <CacheProvider value={cacheRtl}>
      <ThemeProvider theme={theme}>
        <CssBaseline /> {/* Applies baseline styling and background color */}
        <App />
      </ThemeProvider>
    </CacheProvider>
  </React.StrictMode>,
)
