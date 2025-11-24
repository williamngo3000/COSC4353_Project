import { 
  Box, 
  Button, 
  IconButton, 
  Typography, 
  useTheme,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress
} from "@mui/material";
// import { tokens } from "../../../theme"; // Mocked below
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import EmailIcon from "@mui/icons-material/Email";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
// import Header from "../../../components/Header"; // Mocked below
import { useState, useEffect } from "react";


const tokens = (mode) => {
  const isDarkMode = mode === 'dark';
  

  const primaryLight = '#F9FAFB'; 
  const primaryDark = '#1F2A40';  

  return {
    grey: {
      100: isDarkMode ? '#f0f0f0' : '#333333', 
      300: isDarkMode ? '#cecece' : '#555555',
      400: isDarkMode ? '#a3a3a3' : '#777777',
      500: isDarkMode ? '#666666' : '#999999', 
    },

    // This will change the main "squares" based on the mode
    primary: {
      400: isDarkMode ? primaryDark : primaryLight, 
      500: isDarkMode ? '#2a2d6e' : '#E0E0E0',
      600: isDarkMode ? '#1F2A40' : '#F5F5F5', 
    },
    // --- RESTORED ORIGINAL GREEN ---
    green: {
      500: '#4cceac',
      600: '#389e83',
      700: '#2f846d',
    },
    // --- RESTORED ORIGINAL BLUE ---
    blue: {
      500: '#2196f3',
      600: '#1e88e5',
    },
    // Kept original red for "Reject" / "Danger" actions
    red: {
      500: '#f44336', 
      700: '#d32f2f',
    },
  };
};

const Header = ({ title, subtitle }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  return (
    <Box mb="20px">
      <Typography
        variant="h2"
        color={colors.grey[100]} 
        fontWeight="bold"
        sx={{ mb: "5px" }}
      >
        {title}
      </Typography>
      <Typography variant="h5" color={colors.green[500]}> {/* Will be GREEN */}
        {subtitle}
      </Typography>
    </Box>
  );
};

