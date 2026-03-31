import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import { fetchConflictTrends } from '../../services/api';

interface ConflictTrend {
  timestamp: string;
  event_count: number;
  severity_avg: number;
  active_conflicts: number;
}

interface ConflictTrendChartProps {
  days?: number;
  title?: string;
}

const ConflictTrendChart: React.FC<ConflictTrendChartProps> = ({ 
  days = 90, 
  title = "Conflict Trends Over Time" 
}) => {
  const [data, setData] = useState<ConflictTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [granularity, setGranularity] = useState('day');
  const [chartType, setChartType] = useState<'line' | 'area'>('area');
  const [metric, setMetric] = useState<'events' | 'severity' | 'conflicts'>('events');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchConflictTrends(days, granularity);
      setData(result.data || []);
    } catch (err) {
      setError('Failed to load conflict trend data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [days, granularity]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const formatXAxis = (timestamp: string) => {
    const date = new Date(timestamp);
    if (granularity === 'day') return format(date, 'MMM d');
    if (granularity === 'week') return format(date, 'MMM d');
    return format(date, 'MMM yyyy');
  };

  const getYAxisLabel = () => {
    switch (metric) {
      case 'events': return 'Number of Events';
      case 'severity': return 'Average Severity (0-10)';
      case 'conflicts': return 'Active Conflicts';
      default: return '';
    }
  };

  const getChartData = () => {
    return data.map(item => ({
      date: item.timestamp,
      events: item.event_count,
      severity: item.severity_avg,
      conflicts: item.active_conflicts,
    }));
  };

  const getMetricDataKey = () => {
    switch (metric) {
      case 'events': return 'events';
      case 'severity': return 'severity';
      case 'conflicts': return 'conflicts';
      default: return 'events';
    }
  };

  const getMetricColor = () => {
    switch (metric) {
      case 'events': return '#ff6b6b';
      case 'severity': return '#ff8c42';
      case 'conflicts': return '#4ecdc4';
      default: return '#ff6b6b';
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

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 2 }}>
        <Typography variant="h6">{title}</Typography>
        
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Granularity</InputLabel>
            <Select
              value={granularity}
              label="Granularity"
              onChange={(e) => setGranularity(e.target.value)}
            >
              <MenuItem value="day">Daily</MenuItem>
              <MenuItem value="week">Weekly</MenuItem>
              <MenuItem value="month">Monthly</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Metric</InputLabel>
            <Select
              value={metric}
              label="Metric"
              onChange={(e) => setMetric(e.target.value as any)}
            >
              <MenuItem value="events">Event Count</MenuItem>
              <MenuItem value="severity">Severity</MenuItem>
              <MenuItem value="conflicts">Active Conflicts</MenuItem>
            </Select>
          </FormControl>

          <ToggleButtonGroup
            size="small"
            value={chartType}
            exclusive
            onChange={(e, val) => val && setChartType(val)}
          >
            <ToggleButton value="area">Area</ToggleButton>
            <ToggleButton value="line">Line</ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>

      <ResponsiveContainer width="100%" height={400}>
        {chartType === 'area' ? (
          <AreaChart data={getChartData()}>
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis 
              dataKey="date" 
              tickFormatter={formatXAxis}
              interval={granularity === 'day' ? 14 : granularity === 'week' ? 4 : 2}
              stroke="#888"
            />
            <YAxis stroke="#888" label={{ value: getYAxisLabel(), angle: -90, position: 'insideLeft' }} />
            <Tooltip
              labelFormatter={(label) => format(new Date(label), 'MMMM d, yyyy')}
              contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #333' }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey={getMetricDataKey()}
              stroke={getMetricColor()}
              fill={getMetricColor()}
              fillOpacity={0.3}
              name={metric === 'events' ? 'Events' : metric === 'severity' ? 'Avg Severity' : 'Active Conflicts'}
            />
          </AreaChart>
        ) : (
          <LineChart data={getChartData()}>
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis 
              dataKey="date" 
              tickFormatter={formatXAxis}
              interval={granularity === 'day' ? 14 : granularity === 'week' ? 4 : 2}
              stroke="#888"
            />
            <YAxis stroke="#888" label={{ value: getYAxisLabel(), angle: -90, position: 'insideLeft' }} />
            <Tooltip
              labelFormatter={(label) => format(new Date(label), 'MMMM d, yyyy')}
              contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #333' }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey={getMetricDataKey()}
              stroke={getMetricColor()}
              strokeWidth={2}
              dot={granularity !== 'day'}
              name={metric === 'events' ? 'Events' : metric === 'severity' ? 'Avg Severity' : 'Active Conflicts'}
            />
          </LineChart>
        )}
      </ResponsiveContainer>

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', color: 'text.secondary' }}>
        <Typography variant="caption">
          Total events: {data.reduce((sum, d) => sum + d.event_count, 0).toLocaleString()}
        </Typography>
        <Typography variant="caption">
          Peak: {Math.max(...data.map(d => d.event_count)).toLocaleString()} events
        </Typography>
        <Typography variant="caption">
          Avg severity: {(data.reduce((sum, d) => sum + d.severity_avg, 0) / data.length).toFixed(1)}/10
        </Typography>
      </Box>
    </Paper>
  );
};

export default ConflictTrendChart;