import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../theme";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import EmailIcon from "@mui/icons-material/Email";
import Header from "../../components/Header";

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

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
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          {/* FIRST BOX */}
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
          title?
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            // borderBottom={`4px solid ${colors.primary[500]}`}
            colors={colors.grey[100]}
            p="15px"
          >
          </Box>
          
          <Typography>
            TEMP BODY OF ONE W TITLE; just add title later
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;