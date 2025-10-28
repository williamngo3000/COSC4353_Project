import { useEffect } from 'react';

const NotificationQueue = ({ notifications, onClose }) => {
    if (!notifications || notifications.length === 0) return null;

    return (
        <div className="notification-container">
            {notifications.map((notification) => (
                <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onClose={() => onClose(notification.id)}
                />
            ))}
        </div>
    );
};

const NotificationItem = ({ notification, onClose }) => {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, 5000); // Auto-dismiss after 5 seconds

        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div className={`notification-popup ${notification.type}`}>
            <p className="notification-message">{notification.message}</p>
            <button onClick={onClose} className="notification-close">&times;</button>
        </div>
    );
};

export default NotificationQueue;
