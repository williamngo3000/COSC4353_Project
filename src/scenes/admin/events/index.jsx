import { Box, Typography, useTheme, IconButton } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../../theme";
// import { fakeData } from "../../../data/eventFake";
import Header from "../../../components/Header";
import DeleteIcon from "@mui/icons-material/Delete";
import { useState, useEffect } from "react";

const Events = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  // const [rows, setRows] = useState(fakeData);
  const [rows, setRows] = useState([]);

  // Fetch events from backend API
  const fetchEvents = () => {
    fetch('http://localhost:5001/events')
      .then(res => res.json())
      .then(data => {
        const formatted = data.map(ev => ({
          id: ev.id,
          name: ev.event_name,
          description: ev.description,
          location: ev.location,
          requiredSkills: ev.required_skills,
          urgency: ev.urgency,
          date: ev.event_date,
        }));
        setRows(formatted);
      })
      .catch(err => console.error('Failed to load events:', err));
  };

  useEffect(() => {
    // Initial fetch
    fetchEvents();

    // Poll for updates every 3 seconds
    const interval = setInterval(fetchEvents, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleDelete = async (id) => {
    // Optimistic update - remove from UI immediately
    const deletedRow = rows.find(row => row.id === id);
    setRows(rows.filter((row) => row.id !== id));

    // Delete from backend
    try {
      const response = await fetch(`http://localhost:5001/events/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete event');
      }

      console.log('Event deleted successfully');
    } catch (error) {
      console.error('Error deleting event:', error);
      // Revert if delete fails
      setRows(prevRows => [...prevRows, deletedRow]);
      alert('Failed to delete event. Please try again.');
    }
  };

  const handleCellEdit = async (updatedRow) => {
    // Optimistic update - update UI immediately
    const originalRow = rows.find(row => row.id === updatedRow.id);
    setRows(rows.map((row) => (row.id === updatedRow.id ? updatedRow : row)));

    // Update in backend
    try {
      const response = await fetch(`http://localhost:5001/events/${updatedRow.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_name: updatedRow.name,
          description: updatedRow.description,
          location: updatedRow.location,
          required_skills: updatedRow.requiredSkills,
          urgency: updatedRow.urgency,
          event_date: updatedRow.date,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update event');
      }

      console.log('Event updated successfully');
    } catch (error) {
      console.error('Error updating event:', error);
      // Revert if update fails
      setRows(rows.map((row) => (row.id === updatedRow.id ? originalRow : row)));
      alert('Failed to update event. Please try again.');
    }

    return updatedRow;
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
        width: 200,
        cellClassName: "name-column--cell",
        editable: true,
    },
    {
        field: "description",
        headerName: "Description",
        headerAlign: "left",
        flex: .5,
        align: "left",
        editable: true,
    },
    {
        field: "location",
        headerName: "Location",
        headerAlign: "left",
        align: "left",
        editable: true,
    },
    {
        field: "requiredSkills",
        headerName: "Requested Skills",
        headerAlign: "left",
        editable: true,
    },
    {
        field: "urgency",
        headerName: "Urgency",
        headerAlign: "left",
        type: "number",
        editable: true,
    },
    {
        field: "date",
        headerName: "Date Created",
        headerAlign: "left",
        editable: true,
    },
    {
        field: "actions",
        headerName: "Actions",
        width: 100,
        sortable: false,
        filterable: false,
        renderCell: (params) => (
          <IconButton
            onClick={() => handleDelete(params.row.id)}
            sx={{ color: colors.red[500] }}
          >
            <DeleteIcon />
          </IconButton>
        ),
    }
  ];

  return (
    <Box m="20px" fontFamily={"sans-serif"}>
      <Header title="Events" subtitle="" />
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
            autoPageSize
            processRowUpdate={handleCellEdit}
            onProcessRowUpdateError={(error) => console.error(error)}
            sx={{'& .MuiDataGrid-columnHeader--name' : { width: 'auto' } }}
        />
      </Box>
    </Box>
  );
};

export default Events;