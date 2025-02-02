import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import App from './App'

// Kurumsal tema oluşturuyoruz
const theme = createTheme({
  palette: {
    primary: {
      main: '#1a237e', // Koyu mavi
      light: '#534bae',
      dark: '#000051',
    },
    secondary: {
      main: '#424242', // Gri
      light: '#6d6d6d',
      dark: '#1b1b1b',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline /> {/* CSS reset için */}
        <App />
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