// --- ReportPreviewTable ---
const ReportPreviewTable = ({ data, isLoading, colors }) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress sx={{ color: colors.green[500] }} /> {/* Will be GREEN */}
      </Box>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Box p="15px" textAlign="center">
        <Typography color={colors.grey[300]}>
          No data to display for this report.
        </Typography>
      </Box>
    );
  }

  // Get all unique headers from the first item
  const headers = Object.keys(data[0]);

  return (
    <TableContainer 
      component={Paper} 
      sx={{ 
        backgroundColor: 'transparent',
        boxShadow: 'none',
        maxHeight: '200px', // Make table scrollable
        overflow: 'auto',
      }}
    >
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            {headers.map((header) => (
              <TableCell
                key={header}
                sx={{
                  backgroundColor: isDarkMode ? colors.primary[500] : '#E0E0E0', // Darker header for both modes
                  color: colors.grey[100],
                  fontWeight: 'bold',
                  borderBottom: `2px solid ${colors.green[500]}`, // Will be GREEN
                }}
              >
                {header}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row, rowIndex) => (
            <TableRow 
              key={rowIndex} 
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              {headers.map((header) => (
                <TableCell 
                  key={`${rowIndex}-${header}`}
                  sx={{ 
                    color: colors.grey[300],
                    borderBottom: `1px solid ${colors.primary[500]}`, // Border color
                  }}
                >
                  {row[header]}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};


const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [pendingRequests, setPendingRequests] = useState([]);
  
  // --- NEW STATE FOR REPORT PREVIEW ---
  const [reportTabValue, setReportTabValue] = useState(0);
  const [reportData, setReportData] = useState([]);
  const [isLoadingReport, setIsLoadingReport] = useState(false);

  // --- NEW: Generate today's date string for filenames ---
  const todayStr = new Date().toISOString().split('T')[0]; // Format: YYYY-MM-DD

  // --- THIS FUNCTION IS NOW FULLY SUPPORTED BY THE BACKEND ---
  const fetchPendingRequests = async () => {
    try {
      const response = await fetch('http://localhost:5001/invites?status=pending&type=user_request');
      if (!response.ok) {
        throw new Error('Failed to fetch pending requests');
      }
      const data = await response.json();

      const enrichedRequests = await Promise.all(
        data.map(async (request) => {
          try {
            const eventRes = await fetch(`http://localhost:5001/events/${request.event_id}`);
            if (eventRes.ok) {
              const event = await eventRes.json();
              return { ...request, event };
            }
          } catch (err) {
            console.error(`Error fetching event details for event ${request.event_id}:`, err);
          }
          return request;
        })
      );

      setPendingRequests(enrichedRequests);
    } catch (error) {
      console.error('Error fetching pending requests:', error);
    }
  };

  useEffect(() => {
    fetchPendingRequests();
    const interval = setInterval(fetchPendingRequests, 5000);
    return () => clearInterval(interval);
  }, []);

  // --- NEW EFFECT FOR FETCHING REPORT DATA ---
  useEffect(() => {
    const fetchReportData = async () => {
      setIsLoadingReport(true);
      setReportData([]); // Clear previous data
      
      let endpoint = '';
      if (reportTabValue === 0) {
        endpoint = 'http://localhost:5001/reports/json/volunteer_history';
      } else {
        endpoint = 'http://localhost:5001/reports/json/event_assignments';
      }
      
      try {
        const response = await fetch(endpoint);
        if (!response.ok) {
          throw new Error('Failed to fetch report data');
        }
        const data = await response.json();
        setReportData(data);
      } catch (error) {
        console.error('Error fetching report data:', error);
      } finally {
        setIsLoadingReport(false);
      }
    };
    
    fetchReportData();
  }, [reportTabValue]); // Re-fetch when the tab changes

  const handleApprove = async (inviteId) => {
    try {
      const response = await fetch(`http://localhost:5001/invites/${inviteId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'accepted' }),
      });

      if (!response.ok) {
        throw new Error('Failed to approve request');
      }
      setPendingRequests(prev => prev.filter(req => req.id !== inviteId));
      console.log('Request approved successfully');
    } catch (error) {
      console.error('Error approving request:', error);
    }
  };

  const handleReject = async (inviteId) => {
    try {
      const response = await fetch(`http://localhost:5001/invites/${inviteId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'declined' }),
      });

      if (!response.ok) {
        throw new Error('Failed to reject request');
      }
      setPendingRequests(prev => prev.filter(req => req.id !== inviteId));
      console.log('Request rejected successfully');
    } catch (error)
    {
      console.error('Error rejecting request:', error);
    }
  };
  
  // --- Handle Tab Change ---
  const handleTabChange = (event, newValue) => {
    setReportTabValue(newValue);
  };

  return (
    <Box m="20px" sx={{ fontFamily: 'sans-serif'}}>
      {/* HEADER */}
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Header title="DASHBOARD" subtitle="Welcome to your dashboard"/>
        <Box />
      </Box>
      
      {/* GRID & BOXES ON DASHBOARD MAIN */}
      <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="140px"
        gap="20px"
      >
        {/* ROW 1 (Commented out as per your file) */}

        {/* --- ROW 2: REPORT BOX (NOW TALLER & THEME-AWARE) --- */}
        <Box
          gridColumn="span 8"
          gridRow="span 4" // --- INCREASED HEIGHT to span 4 rows
          backgroundColor={colors.primary[400]} // Will be LIGHT or DARK
          p="20px"
          display="flex"
          flexDirection="column"
          borderRadius="8px" // Added border radius
        >
          {/* --- REPORT HEADER --- */}
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mb="10px"
          >
            <Box>
              <Typography
                variant="h3"
                fontWeight="600"
                color={colors.grey[100]} // Correct text color
              >
                REPORTS
              </Typography>
              <Typography
                variant="h5"
                fontWeight="bold"
                color={colors.grey[100]} // Correct text color
              >
                Preview data and download reports.
              </Typography>
            </Box>
            
            {/* --- DOWNLOAD BUTTONS --- */}
            <Box display="flex" gap="10px">
              <a 
                href="http://localhost:5001/reports/volunteer_history.csv" 
                download={`volunteer_history_${todayStr}.csv`}
                style={{ textDecoration: 'none' }}
              >
                <Button
                  variant="contained"
                  sx={{
                    backgroundColor: colors.green[500], // GREEN
                    color: '#FFFFFF', // White text on buttons
                    '&:hover': { backgroundColor: colors.green[600] },
                    fontWeight: 'bold',
                    padding: '6px 16px',
                  }}
                  startIcon={<DownloadOutlinedIcon />}
                >
                  DOWNLOAD VOLUNTEER HISTORY
                </Button>
              </a>
              <a 
                href="http://localhost:5001/reports/event_assignments.csv" 
                download={`event_assignments_${todayStr}.csv`}
                style={{ textDecoration: 'none' }}
              >
                <Button
                  variant="contained"
                  sx={{
                    backgroundColor: colors.blue[500], // BLUE
                    color: '#FFFFFF', // White text on buttons
                    '&:hover': { backgroundColor: colors.blue[600] },
                    fontWeight: 'bold',
                    padding: '6px 16px',
                  }}
                  startIcon={<DownloadOutlinedIcon />}
                >
                  DOWNLOAD EVENT ASSIGNMENTS
                </Button>
              </a>
            </Box>
          </Box>
          
          {/* --- NEW: REPORT PREVIEW TABS (Indicator will be GREEN) --- */}
          <Box sx={{ borderBottom: 1, borderColor: colors.primary[500] }}>
            <Tabs 
              value={reportTabValue} 
              onChange={handleTabChange} 
              aria-label="Report preview tabs"
              textColor="inherit"
              TabIndicatorProps={{ style: { backgroundColor: colors.green[500] } }} // GREEN
              sx={{ color: colors.grey[300] }}
            >
              <Tab label="Volunteer History Preview" sx={{ color: colors.grey[100] }} />
              <Tab label="Event Assignments Preview" sx={{ color: colors.grey[100] }} />
            </Tabs>
          </Box>
          
          {/* --- NEW: PREVIEW TABLE (Fills remaining space) --- */}
          <Box
            mt="10px"
            flex="1" // This makes the box fill the remaining space
            overflow="hidden" // Prevents its children from overflowing the grid
          >
            <ReportPreviewTable 
              data={reportData} 
              isLoading={isLoadingReport} 
              colors={colors} 
            />
          </Box>

        </Box>
        
        {/* --- PENDING REQUESTS BOX  --- */}
        <Box
          gridColumn="span 4"
          gridRow="span 4" // --- INCREASED HEIGHT to span 4 rows
          backgroundColor={colors.primary[400]} // Will be LIGHT or DARK
          overflow="auto"
          borderRadius="8px" // Added border radius
        >
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            borderBottom={`4px solid ${colors.primary[500]}`}
            colors={colors.grey[100]}
            p="15px"
            sx={{ 
              position: "sticky", 
              top: 0, 
              zIndex: 1, 
              backgroundColor: colors.primary[400] // Match background
            }}
          >
            <Typography variant="h5" fontWeight="600" color={colors.grey[100]}>
              Pending Requests
            </Typography>
            <Typography variant="h6" color={colors.grey[300]}>
              {pendingRequests.length}
            </Typography>
          </Box>

          {pendingRequests.length === 0 ? (
            <Box p="15px" textAlign="center">
              <Typography color={colors.grey[300]}>
                No pending requests
              </Typography>
            </Box>
          ) : (
            pendingRequests.map((request) => (
              <Box
                key={request.id}
                display="flex"
                justifyContent="space-between"
                alignItems="center"
                borderBottom={`1px solid ${colors.primary[500]}`}
                p="15px"
              >
                <Box flex="1">
                  <Typography color={colors.green[500]} fontWeight="600"> {/* GREEN */}
                    {request.user_email}
                  </Typography>
                  <Typography variant="body2" color={colors.grey[300]}>
                    {request.event?.event_name || `Event #${request.event_id}`}
                  </Typography>
                  {request.event?.event_date && (
                    <Typography variant="caption" color={colors.grey[400]}>
                      {new Date(request.event.event_date).toLocaleDateString()}
                    </Typography>
                  )}
                </Box>
                <Box display="flex" gap="5px">
                  <IconButton
                    onClick={() => handleApprove(request.id)}
                    sx={{
                      color: colors.green[500], // GREEN
                      '&:hover': { backgroundColor: colors.green[700] }
                    }}
                    title="Approve request"
                  >
                    <CheckCircleIcon />
                  </IconButton>
                  <IconButton
                    onClick={() => handleReject(request.id)}
                    sx={{
                      color: colors.red[500], // Stays danger red
                      '&:hover': { backgroundColor: colors.red[700] }
                    }}
                    title="Reject request"
                  >
                    <CancelIcon />
                  </IconButton>
                </Box>
              </Box>
            ))
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
