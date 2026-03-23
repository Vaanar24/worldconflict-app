import React from 'react';
import { Box, Typography, Paper, Grid, Chip } from '@mui/material';
import { useEventContext } from '../context/EventContext';

const StatisticsPanel: React.FC = () => {
  const { stats } = useEventContext();

  if (!stats) return null;

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom sx={{ color: '#ff4444' }}>
        War Statistics
      </Typography>

      <Grid container spacing={1}>
        <Grid item xs={6}>
          <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
            <Typography variant="caption">Active Conflicts</Typography>
            <Typography variant="h6">{stats.active_conflicts || 0}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={6}>
          <Paper variant="outlined" sx={{ p: 1, textAlign: 'center' }}>
            <Typography variant="caption">Total Casualties</Typography>
            <Typography variant="h6" color="error">
              {(stats.total_casualties || 0).toLocaleString()}+
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Hotspots
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {stats.hotspots?.slice(0, 5).map((hotspot: any) => (
            <Chip
              key={hotspot.country}
              label={`${hotspot.country}: ${hotspot.count}`}
              size="small"
              color="primary"
              variant="outlined"
            />
          ))}
        </Box>
      </Box>
    </Paper>
  );
};

export default StatisticsPanel;