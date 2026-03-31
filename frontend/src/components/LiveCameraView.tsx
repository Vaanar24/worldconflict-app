import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Modal,
  Card,
  CardMedia,
  CardContent,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Snackbar,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import VideocamIcon from '@mui/icons-material/Videocam';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useEventContext } from '../context/EventContext';

interface CameraFeed {
  id: string;
  title: string;
  description: string;
  url: string;
  thumbnail: string;
  location_name: string;
  country: string;
  feed_type: string;
  status: string;
}

const LiveCameraView: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState<CameraFeed | null>(null);
  const [cameraFeeds, setCameraFeeds] = useState<CameraFeed[]>([]);
  const [loading, setLoading] = useState(false);
  const [feedType, setFeedType] = useState('all');
  const [iframeError, setIframeError] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const { selectedEvent } = useEventContext();

  const fetchCameraFeeds = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/cameras');
      const data = await response.json();
      setCameraFeeds(data.feeds || []);
    } catch (error) {
      console.error('Error fetching camera feeds:', error);
      setCameraFeeds(getMockCameraFeeds());
    } finally {
      setLoading(false);
    }
  }, []);

  const getMockCameraFeeds = (): CameraFeed[] => {
    return [
      {
        id: 'kyiv_live',
        title: 'Ukraine - Kyiv City Center',
        description: 'Live view of Independence Square',
        url: 'https://www.youtube.com/embed/SlHjBp_w4kA',
        thumbnail: 'https://img.youtube.com/vi/SlHjBp_w4kA/0.jpg',
        location_name: 'Kyiv',
        country: 'Ukraine',
        feed_type: 'conflict_feed',
        status: 'live'
      },
      {
        id: 'jerusalem_live',
        title: 'Jerusalem - Western Wall',
        description: 'Live view of the Western Wall',
        url: 'https://www.youtube.com/embed/ZN5jW6G-qOk',
        thumbnail: 'https://img.youtube.com/vi/ZN5jW6G-qOk/0.jpg',
        location_name: 'Jerusalem',
        country: 'Israel',
        feed_type: 'conflict_feed',
        status: 'live'
      },
      {
        id: 'times_square',
        title: 'New York - Times Square',
        description: 'Live view of Times Square',
        url: 'https://www.youtube.com/embed/1hJGh9BRNDM',
        thumbnail: 'https://img.youtube.com/vi/1hJGh9BRNDM/0.jpg',
        location_name: 'Times Square',
        country: 'USA',
        feed_type: 'city_cam',
        status: 'live'
      },
      {
        id: 'shibuya',
        title: 'Tokyo - Shibuya Crossing',
        description: 'Live view of Shibuya Crossing',
        url: 'https://www.youtube.com/embed/FQHtKJ7YXZI',
        thumbnail: 'https://img.youtube.com/vi/FQHtKJ7YXZI/0.jpg',
        location_name: 'Shibuya',
        country: 'Japan',
        feed_type: 'city_cam',
        status: 'live'
      },
      {
        id: 'london',
        title: 'London - Piccadilly Circus',
        description: 'Live view of Piccadilly Circus',
        url: 'https://www.youtube.com/embed/irv1YGgQXeg',
        thumbnail: 'https://img.youtube.com/vi/irv1YGgQXeg/0.jpg',
        location_name: 'London',
        country: 'UK',
        feed_type: 'city_cam',
        status: 'live'
      },
      {
        id: 'paris',
        title: 'Paris - Eiffel Tower',
        description: 'Live view of Eiffel Tower',
        url: 'https://www.youtube.com/embed/46sQ0OMlV-U',
        thumbnail: 'https://img.youtube.com/vi/46sQ0OMlV-U/0.jpg',
        location_name: 'Paris',
        country: 'France',
        feed_type: 'city_cam',
        status: 'live'
      }
    ];
  };

  // Listen for camera show events from map
  useEffect(() => {
    const handleShowCamera = (event: CustomEvent) => {
      const { location, country } = event.detail;
      const matchingFeed = cameraFeeds.find(feed => 
        feed.location_name.toLowerCase().includes(location.toLowerCase()) ||
        feed.country.toLowerCase().includes(country.toLowerCase())
      );
      
      if (matchingFeed) {
        setSelectedCamera(matchingFeed);
        setIframeError(false);
        setOpen(true);
      } else {
        setSnackbarOpen(true);
      }
    };

    window.addEventListener('showCamera', handleShowCamera as EventListener);
    
    return () => {
      window.removeEventListener('showCamera', handleShowCamera as EventListener);
    };
  }, [cameraFeeds]);

  useEffect(() => {
    fetchCameraFeeds();
  }, [fetchCameraFeeds]);

  useEffect(() => {
    if (selectedEvent && !open) {
      const matchingFeed = cameraFeeds.find(feed => 
        feed.location_name.toLowerCase().includes(selectedEvent.location_name.toLowerCase()) ||
        feed.country.toLowerCase().includes(selectedEvent.country.toLowerCase())
      );
      if (matchingFeed) {
        setSelectedCamera(matchingFeed);
        setIframeError(false);
        setOpen(true);
      }
    }
  }, [selectedEvent, cameraFeeds, open]);

  const filteredFeeds = feedType === 'all' 
    ? cameraFeeds 
    : cameraFeeds.filter(feed => feed.feed_type === feedType);

  const handleRetry = () => {
    setIframeError(false);
    // Force iframe reload by updating key
    setSelectedCamera({ ...selectedCamera! });
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        startIcon={<VideocamIcon />}
        onClick={() => setOpen(true)}
        sx={{ position: 'fixed', bottom: 20, right: 20, zIndex: 1000, borderRadius: 2 }}
      >
        Live Cameras
      </Button>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        message="No camera feed available for this location"
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Paper
          sx={{
            position: 'relative',
            width: '90%',
            height: '90%',
            maxWidth: 1200,
            bgcolor: 'background.paper',
            overflow: 'auto',
            p: 2,
            borderRadius: 2,
          }}
        >
          <IconButton
            sx={{ position: 'absolute', top: 8, right: 8, zIndex: 1 }}
            onClick={() => setOpen(false)}
          >
            <CloseIcon />
          </IconButton>

          <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
            📹 Live Camera Feeds
          </Typography>

          <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Feed Type</InputLabel>
              <Select
                value={feedType}
                label="Feed Type"
                onChange={(e) => setFeedType(e.target.value)}
              >
                <MenuItem value="all">All Feeds</MenuItem>
                <MenuItem value="conflict_feed">Conflict Zones</MenuItem>
                <MenuItem value="city_cam">City Cameras</MenuItem>
              </Select>
            </FormControl>
            <Button
              size="small"
              startIcon={<RefreshIcon />}
              onClick={() => fetchCameraFeeds()}
            >
              Refresh
            </Button>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : selectedCamera ? (
            <Box>
              <IconButton sx={{ mb: 1 }} onClick={() => setSelectedCamera(null)}>
                ← Back to Feeds
              </IconButton>
              <Typography variant="h6">{selectedCamera.title}</Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {selectedCamera.location_name}, {selectedCamera.country}
              </Typography>
              
              {iframeError ? (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    Unable to load the live feed. This may be due to:
                    <ul style={{ marginTop: 8, marginBottom: 0 }}>
                      <li>The stream is currently offline</li>
                      <li>The video is restricted in your region</li>
                      <li>Network connectivity issues</li>
                    </ul>
                  </Alert>
                  <Button variant="contained" onClick={handleRetry}>
                    Try Again
                  </Button>
                </Box>
              ) : (
                <Box
                  sx={{
                    position: 'relative',
                    paddingBottom: '56.25%',
                    height: 0,
                    overflow: 'hidden',
                    borderRadius: 2,
                    mt: 2,
                    bgcolor: '#000',
                  }}
                >
                  <iframe
                    key={selectedCamera.id}
                    src={selectedCamera.url}
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '100%',
                      border: 'none',
                    }}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    title={selectedCamera.title}
                    onError={() => setIframeError(true)}
                  />
                </Box>
              )}
            </Box>
          ) : (
            <Grid container spacing={2}>
              {filteredFeeds.length === 0 ? (
                <Box sx={{ textAlign: 'center', width: '100%', py: 4 }}>
                  <Typography color="text.secondary">No camera feeds available</Typography>
                </Box>
              ) : (
                filteredFeeds.map((feed) => (
                  <Grid item xs={12} sm={6} md={4} key={feed.id}>
                    <Card
                      sx={{
                        cursor: 'pointer',
                        transition: 'transform 0.2s',
                        '&:hover': { transform: 'scale(1.02)' },
                      }}
                      onClick={() => {
                        setSelectedCamera(feed);
                        setIframeError(false);
                      }}
                    >
                      <CardMedia
                        component="img"
                        height="180"
                        image={feed.thumbnail}
                        alt={feed.title}
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x225?text=Live+Feed';
                        }}
                      />
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="subtitle1" noWrap sx={{ fontWeight: 'bold' }}>
                            {feed.title}
                          </Typography>
                          <Chip
                            label="LIVE"
                            size="small"
                            color="error"
                            sx={{ fontSize: '0.7rem', fontWeight: 'bold' }}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {feed.location_name}, {feed.country}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                          <PlayArrowIcon fontSize="small" color="primary" />
                          <Typography variant="caption" color="primary" sx={{ ml: 0.5 }}>
                            Click to watch
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))
              )}
            </Grid>
          )}
        </Paper>
      </Modal>
    </>
  );
};

export default LiveCameraView;