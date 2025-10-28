import { useState, useEffect } from 'react';
import { Box, Checkbox, useTheme } from "@mui/material";
import { tokens } from "../../../theme";
import PersonIcon from '@mui/icons-material/Person';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';

const AdminNotifications = ({ addNotification }) => {
    const theme = useTheme();
    const colors = tokens(theme.palette.mode);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        totalEvents: 0,
        upcomingEvents: 0,
        totalVolunteers: 0,
        recentRegistrations: 0
    });
    const [recentActivity, setRecentActivity] = useState([]);
    const [userNames, setUserNames] = useState({}); // Cache for email -> name mapping

    useEffect(() => {
        fetchAdminStats();

        // Poll for updates every 10 seconds
        const interval = setInterval(fetchAdminStats, 10000);

        return () => clearInterval(interval);
    }, []);

    const fetchAdminStats = async () => {
        try {
            // Placeholder - Need to implement these endpoints in Flask later on if we push to Reclaim
            const eventsRes = await fetch('http://localhost:5001/events');
            const usersRes = await fetch('http://localhost:5001/users');

            if (!eventsRes.ok || !usersRes.ok) {
                throw new Error('Failed to fetch statistics');
            }

            const events = await eventsRes.json();
            const users = await usersRes.json();

            // Build email -> name mapping
            const nameMapping = {};
            users.forEach(user => {
                nameMapping[user.email] = user.name || user.email;
            });
            setUserNames(nameMapping);

            // Calculate stats
            const now = new Date();
            const upcomingEvents = events.filter(event => new Date(event.event_date) >= now);

            setStats({
                totalEvents: events.length,
                upcomingEvents: upcomingEvents.length,
                totalVolunteers: users.length,
                recentRegistrations: users.filter(u => {
                    // Placeholder: filter users registered in last 7 days
                    // You'll need to add registration_date to your user model
                    return true;
                }).length
            });

            // Fetch real activity data from backend
            const activityRes = await fetch('http://localhost:5001/activity');
            const activity = await activityRes.json();

            // Format activity data for display
            const formattedActivity = activity.map(act => ({
                type: act.type,
                user: act.user,
                event: act.event,
                time: new Date(act.time).toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: '2-digit'
                })
            }));

            setRecentActivity(formattedActivity);

        } catch (error) {
            addNotification(error.message || 'Failed to load statistics', 'error');
        } finally {
            setLoading(false);
        }
    };

    const StatCard = ({ title, value, color }) => (
        <Box
            sx={{
                padding: '1.5rem',
                borderRadius: '0.5rem',
                backgroundColor: colors.primary[400],
                border: `1px solid ${colors.primary[300]}`
            }}
        >
            <h4 style={{ fontSize: '0.875rem', color: colors.grey[100], marginBottom: '0.5rem' }}>
                {title}
            </h4>
            <p style={{ fontSize: '2rem', fontWeight: '700', color: color || colors.green[500] }}>
                {value}
            </p>
        </Box>
    );

    const ActivityItem = ({ activity }) => {
        const getActivityIcon = (type) => {
            switch(type) {
                case 'registration': return <PersonIcon />;
                case 'event_signup': return <CheckBoxIcon />;
                case 'event_created': return <CalendarMonthIcon />;
                default: return <span></span>;
            }
        };

        const getActivityText = (activity) => {
            const userName = userNames[activity.user];
            const userDisplay = userName && userName !== activity.user
                ? `${userName} (${activity.user})`
                : activity.user;

            switch(activity.type) {
                case 'registration':
                    return `New user registered: ${userDisplay}`;
                case 'event_signup':
                    return `${userDisplay} signed up for ${activity.event}`;
                case 'event_created':
                    return `New event created: ${activity.event}`;
                default:
                    return 'Activity';
            }
        };

        return (
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '1rem',
                    borderBottom: `1px solid ${colors.primary[300]}`,
                    '&:last-child': {
                        borderBottom: 'none'
                    }
                }}
            >
                <Box sx={{ fontSize: '1.5rem', marginRight: '1rem', display: 'flex', alignItems: 'center' }}>
                    {getActivityIcon(activity.type)}
                </Box>
                <div style={{ flex: 1 }}>
                    <p style={{ color: colors.grey[100], marginBottom: '0.25rem' }}>
                        {getActivityText(activity)}
                    </p>
                    <p style={{ fontSize: '0.75rem', color: colors.grey[300] }}>
                        {activity.time}
                    </p>
                </div>
            </Box>
        );
    };

    if (loading) {
        return (
            <Box m="20px">
                <h2 style={{ color: colors.grey[100] }}>Loading notifications...</h2>
            </Box>
        );
    }

    return (
        <Box m="20px">
            <Box display="flex" justifyContent="space-between" alignItems="center" mb="30px">
                <Box>
                    <h2 style={{ color: colors.grey[100], fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem' }}>
                        Admin Notifications
                    </h2>
                    <p style={{ color: colors.green[400] }}>
                        System overview and recent activity
                    </p>
                </Box>
            </Box>

            {/* Statistics Cards */}
            <Box
                display="grid"
                gridTemplateColumns="repeat(4, 1fr)"
                gap="20px"
                mb="30px"
            >
                <StatCard
                    title="Total Events"
                    value={stats.totalEvents}
                    color={colors.indigo[500]}
                />
                <StatCard
                    title="Upcoming Events"
                    value={stats.upcomingEvents}
                    color={colors.green[500]}
                />
                <StatCard
                    title="Total Volunteers"
                    value={stats.totalVolunteers}
                    color={colors.primary[100]}
                />
                <StatCard
                    title="Recent Registrations"
                    value={stats.recentRegistrations}
                    color={colors.red[500]}
                />
            </Box>

            {/* Recent Activity */}
            <Box
                sx={{
                    backgroundColor: colors.primary[400],
                    borderRadius: '0.5rem',
                    border: `1px solid ${colors.primary[300]}`
                }}
            >
                <Box p="20px" borderBottom={`1px solid ${colors.primary[300]}`}>
                    <h3 style={{ color: colors.grey[100], fontSize: '1.25rem', fontWeight: '600' }}>
                        Recent Activity
                    </h3>
                </Box>

                {recentActivity.length === 0 ? (
                    <Box p="40px" textAlign="center">
                        <p style={{ color: colors.grey[300] }}>No recent activity</p>
                    </Box>
                ) : (
                    <Box>
                        {recentActivity.map((activity, index) => (
                            <ActivityItem key={index} activity={activity} />
                        ))}
                    </Box>
                )}
            </Box>

            {/* System Alerts Section - Expand if needed */}
            <Box
                mt="30px"
                sx={{
                    backgroundColor: colors.primary[400],
                    borderRadius: '0.5rem',
                    border: `1px solid ${colors.primary[300]}`,
                    padding: '1.5rem'
                }}
            >
                <h3 style={{ color: colors.grey[100], fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
                    System Alerts
                </h3>
                <p style={{ color: colors.grey[300] }}>
                    No system alerts at this time. This section will display important notifications about events, user activity, and system status.
                </p>

                {/* Template for future alerts */}
                <Box mt="1rem" p="1rem" sx={{ backgroundColor: colors.primary[400], borderRadius: '0.375rem' }}>
                    <p style={{ color: colors.grey[200], fontSize: '0.875rem' }}>
                        <strong>(Placeholder text here)</strong>
                    </p>
                </Box>
            </Box>
        </Box>
    );
};

export default AdminNotifications;
