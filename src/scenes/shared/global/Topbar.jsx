import { Box, IconButton, useTheme, Menu, MenuItem, Badge, Typography, Divider } from "@mui/material";
import { useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ColorModeContext, tokens } from "../../../theme";
import InputBase from "@mui/material/InputBase";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import NotificationsOutlinedIcon from "@mui/icons-material/NotificationsOutlined";
// import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import LogoutIcon from '@mui/icons-material/Logout';
import SearchIcon from "@mui/icons-material/Search";
import { mockNotifications } from "../../../data/mockNotifications";

const Topbar = ({ onLogout }) => {
    const theme = useTheme();
    const navigate = useNavigate();
    const colors = tokens(theme.palette.mode);
    const colorMode = useContext(ColorModeContext);

    // Notification dropdown
    const [notificationAnchor, setNotificationAnchor] = useState(null);
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);

    // Fetch notifications on component mount and poll for updates
    useEffect(() => {
        fetchNotifications();

        // Poll every 5 seconds for new notifications
        const interval = setInterval(fetchNotifications, 5000);

        return () => clearInterval(interval);
    }, []);

    const fetchNotifications = async () => {
        try {
            const response = await fetch('http://localhost:5001/notifications');
            const data = await response.json();

            // Format notifications for display
            const formattedNotifications = data.map(notif => ({
                id: notif.id,
                message: notif.message,
                time: new Date(notif.time).toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: '2-digit'
                }),
                read: notif.read
            }));

            setNotifications(formattedNotifications);
            setUnreadCount(formattedNotifications.filter(n => !n.read).length);
        } catch (error) {
            console.error("Failed to fetch notifications:", error);
            // Fallback to mock data if backend fails
            setNotifications(mockNotifications);
            setUnreadCount(mockNotifications.filter(n => !n.read).length);
        }
    };

    const handleNotificationClick = (event) => {
        setNotificationAnchor(event.currentTarget);
    };

    const handleNotificationClose = () => {
        setNotificationAnchor(null);
    };

    const handleViewAllNotifications = () => {
        setNotificationAnchor(null);
        navigate('/notifications');
    };

    const handleMarkAsRead = async (notificationId) => {
        // Optimistic update
        setNotifications(prev =>
            prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
        );
        setUnreadCount(prev => Math.max(0, prev - 1));

        // Update backend
        try {
            await fetch(`http://localhost:5001/notifications/${notificationId}/read`, {
                method: 'PUT',
            });
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
    };

    const handleLogout = () => {
        // Clear authentication data from localStorage
        localStorage.removeItem('token');
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userRole');
        sessionStorage.clear();

        //Reset to light mode on logout
        if(theme.palette.mode === 'dark'){ colorMode.toggleColorMode();}

        // Call the onLogout prop if provided
        if (onLogout) {
            onLogout();
        }

        // Navigate to login page
        navigate('/login');
    };

    return (
    <Box display="Flex" justifyContent="space-between" p={2}> 
        <IconButton sx={{ display: "flex"}}> </IconButton>
        {/* Search bar */}
        {/* <Box 
            display="Flex"
            backgroundColor={colors.primary[400]}
            borderRadius="3px"
        >
            <InputBase sx={{ ml: 2, flex: 1}} placeholder="Search" />
            <IconButton type="button" sx={{p: 1}}>
                <SearchIcon />
            </IconButton>
        </Box> */}

        {/* Icons */}
        <Box display="flex">
            {/* Change between light/dark */}
            <IconButton onClick={colorMode.toggleColorMode}>
                {theme.palette.mode == 'dark' ? (
                    <DarkModeOutlinedIcon />
                ) : (
                    <LightModeOutlinedIcon />
                )}
            </IconButton>

            <IconButton onClick={handleNotificationClick}>
                <Badge badgeContent={unreadCount} color="error">
                    <NotificationsOutlinedIcon />
                </Badge>
            </IconButton>

            {/* Notification Dropdown Menu */}
            <Menu
                anchorEl={notificationAnchor}
                open={Boolean(notificationAnchor)}
                onClose={handleNotificationClose}
                slotProps={{
                    paper: {
                        sx: {
                            width: 360,
                            maxHeight: 400,
                            backgroundColor: colors.primary[400],
                            boxShadow: `0 4px 6px -1px rgb(0 0 0 / 0.1)`,
                        }
                    }
                }}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
                {/* Header */}
                <Box sx={{ p: 2, borderBottom: `1px solid ${colors.primary[300]}` }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: colors.grey[100] }}>
                        Notifications
                    </Typography>
                    {unreadCount > 0 && (
                        <Typography variant="caption" sx={{ color: colors.green[400] }}>
                            {unreadCount} unread
                        </Typography>
                    )}
                </Box>

                {/* Notification List */}
                {notifications.length === 0 ? (
                    <Box sx={{ p: 3, textAlign: 'center' }}>
                        <Typography sx={{ color: colors.grey[300] }}>
                            No notifications
                        </Typography>
                    </Box>
                ) : (
                    notifications.slice(0, 5).map((notification, index) => (
                        <MenuItem
                            key={notification.id}
                            onClick={() => handleMarkAsRead(notification.id)}
                            sx={{
                                py: 1.5,
                                px: 2,
                                borderBottom: index < notifications.length - 1 ? `1px solid ${colors.primary[300]}` : 'none',
                                backgroundColor: !notification.read ? colors.primary[700] : 'transparent',
                                '&:hover': {
                                    backgroundColor: colors.primary[700],
                                }
                            }}
                        >
                            <Box sx={{ width: '100%' }}>
                                <Typography
                                    sx={{
                                        fontSize: '0.875rem',
                                        color: colors.grey[100],
                                        fontWeight: !notification.read ? 600 : 400,
                                        mb: 0.5
                                    }}
                                >
                                    {notification.message}
                                </Typography>
                                <Typography
                                    sx={{
                                        fontSize: '0.75rem',
                                        color: colors.grey[300]
                                    }}
                                >
                                    {notification.time}
                                </Typography>
                            </Box>
                        </MenuItem>
                    ))
                )}

                {/* View All Footer */}
                {notifications.length > 0 && [
                    <Divider key="divider" sx={{ borderColor: colors.primary[300] }} />,
                    <MenuItem
                        key="view-all"
                        onClick={handleViewAllNotifications}
                        sx={{
                            justifyContent: 'center',
                            py: 1.5,
                            color: colors.green[400],
                            fontWeight: 600,
                            '&:hover': {
                                backgroundColor: colors.primary[500],
                            }
                        }}
                    >
                        View All Notifications
                    </MenuItem>
                ]}
            </Menu>

            {/* <IconButton>
                <SettingsOutlinedIcon />
            </IconButton> */}

            <IconButton onClick={handleLogout}>
                <LogoutIcon />
            </IconButton>
        </Box>
    </Box>
    );
}

export default Topbar;