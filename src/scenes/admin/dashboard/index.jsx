import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../../theme";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import EmailIcon from "@mui/icons-material/Email";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
import Header from "../../../components/Header";
import { useState, useEffect } from "react";

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [pendingRequests, setPendingRequests] = useState([]);

  const fetchPendingRequests = async () => {
    try {
      const response = await fetch('http://localhost:5001/invites?status=pending&type=user_request');
      if (!response.ok) {
        throw new Error('Failed to fetch pending requests');
      }
      const data = await response.json();

      // Enrich with event details
      const enrichedRequests = await Promise.all(
        data.map(async (request) => {
          try {
            const eventRes = await fetch(`http://localhost:5001/events/${request.event_id}`);
            if (eventRes.ok) {
              const event = await eventRes.json();
              return { ...request, event };
            }
          } catch (err) {
            console.error('Error fetching event details:', err);
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
    // Initial fetch
    fetchPendingRequests();

    // Polling every 5 seconds
    const interval = setInterval(fetchPendingRequests, 5000);

    return () => clearInterval(interval);
  }, []);

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

      // Optimistic update
      setPendingRequests(prev => prev.filter(req => req.id !== inviteId));
      console.log('Request approved successfully');
    } catch (error) {
      console.error('Error approving request:', error);
      alert('Failed to approve request. Please try again.');
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

      // Optimistic update
      setPendingRequests(prev => prev.filter(req => req.id !== inviteId));
      console.log('Request rejected successfully');
    } catch (error) {
      console.error('Error rejecting request:', error);
      alert('Failed to reject request. Please try again.');
    }
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
        {/* ROW 1 */}
        {/* <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        > */}
          {/* FIRST BOX */}
          {/* <Typography>
            TEMP PLACEHOLDER
          </Typography>

        </Box>
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Typography>
            TEMP PLACEHOLDER
          </Typography>

        </Box>
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Typography>
            TEMP PLACEHOLDER
          </Typography>

        </Box>
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Typography>
            TEMP PLACEHOLDER
          </Typography>

        </Box> */} 


        {/* ROW 2 */}
        <Box
          gridColumn="span 8"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
        >
          <Box
            mt="25px"
            p="0 30px"
            display="flex "
            justifyContent="space-between"
            alignItems="center"
          >
            <Box>
              <Typography
                variant="h3"
                fontWeight="600"
                color={colors.grey[100]}
              >
                REPORT
              </Typography>
              <Typography
                variant="h5"
                fontWeight="bold"
                color={colors.grey[100]}
              >
                Have some form of report here for admins to download user information on volunteering + their history
              </Typography>
            </Box>
            <Box>
              <IconButton>
                {/* Button here to download files as listed in the "Complete Project with Demo */}
                <DownloadOutlinedIcon
                  sx={{ fontSize: "26px", color: colors.green[500] }}
                />
              </IconButton>
            </Box>
          </Box>
          <Typography
            fontWeight="bold"
            fontSize={20}
            mt="25px"
            p="0 250px"
            display="flex"
            justifyContent="space-between"
            alignItems="center"
          >
            Maybe preview of table here?
          </Typography>
        </Box>
        <Box
          gridColumn="span 4"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
          overflow="auto"
        >
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            borderBottom={`4px solid ${colors.primary[500]}`}
            colors={colors.grey[100]}
            p="15px"
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
                  <Typography color={colors.green[500]} fontWeight="600">
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
                      color: colors.green[500],
                      '&:hover': { backgroundColor: colors.green[700] }
                    }}
                    title="Approve request"
                  >
                    <CheckCircleIcon />
                  </IconButton>
                  <IconButton
                    onClick={() => handleReject(request.id)}
                    sx={{
                      color: colors.red[500],
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