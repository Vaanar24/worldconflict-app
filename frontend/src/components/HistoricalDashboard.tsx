import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import ConflictTrendChart from './Charts/ConflictTrendChart';
import CasualtyTrendChart from './Charts/CasualtyTrendChart';
import TerritorialChanges from './TerritorialChanges';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const HistoricalDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [timeRange, setTimeRange] = useState(90);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Paper sx={{ width: '100%', mb: 3 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 2, pt: 2 }}>
        <Typography variant="h5" gutterBottom>
          Historical Analysis Dashboard
        </Typography>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Conflict Trends" />
          <Tab label="Casualty Analysis" />
          <Tab label="Territorial Changes" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value as number)}
            >
              <MenuItem value={30}>Last 30 Days</MenuItem>
              <MenuItem value={90}>Last 90 Days</MenuItem>
              <MenuItem value={180}>Last 6 Months</MenuItem>
              <MenuItem value={365}>Last Year</MenuItem>
            </Select>
          </FormControl>
        </Box>
        <ConflictTrendChart days={timeRange} />
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <CasualtyTrendChart days={timeRange} />
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <TerritorialChanges />
      </TabPanel>
    </Paper>
  );
};

export default HistoricalDashboard;