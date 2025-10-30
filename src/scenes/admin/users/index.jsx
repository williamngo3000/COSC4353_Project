import { Box, Typography, useTheme, IconButton, Select, MenuItem, Dialog, DialogTitle, DialogContent, DialogActions, Button } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../theme";
// import { mockDataUsers } from "../../../data/mockDataUsers";
import AdminPanelSettingsOutlinedIcon from "@mui/icons-material/AdminPanelSettingsOutlined";
import LockOpenOutlinedIcon from "@mui/icons-material/LockOpenOutlined";
import SecurityOutlinedIcon from "@mui/icons-material/SecurityOutlined";
import DeleteIcon from "@mui/icons-material/Delete";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import Header from "../../../components/Header";
import { useState, useEffect } from "react";

const Users = ({ addNotification }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [rows, setRows] = useState([]);
  const [currentUserEmail, setCurrentUserEmail] = useState("");
  const [events, setEvents] = useState([]);
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState("");

  // Get current logged-in user's email
  useEffect(() => {
    const userEmail = localStorage.getItem('userEmail');
    console.log('Current logged-in user email:', userEmail);
    if (userEmail) {
      setCurrentUserEmail(userEmail);
    }
  }, []);

  // Fetch users from backend
  const fetchUsers = () => {
    fetch('http://localhost:5001/users')
      .then(res => res.json())
      .then(data => {
        setRows(data);
      })
      .catch(err => console.error('Failed to load users:', err));
  };

  // Fetch events for invite dropdown
  const fetchEvents = () => {
    fetch('http://localhost:5001/events?only_open=true')
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        console.log('Fetched events for invite dialog:', data);
        setEvents(data);
      })
      .catch(err => console.error('Failed to load events:', err));
  };

  useEffect(() => {
    // Initial fetch
    fetchUsers();
    fetchEvents();

    // Updates users every 3 sec
    const interval = setInterval(fetchUsers, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleDelete = async (email) => {
    // Optimistic purposes
    const deletedRow = rows.find(row => row.email === email);
    setRows(rows.filter((row) => row.email !== email));

    try {
      const response = await fetch(`http://localhost:5001/users/${email}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete user');
      }

      console.log('User deleted successfully');
    } catch (error) {
      console.error('Error deleting user:', error);
      setRows(prevRows => [...prevRows, deletedRow]);
      addNotification('Failed to delete user. Please try again.', 'error');
    }
  };

  const handleCellEdit = async (updatedRow) => {
    // Optimistic purposes
    const originalRow = rows.find(row => row.id === updatedRow.id);
    setRows(rows.map((row) => (row.id === updatedRow.id ? updatedRow : row)));

    try {
      const response = await fetch(`http://localhost:5001/users/${updatedRow.email}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: updatedRow.name,
          role: updatedRow.role,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update user');
      }

      console.log('User updated successfully');
    } catch (error) {
      console.error('Error updating user:', error);
      setRows(rows.map((row) => (row.id === updatedRow.id ? originalRow : row)));
      addNotification('Failed to update user. Please try again.', 'error');
    }

    return updatedRow;
  };

  const handleRoleChange = async (email, newRole) => {
    const originalRows = [...rows];
    setRows(rows.map(row => row.email === email ? { ...row, role: newRole } : row));

    try {
      const response = await fetch(`http://localhost:5001/users/${email}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole }),
      });

      if (!response.ok) {
        throw new Error('Failed to update role');
      }

      console.log('Role updated successfully');
    } catch (error) {
      console.error('Error updating role:', error);
      setRows(originalRows);
      addNotification('Failed to update role. Please try again.', 'error');
    }
  };

  const handleInviteClick = (user) => {
    setSelectedUser(user);
    setInviteDialogOpen(true);
  };

  const handleInviteSubmit = async () => {
    if (!selectedEvent) {
      addNotification('Please select an event', 'error');
      return;
    }

    try {
      const response = await fetch('http://localhost:5001/invites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_id: selectedEvent,
          user_email: selectedUser.email,
          type: 'admin_invite'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send invite');
      }

      addNotification(`Invite sent to ${selectedUser.name}`, 'success');
      setInviteDialogOpen(false);
      setSelectedEvent("");
    } catch (error) {
      console.error('Error sending invite:', error);
      addNotification('Failed to send invite. Please try again.', 'error');
    }
  };

  const columns = [
    {
      field: "id",
      headerName: "ID",
      editable: false,
    },
    {
      field: "name",
      headerName: "Name",
      flex: 1,
      cellClassName: "name-column--cell",
      editable: true,
    },
    {
      field: "phone",
      headerName: "Phone Number",
      flex: 1,
      editable: true,
    },
    {
      field: "email",
      headerName: "Email",
      flex: 1,
      editable: true,
    },
    {
      field: "role",
      headerName: "Access Level",
      flex: 1,
      renderCell: ({ row }) => {
        return (
          <Select
            value={row.role}
            onChange={(e) => handleRoleChange(row.email, e.target.value)}
            size="small"
            sx={{
              width: "100%",
              backgroundColor: row.role === "admin" ? colors.green[600] : colors.green[700],
              color: colors.grey[100],
              '& .MuiSelect-icon': { color: colors.grey[100] },
              '& .MuiOutlinedInput-notchedOutline': { border: 'none' },
            }}
          >
            <MenuItem value="volunteer">
              <Box display="flex" alignItems="center">
                <LockOpenOutlinedIcon sx={{ mr: 1 }} />
                Volunteer
              </Box>
            </MenuItem>
            <MenuItem value="admin">
              <Box display="flex" alignItems="center">
                <AdminPanelSettingsOutlinedIcon sx={{ mr: 1 }} />
                Admin
              </Box>
            </MenuItem>
          </Select>
        );
      },
    },
    {
      field: "invite",
      headerName: "Invite",
      width: 100,
      sortable: false,
      filterable: false,
      renderCell: (params) => (
        <IconButton
          onClick={() => handleInviteClick(params.row)}
          sx={{ color: colors.green[500] }}
          title="Invite to event"
        >
          <PersonAddIcon />
        </IconButton>
      ),
    },
    {
      field: "actions",
      headerName: "Actions",
      width: 100,
      sortable: false,
      filterable: false,
      renderCell: (params) => {
        const isCurrentUser = params.row.email === currentUserEmail;
        return (
          <IconButton
            onClick={() => handleDelete(params.row.email)}
            disabled={isCurrentUser}
            sx={{
              color: isCurrentUser ? colors.grey[500] : colors.red[500],
              cursor: isCurrentUser ? 'not-allowed' : 'pointer',
              '&.Mui-disabled': {
                color: colors.grey[500],
              }
            }}
            title={isCurrentUser ? "Cannot delete your own account" : "Delete user"}
          >
            <DeleteIcon />
          </IconButton>
        );
      },
    },
  ];

  return (
    <Box m="20px" fontFamily={"sans-serif"}>
      <Header title="Users" subtitle="Managing Users" />
      <Box
        m="40px 0 0 0"
        height="75vh"
        sx={{
          "& .MuiDataGrid-root": {
            border: "none",
            fontFamily: "sans-serif"
          },
          "& .MuiDataGrid-cell": {
            borderBottom: "none",
          },
          "& .MuiDataGrid-cell:focus": {
            outline: "none !important",
          },
          "& .MuiDataGrid-cell:focus-within": {
            outline: "none !important",
          },
          "& .MuiDataGrid-row:focus": {
            outline: "none !important",
          },
          "& .MuiDataGrid-row:focus-within": {
            outline: "none !important",
          },
          "& .MuiDataGrid-columnHeader:focus": {
            outline: "none !important",
          },
          "& .MuiDataGrid-columnHeader:focus-within": {
            outline: "none !important",
          },
          "& .name-column--cell": {
            color: colors.green[300],
          },
          "& .MuiDataGrid-columnHeaders": {
            backgroundColor: colors.indigo[700],
            borderBottom: "none",
          },
          "& .MuiDataGrid-virtualScroller": {
            backgroundColor: colors.primary[400],
          },
          "& .MuiDataGrid-footerContainer": {
            backgroundColor: colors.primary[400],
            borderTop: "none"
          },
          "& .MuiCheckbox-root": {
            color: `${colors.green[200]} !important`,
          },
        }}
      >
        <DataGrid
          checkboxSelection
          rows={rows}
          columns={columns}
          processRowUpdate={handleCellEdit}
          onProcessRowUpdateError={(error) => console.error(error)}
        />
      </Box>

      {/* Invite Dialog */}
      <Dialog
        open={inviteDialogOpen}
        onClose={() => setInviteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        slotProps={{
          paper: {
            sx: {
              backgroundColor: colors.primary[400],
              backgroundImage: 'none',
              minWidth: '400px'
            }
          }
        }}
      >
        <DialogTitle sx={{ backgroundColor: colors.primary[400], color: colors.grey[100] }}>
          Invite {selectedUser?.name} to Event
        </DialogTitle>
        <DialogContent sx={{ backgroundColor: colors.primary[400], mt: 2, pb: 2 }}>
          {events.length === 0 ? (
            <Typography sx={{ color: colors.grey[100], textAlign: 'center', py: 2 }}>
              No events available. Please create an event first.
            </Typography>
          ) : (
            <Select
              value={selectedEvent}
              onChange={(e) => setSelectedEvent(e.target.value)}
              fullWidth
              displayEmpty
              renderValue={(selected) => {
                if (!selected) {
                  return <span style={{ color: colors.grey[300] }}>Select an event</span>;
                }
                const selectedEvent = events.find(e => e.id === selected);
                return selectedEvent ? `${selectedEvent.event_name} - ${selectedEvent.event_date}` : '';
              }}
              sx={{
                color: colors.grey[100],
                backgroundColor: colors.primary[400],
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: colors.grey[100],
                  borderWidth: '2px'
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: colors.grey[100]
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: colors.indigo[500]
                },
                '& .MuiSelect-icon': {
                  color: colors.grey[100]
                }
              }}
              MenuProps={{
                PaperProps: {
                  sx: {
                    backgroundColor: colors.primary[400],
                    backgroundImage: 'none',
                    '& .MuiMenuItem-root': {
                      color: colors.grey[100],
                      '&:hover': {
                        backgroundColor: colors.grey[700]
                      },
                      '&.Mui-selected': {
                        backgroundColor: colors.grey[900],
                        '&:hover': {
                          backgroundColor: colors.grey[700]
                        }
                      },
                      '&.Mui-disabled': {
                        color: colors.grey[100],
                        opacity: 1
                      }
                    }
                  }
                }
              }}
            >
              <MenuItem value="" disabled>Select an event</MenuItem>
              {events.map((event) => (
                <MenuItem key={event.id} value={event.id}>
                  {event.event_name} - {event.event_date}
                </MenuItem>
              ))}
            </Select>
          )}
        </DialogContent>
        <DialogActions sx={{ backgroundColor: colors.primary[400] }}>
          <Button onClick={() => setInviteDialogOpen(false)} sx={{ color: colors.grey[100] }}>
            Cancel
          </Button>
          <Button onClick={handleInviteSubmit} sx={{ color: colors.green[500], fontWeight: 'bold' }}>
            Send Invite
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Users;