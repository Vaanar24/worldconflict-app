import React, { useState } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  Divider,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import WarningIcon from '@mui/icons-material/Warning';
import WhatshotIcon from '@mui/icons-material/Whatshot';
import PublicIcon from '@mui/icons-material/Public';
import { useEventContext } from '../context/EventContext';
import { formatDistanceToNow } from 'date-fns';

const EventSidebar: React.FC = () => {
  const { events, selectedEvent, setSelectedEvent, filters, setFilters, stats } = useEventContext();
  const [searchTerm, setSearchTerm] = useState('');

  const handleEventClick = (event: any) => {
    setSelectedEvent(event);
    if (event.location?.coordinates) {
      const [lon, lat] = event.location.coordinates;
      window.dispatchEvent(new CustomEvent('centerMap', { 
        detail: { lat, lng: lon, zoom: 6 }
      }));
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'conflict':
      case 'battle':
        return <WhatshotIcon />;
      case 'air_strike':
        return <WarningIcon />;
      default:
        return <PublicIcon />;
    }
  };

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const filteredEvents = events.filter(event => {
    const matchesSearch = searchTerm === '' || 
      event.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.country?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = !filters.eventType || event.type === filters.eventType;
    const matchesThreat = !filters.threatLevel || event.threat_level === filters.threatLevel;
    
    return matchesSearch && matchesType && matchesThreat;
  });

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', color: '#ff4444' }}>
        ⚔️ War Monitor
      </Typography>

      {stats && (
        <Box sx={{ mb: 2, display: 'flex', gap: 1 }}>
          <Box sx={{ p: 1, flex: 1, textAlign: 'center', bgcolor: 'error.dark', borderRadius: 1 }}>
            <Typography variant="caption">Active</Typography>
            <Typography variant="h6">{stats.active_conflicts || 0}</Typography>
          </Box>
          <Box sx={{ p: 1, flex: 1, textAlign: 'center', bgcolor: 'warning.dark', borderRadius: 1 }}>
            <Typography variant="caption">Critical</Typography>
            <Typography variant="h6">{stats.by_threat_level?.critical || 0}</Typography>
          </Box>
          <Box sx={{ p: 1, flex: 1, textAlign: 'center', bgcolor: 'info.dark', borderRadius: 1 }}>
            <Typography variant="caption">Countries</Typography>
            <Typography variant="h6">{stats.hotspots?.length || 0}</Typography>
          </Box>
        </Box>
      )}

      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth size="small" placeholder="Search conflicts..."
          value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment>,
          }}
          sx={{ mb: 1 }}
        />

        <FormControl fullWidth size="small" sx={{ mb: 1 }}>
          <InputLabel>Type</InputLabel>
          <Select value={filters.eventType || ''} label="Type" onChange={(e) => setFilters({...filters, eventType: e.target.value})}>
            <MenuItem value="">All Types</MenuItem>
            <MenuItem value="conflict">Conflict</MenuItem>
            <MenuItem value="battle">Battle</MenuItem>
            <MenuItem value="air_strike">Air Strike</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth size="small">
          <InputLabel>Threat</InputLabel>
          <Select value={filters.threatLevel || ''} label="Threat" onChange={(e) => setFilters({...filters, threatLevel: e.target.value})}>
            <MenuItem value="">All Levels</MenuItem>
            <MenuItem value="critical">Critical</MenuItem>
            <MenuItem value="high">High</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="low">Low</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Divider sx={{ my: 1 }} />

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {filteredEvents.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography color="text.secondary">No active conflicts found</Typography>
          </Box>
        ) : (
          <List>
            {filteredEvents.map((event) => (
              <ListItem
                key={event.id}
                sx={{
                  cursor: 'pointer',
                  bgcolor: selectedEvent?.id === event.id ? 'action.selected' : 'background.paper',
                  borderRadius: 1, mb: 1,
                  border: '1px solid',
                  borderColor: selectedEvent?.id === event.id ? 'primary.main' : 'divider',
                  '&:hover': { bgcolor: 'action.hover' }
                }}
                onClick={() => handleEventClick(event)}
              >
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: event.threat_level === 'critical' ? 'error.main' : 'warning.main' }}>
                    {getEventIcon(event.type)}
                  </Avatar>
                </ListItemAvatar>
                
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                        {event.title}
                      </Typography>
                      <Chip
                        label={event.threat_level}
                        size="small"
                        color={getThreatLevelColor(event.threat_level) as any}
                        sx={{ height: 20, '& .MuiChip-label': { fontSize: '0.7rem' } }}
                      />
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" color="text.secondary">
                        {event.location_name}, {event.country}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {formatDistanceToNow(new Date(event.occurred_at), { addSuffix: true })}
                      </Typography>
                      {event.casualties?.total && (
                        <Typography variant="caption" color="error" display="block">
                          💀 {event.casualties.total.toLocaleString()}+ casualties
                        </Typography>
                      )}
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        )}
      </Box>
    </Box>
  );
};

export default EventSidebar;