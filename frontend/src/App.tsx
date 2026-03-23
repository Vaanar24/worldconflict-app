import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import WorldMap from './components/WorldMap';
import EventSidebar from './components/EventSidebar';
import StatisticsPanel from './components/StatisticsPanel';
import { EventProvider } from './context/EventContext';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#90caf9' },
    secondary: { main: '#f48fb1' },
    error: { main: '#f44336' },
    warning: { main: '#ff9800' },
    info: { main: '#2196f3' },
    success: { main: '#4caf50' },
    background: {
      default: '#0a1929',
      paper: '#132f4c',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <EventProvider>
        <Box sx={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
          <Grid container sx={{ height: '100%', width: '100%' }}>
            <Grid item xs={12} md={9} sx={{ height: '100%' }}>
              <WorldMap />
            </Grid>
            <Grid item xs={12} md={3} sx={{ height: '100%', overflow: 'auto', bgcolor: 'background.paper' }}>
              <Box sx={{ p: 2 }}>
                <StatisticsPanel />
                <EventSidebar />
              </Box>
            </Grid>
          </Grid>
        </Box>
      </EventProvider>
    </ThemeProvider>
  );
}

export default App;