import React, { useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import WorldMap from './components/WorldMap';
import EventSidebar from './components/EventSidebar';
import StatisticsPanel from './components/StatisticsPanel';
import HistoricalDashboard from './components/HistoricalDashboard';
import LiveCameraView from './components/LiveCameraView';
import { EventProvider } from './context/EventContext';
import { websocketService } from './services/websocket';

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
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
});

function App() {
  useEffect(() => {
    websocketService.connect();
    websocketService.onEvent((event) => {
      console.log('New event received via WebSocket:', event);
    });
    return () => {
      websocketService.disconnect();
    };
  }, []);

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
                <HistoricalDashboard />
                <EventSidebar />
              </Box>
            </Grid>
          </Grid>
        </Box>
        <LiveCameraView />
      </EventProvider>
    </ThemeProvider>
  );
}

export default App;