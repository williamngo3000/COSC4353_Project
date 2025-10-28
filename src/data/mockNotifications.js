// Mock notification data for admin dashboard
// Replace this with real API calls when backend is ready (if firebase is good... T_T)

export const mockNotifications = [
    {
        id: 1,
        message: "New user registered: john@example.com",
        time: "5 minutes ago",
        read: false,
        type: "user"
    },
    {
        id: 2,
        message: "Beach Cleanup event created",
        time: "1 hour ago",
        read: false,
        type: "event"
    },
    {
        id: 3,
        message: "10 volunteers signed up for Food Drive",
        time: "3 hours ago",
        read: true,
        type: "signup"
    },
    {
        id: 4,
        message: "Profile updated by volunteer@example.com",
        time: "5 hours ago",
        read: true,
        type: "profile"
    },
    {
        id: 5,
        message: "New event: Community Garden Planting",
        time: "1 day ago",
        read: true,
        type: "event"
    }
];

// Helper function to get unread count
export const getUnreadCount = (notifications) => {
    return notifications.filter(n => !n.read).length;
};

// Helper function to get recent notifications (limit to X most recent)
export const getRecentNotifications = (notifications, limit = 5) => {
    return notifications.slice(0, limit);
};
