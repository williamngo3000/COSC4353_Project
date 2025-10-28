import { useState } from "react";
import { ProSidebar, Menu, MenuItem } from "react-pro-sidebar";
import { Box, IconButton, Typography, useTheme } from "@mui/material";
import { Link } from "react-router-dom";
import 'react-pro-sidebar/dist/css/styles.css';
import { tokens } from "../../theme";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import PeopleOutlinedIcon from "@mui/icons-material/PeopleOutlined";
import EventNoteIcon from '@mui/icons-material/EventNote';
import EventIcon from "@mui/icons-material/Event";
import NotificationsOutlinedIcon from "@mui/icons-material/NotificationsOutlined";
import MenuOutlinedIcon from "@mui/icons-material/MenuOutlined";

const Item = ({ title, to, icon, selected, setSelected }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  return (
    <MenuItem
      active={selected === title}
      style={{
        color: colors.grey[100],
      }}
      onClick={() => setSelected(title)}
      icon={icon}
    >
      <Typography fontFamily='sans-serif'>{title}</Typography>
      <Link to={to} />
    </MenuItem>
  );
};

const Sidebar = () => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [isCollapsed, setIsCollapsed] = useState(false);
    const [selected, setSelected] = useState("Dashboard");

    return (
        <Box
            sx={{
                "& .pro-sidebar-inner": {
                background: `${colors.primary[400]} !important`,
                },
                "& .pro-icon-wrapper": {
                backgroundColor: "transparent !important",
                },
                "& .pro-inner-item": {
                padding: "5px 35px 5px 20px !important",
                },
                "& .pro-inner-item:hover": {
                color: "#868dfb !important",
                },
                "& .pro-menu-item.active": {
                color: "#6870fa !important",
                },
            }}
        >
            <ProSidebar collapsed = {isCollapsed}>
                <Menu iconShape="square">
                          {/* LOGO AND MENU ICON */}
                          <MenuItem
                            onClick={() => setIsCollapsed(!isCollapsed)}
                            icon={isCollapsed ? <MenuOutlinedIcon /> : undefined}
                            style={{
                              margin: "10px 0 20px 0",
                              color: colors.grey[100],
                            }}
                          >
                            {!isCollapsed && (
                              <Box
                                display="flex"
                                justifyContent="space-between"
                                alignItems="center"
                                ml="15px"
                              >
                                <Typography variant="h3" color={colors.grey[100]} fontFamily='sans-serif'>
                                  Admin Title Bar
                                </Typography>
                                <IconButton onClick={() => setIsCollapsed(!isCollapsed)}>
                                  <MenuOutlinedIcon />
                                </IconButton>
                              </Box>
                            )}
                          </MenuItem>
                
                          {!isCollapsed && (
                            <Box mb="25px">
                              <Box display="flex" justifyContent="center" alignItems="center">
                                <img
                                  alt="profile-user"
                                  width="100px"
                                  height="100px"
                                  src={`../../assets/evernight.gif`}
                                  style={{ cursor: "pointer", borderRadius: "50%" }}
                                />
                              </Box>
                              <Box textAlign="center">
                                <Typography
                                  variant="h2"
                                  color={colors.grey[100]}
                                  fontWeight="bold"
                                  fontFamily={"sans-serif"}
                                  sx={{ m: "10px 0 0 0" }}
                                >
                                  Insert Admin Name Here
                                </Typography>
                                <Typography variant="h5" color={colors.green[500]} fontFamily='sans-serif'>
                                  xD
                                </Typography>
                              </Box>
                            </Box>
                          )}
                
                          <Box paddingLeft={isCollapsed ? undefined : "10%"}>
                            <Item
                              title="Dashboard"
                              to="/"
                              icon={<HomeOutlinedIcon />}
                              selected={selected}
                              setSelected={setSelected}
                            />
                
                            <Typography
                              variant="h6"
                              color={colors.grey[300]}
                              fontFamily='sans-serif'
                              sx={{ m: "15px 0 5px 20px" }}
                            >
                              Management
                            </Typography>
                            <Item
                              title="Manage Users"
                              to="/Users"
                              icon={<PeopleOutlinedIcon />}
                              selected={selected}
                              setSelected={setSelected}
                            />
                            <Item
                              title="Volunteer Events"
                              to="/events"
                              icon={<EventIcon />}
                              selected={selected}
                              setSelected={setSelected}
                            />
                            <Typography
                                variant="h6"
                                color={colors.grey[300]}
                                fontFamily='sans-serif'
                                sx={{ m: "15px 0 5px 20px" }}
                            >
                                Pages
                            </Typography>
                            <Item
                                title="Event Creation Form"
                                to="/eventmanagement"
                                icon={<EventNoteIcon />}
                                selected={selected}
                                setSelected={setSelected}
                            />
                            <Item
                                title="Notifications"
                                to="/notifications"
                                icon={<NotificationsOutlinedIcon />}
                                selected={selected}
                                setSelected={setSelected}
                            />
            </Box>
        </Menu>
      </ProSidebar>
    </Box>
  );
};

export default Sidebar;