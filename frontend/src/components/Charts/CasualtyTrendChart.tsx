import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Line,
} from 'recharts';
import { format } from 'date-fns';
import { fetchCasualtyTrends } from '../../services/api';

interface CasualtyTrend {
  timestamp: string;
  military_casualties: number;
  civilian_casualties: number;
  total_casualties: number;
}

interface CasualtyTrendChartProps {
  days?: number;
}

const CasualtyTrendChart: React.FC<CasualtyTrendChartProps> = ({ days = 90 }) => {
  const [data, setData] = useState<CasualtyTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartType, setChartType] = useState<'stacked' | 'line'>('stacked');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchCasualtyTrends(days);
      setData(result.data || []);
    } catch (err) {
      setError('Failed to load casualty data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const formatData = () => {
    return data.map(item => ({
      date: item.timestamp,
      military: item.military_casualties,
      civilian: item.civilian_casualties,
      total: item.total_casualties,
    }));
  };

  const totalCasualties = data.reduce((sum, d) => sum + d.total_casualties, 0);
  const civilianPercentage = totalCasualties > 0 
    ? (data.reduce((sum, d) => sum + d.civilian_casualties, 0) / totalCasualties) * 100 
    : 0;

  if (loading) return <Paper sx={{ p: 3, textAlign: 'center' }}><CircularProgress /></Paper>;
  if (error) return <Paper sx={{ p: 3 }}><Alert severity="error">{error}</Alert></Paper>;

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 2 }}>
        <Typography variant="h6">Casualty Trends</Typography>
        
        <ToggleButtonGroup
          size="small"
          value={chartType}
          exclusive
          onChange={(e, val) => val && setChartType(val)}
        >
          <ToggleButton value="stacked">Stacked Bar</ToggleButton>
          <ToggleButton value="line">Line Chart</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <ResponsiveContainer width="100%" height={400}>
        {chartType === 'stacked' ? (
          <BarChart data={formatData()}>
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(date) => format(new Date(date), 'MMM d')}
              interval={Math.floor(data.length / 10)}
              stroke="#888"
            />
            <YAxis stroke="#888" />
            <Tooltip
              labelFormatter={(label) => format(new Date(label), 'MMMM d, yyyy')}
              contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #333' }}
            />
            <Legend />
            <Bar dataKey="civilian" stackId="a" fill="#ff6b6b" name="Civilian Casualties" />
            <Bar dataKey="military" stackId="a" fill="#4ecdc4" name="Military Casualties" />
          </BarChart>
        ) : (
          <ComposedChart data={formatData()}>
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(date) => format(new Date(date), 'MMM d')}
              interval={Math.floor(data.length / 10)}
              stroke="#888"
            />
            <YAxis stroke="#888" />
            <Tooltip
              labelFormatter={(label) => format(new Date(label), 'MMMM d, yyyy')}
              contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #333' }}
            />
            <Legend />
            <Line type="monotone" dataKey="civilian" stroke="#ff6b6b" strokeWidth={2} name="Civilian" />
            <Line type="monotone" dataKey="military" stroke="#4ecdc4" strokeWidth={2} name="Military" />
            <Bar dataKey="total" fill="#ff8c42" opacity={0.3} name="Total" />
          </ComposedChart>
        )}
      </ResponsiveContainer>

      <Box sx={{ mt: 2, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 2 }}>
        <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'rgba(0,0,0,0.3)', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary">Total Casualties</Typography>
          <Typography variant="h6" color="error">{totalCasualties.toLocaleString()}+</Typography>
        </Box>
        <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'rgba(0,0,0,0.3)', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary">Civilian Casualties</Typography>
          <Typography variant="h6" color="warning.main">{civilianPercentage.toFixed(1)}%</Typography>
        </Box>
        <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'rgba(0,0,0,0.3)', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary">Daily Average</Typography>
          <Typography variant="h6">{(totalCasualties / days).toFixed(0)}</Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default CasualtyTrendChart;