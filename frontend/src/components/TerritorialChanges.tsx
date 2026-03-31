import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
} from '@mui/material';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import { formatDistanceToNow } from 'date-fns';
import { fetchTerritorialChanges } from '../services/api';

interface TerritorialChange {
  id: string;
  location_name: string;
  country: string;
  from_control: string;
  to_control: string;
  changed_at: string;
  coordinates: [number, number];
  significance: string;
  source: string;
}

const TerritorialChanges: React.FC = () => {
  const [changes, setChanges] = useState<TerritorialChange[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadTerritorialChanges = async () => {
      try {
        const result = await fetchTerritorialChanges();
        setChanges(result.changes || []);
      } catch (err) {
        setError('Failed to load territorial changes');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadTerritorialChanges();
  }, []);

  const getSignificanceColor = (significance: string) => {
    switch (significance) {
      case 'strategic': return 'error';
      case 'tactical': return 'warning';
      case 'symbolic': return 'info';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Paper>
    );
  }

  if (changes.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">No territorial changes recorded</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <SwapHorizIcon /> Territorial Changes
      </Typography>
      <List>
        {changes.map((change, idx) => (
          <React.Fragment key={change.id}>
            <ListItem alignItems="flex-start">
              <ListItemAvatar>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <SwapHorizIcon />
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={`${change.location_name}, ${change.country}`}
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Chip 
                        label={change.from_control} 
                        size="small" 
                        color="error" 
                        variant="outlined" 
                      />
                      <Typography variant="body2">→</Typography>
                      <Chip 
                        label={change.to_control} 
                        size="small" 
                        color="success" 
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {formatDistanceToNow(new Date(change.changed_at), { addSuffix: true })} • {change.significance.toUpperCase()}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Source: {change.source}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
            {idx < changes.length - 1 && <Divider variant="inset" component="li" />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default TerritorialChanges;