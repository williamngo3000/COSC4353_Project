import { Box, Typography, useTheme, IconButton, Select, MenuItem } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../theme";
// import { mockDataUsers } from "../../../data/mockDataUsers";
import AdminPanelSettingsOutlinedIcon from "@mui/icons-material/AdminPanelSettingsOutlined";
import LockOpenOutlinedIcon from "@mui/icons-material/LockOpenOutlined";
import SecurityOutlinedIcon from "@mui/icons-material/SecurityOutlined";
import DeleteIcon from "@mui/icons-material/Delete";
import Header from "../../../components/Header";
import { useState, useEffect } from "react";

const Users = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [rows, setRows] = useState([]);
  const [currentUserEmail, setCurrentUserEmail] = useState("");

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

  useEffect(() => {
    // Initial fetch
    fetchUsers();

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
      alert('Failed to delete user. Please try again.');
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
      alert('Failed to update user. Please try again.');
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
      alert('Failed to update role. Please try again.');
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
      editable: false,
    },
    {
      field: "email",
      headerName: "Email",
      flex: 1,
      editable: false,
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
    </Box>
  );
};

export default Users;