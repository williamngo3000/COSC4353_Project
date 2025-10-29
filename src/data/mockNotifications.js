// Mock notification data for admin dashboard

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
