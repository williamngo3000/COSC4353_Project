import { Box, Typography, useTheme, IconButton, Collapse, Checkbox, TextField, Button, Select, MenuItem, InputLabel, FormControl, OutlinedInput, Chip } from "@mui/material";
import { tokens } from "../../../theme";
import Header from "../../../components/Header";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import { useState, useEffect } from "react";
import { SKILLS_LIST } from '../../../utils/constants';

const Events = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [rows, setRows] = useState([]);
  const [expandedEvent, setExpandedEvent] = useState(null);
  const [eventVolunteers, setEventVolunteers] = useState({});
  const [editingEvent, setEditingEvent] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [filterUrgency, setFilterUrgency] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

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
          volunteerLimit: ev.volunteer_limit,
          currentVolunteers: ev.current_volunteers,
          status: ev.status,
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

  const handleToggleExpand = async (eventId) => {
    if (expandedEvent === eventId) {
      setExpandedEvent(null);
    } else {
      setExpandedEvent(eventId);
      // Fetch volunteers for this event if not already loaded
      if (!eventVolunteers[eventId]) {
        await fetchEventVolunteers(eventId);
      }
    }
  };

  const fetchEventVolunteers = async (eventId) => {
    try {
      // Fetch all accepted invites for this event
      const response = await fetch(`http://localhost:5001/invites?status=accepted`);
      if (!response.ok) {
        throw new Error('Failed to fetch volunteers');
      }

      const invites = await response.json();
      const eventInvites = invites.filter(inv => inv.event_id === eventId);

      // Fetch user details for each volunteer
      const volunteersWithDetails = await Promise.all(
        eventInvites.map(async (invite) => {
          try {
            const userRes = await fetch(`http://localhost:5001/profile/${encodeURIComponent(invite.user_email)}`);
            if (userRes.ok) {
              const profile = await userRes.json();
              return {
                email: invite.user_email,
                name: profile.full_name || invite.user_email,
                inviteId: invite.id,
                completed: invite.completed || false
              };
            }
          } catch (err) {
            console.error('Error fetching user profile:', err);
          }
          return {
            email: invite.user_email,
            name: invite.user_email,
            inviteId: invite.id,
            completed: invite.completed || false
          };
        })
      );

      setEventVolunteers(prev => ({
        ...prev,
        [eventId]: volunteersWithDetails
      }));
    } catch (error) {
      console.error('Error fetching event volunteers:', error);
      alert('Failed to load volunteers for this event');
    }
  };

  const handleToggleCompletion = async (eventId, inviteId, currentStatus) => {
    try {
      const response = await fetch(`http://localhost:5001/invites/${inviteId}/complete`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !currentStatus }),
      });

      if (!response.ok) {
        throw new Error('Failed to update completion status');
      }

      // Update local state
      setEventVolunteers(prev => ({
        ...prev,
        [eventId]: prev[eventId].map(vol =>
          vol.inviteId === inviteId
            ? { ...vol, completed: !currentStatus }
            : vol
        )
      }));

      console.log('Completion status updated successfully');
    } catch (error) {
      console.error('Error updating completion status:', error);
      alert('Failed to update completion status. Please try again.');
    }
  };

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

  const handleStartEdit = (event) => {
    setEditingEvent(event.id);
    setEditForm({
      name: event.name,
      description: event.description,
      location: event.location,
      requiredSkills: Array.isArray(event.requiredSkills) ? event.requiredSkills : [],
      urgency: event.urgency,
      date: event.date,
      volunteerLimit: event.volunteerLimit || '',
    });
  };

  const handleCancelEdit = () => {
    setEditingEvent(null);
    setEditForm({});
  };

  const handleSaveEdit = async (eventId) => {
    try {
      const response = await fetch(`http://localhost:5001/events/${eventId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_name: editForm.name,
          description: editForm.description,
          location: editForm.location,
          required_skills: editForm.requiredSkills,
          urgency: editForm.urgency,
          event_date: editForm.date,
          volunteer_limit: editForm.volunteerLimit ? parseInt(editForm.volunteerLimit) : null,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update event');
      }

      // Update local state
      setRows(rows.map(row =>
        row.id === eventId
          ? {
              ...row,
              name: editForm.name,
              description: editForm.description,
              location: editForm.location,
              requiredSkills: editForm.requiredSkills,
              urgency: editForm.urgency,
              date: editForm.date,
              volunteerLimit: editForm.volunteerLimit ? parseInt(editForm.volunteerLimit) : null,
            }
          : row
      ));

      setEditingEvent(null);
      setEditForm({});
      console.log('Event updated successfully');
    } catch (error) {
      console.error('Error updating event:', error);
      alert('Failed to update event. Please try again.');
    }
  };

  const handleFormChange = (field, value) => {
    setEditForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Filter events based on search and filters
  const filteredRows = rows.filter(event => {
    const matchesSearch = event.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          event.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          event.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesUrgency = !filterUrgency || event.urgency === filterUrgency;
    const matchesStatus = !filterStatus || event.status === filterStatus;

    return matchesSearch && matchesUrgency && matchesStatus;
  });

  return (
    <Box m="20px" fontFamily={"sans-serif"}>
      <Header title="Events" subtitle="List of all volunteer events - Click to expand" />

      {/* Search and Filter Section */}
      <Box display="flex" gap="15px" mb="20px" flexWrap="wrap">
        <TextField
          label="Search events..."
          variant="outlined"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{
            flex: 1,
            minWidth: '250px',
            '& .MuiInputLabel-root': { color: colors.grey[100] },
            '& .MuiOutlinedInput-root': {
              color: colors.grey[100],
              '& fieldset': { borderColor: colors.grey[100] },
              '&:hover fieldset': { borderColor: colors.grey[100] },
              '&.Mui-focused fieldset': { borderColor: colors.indigo[500] }
            }
          }}
        />
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel sx={{ color: colors.grey[100], '&.Mui-focused': { color: colors.indigo[500] } }}>
            Urgency
          </InputLabel>
          <Select
            value={filterUrgency}
            label="Urgency"
            onChange={(e) => setFilterUrgency(e.target.value)}
            sx={{
              color: colors.grey[100],
              '& .MuiOutlinedInput-notchedOutline': { borderColor: colors.grey[100] },
              '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: colors.grey[100] },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: colors.indigo[500] },
              '& .MuiSvgIcon-root': { color: colors.grey[100] }
            }}
            MenuProps={{
              PaperProps: {
                sx: {
                  backgroundColor: colors.primary[400],
                  '& .MuiMenuItem-root': {
                    color: colors.grey[100],
                    '&:hover': { backgroundColor: colors.grey[700] },
                    '&.Mui-selected': { backgroundColor: colors.grey[900] }
                  }
                }
              }
            }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="Low">Low</MenuItem>
            <MenuItem value="Medium">Medium</MenuItem>
            <MenuItem value="High">High</MenuItem>
            <MenuItem value="Critical">Critical</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel sx={{ color: colors.grey[100], '&.Mui-focused': { color: colors.indigo[500] } }}>
            Status
          </InputLabel>
          <Select
            value={filterStatus}
            label="Status"
            onChange={(e) => setFilterStatus(e.target.value)}
            sx={{
              color: colors.grey[100],
              '& .MuiOutlinedInput-notchedOutline': { borderColor: colors.grey[100] },
              '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: colors.grey[100] },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: colors.indigo[500] },
              '& .MuiSvgIcon-root': { color: colors.grey[100] }
            }}
            MenuProps={{
              PaperProps: {
                sx: {
                  backgroundColor: colors.primary[400],
                  '& .MuiMenuItem-root': {
                    color: colors.grey[100],
                    '&:hover': { backgroundColor: colors.grey[700] },
                    '&.Mui-selected': { backgroundColor: colors.grey[900] }
                  }
                }
              }
            }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="open">Open</MenuItem>
            <MenuItem value="closed">Closed</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Box m="40px 0 0 0">
        {rows.length === 0 ? (
          <Typography sx={{ textAlign: 'center', color: colors.grey[300], mt: 4 }}>
            No events created yet
          </Typography>
        ) : filteredRows.length === 0 ? (
          <Typography sx={{ textAlign: 'center', color: colors.grey[300], mt: 4 }}>
            No events match your search criteria
          </Typography>
        ) : (
          filteredRows.map((event) => (
            <Box
              key={event.id}
              mb="10px"
              sx={{
                backgroundColor: colors.primary[400],
                borderRadius: '8px',
                overflow: 'hidden',
                border: `1px solid ${colors.primary[300]}`
              }}
            >
              {/* Event Header - Clickable Part or Edit Mode */}
              {editingEvent === event.id ? (
                // Edit Mode
                <Box p="20px" sx={{ backgroundColor: colors.primary[400] }}>
                  <Typography variant="h5" fontWeight="600" color={colors.grey[100]} mb="15px">
                    Edit Event
                  </Typography>
                  <Box display="flex" flexDirection="column" gap="15px">
                    <TextField
                      label="Event Name"
                      value={editForm.name}
                      onChange={(e) => handleFormChange('name', e.target.value)}
                      fullWidth
                      sx={{
                        '& .MuiInputLabel-root': { color: colors.grey[100] },
                        '& .MuiOutlinedInput-root': {
                          color: colors.grey[100],
                          '& fieldset': { borderColor: colors.grey[100] },
                          '&:hover fieldset': { borderColor: colors.grey[100] },
                          '&.Mui-focused fieldset': { borderColor: colors.indigo[500] }
                        }
                      }}
                    />
                    <TextField
                      label="Description"
                      value={editForm.description}
                      onChange={(e) => handleFormChange('description', e.target.value)}
                      fullWidth
                      multiline
                      rows={2}
                      sx={{
                        '& .MuiInputLabel-root': { color: colors.grey[100] },
                        '& .MuiOutlinedInput-root': {
                          color: colors.grey[100],
                          '& fieldset': { borderColor: colors.grey[100] },
                          '&:hover fieldset': { borderColor: colors.grey[100] },
                          '&.Mui-focused fieldset': { borderColor: colors.indigo[500] }
                        }
                      }}
                    />
                    <TextField
                      label="Location"
                      value={editForm.location}
                      onChange={(e) => handleFormChange('location', e.target.value)}
                      fullWidth
                      sx={{
                        '& .MuiInputLabel-root': { color: colors.grey[100] },
                        '& .MuiOutlinedInput-root': {
                          color: colors.grey[100],
                          '& fieldset': { borderColor: colors.grey[100] },
                          '&:hover fieldset': { borderColor: colors.grey[100] },
                          '&.Mui-focused fieldset': { borderColor: colors.indigo[500] }
                        }
                      }}
                    />
                    <FormControl fullWidth>
                      <InputLabel sx={{ color: colors.grey[100], '&.Mui-focused': { color: colors.indigo[500] } }}>
                        Required Skills
                      </InputLabel>
                      <Select
                        multiple
                        value={editForm.requiredSkills || []}
                        onChange={(e) => handleFormChange('requiredSkills', e.target.value)}
                        input={<OutlinedInput label="Required Skills" />}
                        renderValue={(selected) => (
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {selected.map((value) => (
                              <Chip key={value} label={value} sx={{ backgroundColor: colors.grey[300], color: colors.grey[900] }} />
                            ))}
                          </Box>
                        )}
                        sx={{
                          color: colors.primary[100],
                          '& .MuiOutlinedInput-notchedOutline': { borderColor: colors.grey[100] },
                          '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: colors.grey[100] },
                          '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: colors.indigo[500] },
                          '& .MuiSvgIcon-root': { color: colors.grey[100] }
                        }}
                        MenuProps={{
                          PaperProps: {
                            sx: {
                              backgroundColor: colors.primary[400],
                              '& .MuiMenuItem-root': {
                                color: colors.grey[100],
                                '&:hover': { backgroundColor: colors.grey[700] },
                                '&.Mui-selected': {
                                  backgroundColor: colors.grey[900],
                                  '&:hover': { backgroundColor: colors.grey[700] }
                                }
                              }
                            }
                          }
                        }}
                      >
                        {SKILLS_LIST.map((skill) => (
                          <MenuItem key={skill} value={skill}>
                            <Checkbox checked={(editForm.requiredSkills || []).indexOf(skill) > -1} />
                            <Typography>{skill}</Typography>
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                    <TextField
                      label="Urgency"
                      value={editForm.urgency}
                      onChange={(e) => handleFormChange('urgency', e.target.value)}
                      fullWidth
                      sx={{
                        '& .MuiInputLabel-root': { color: colors.grey[100] },
                        '& .MuiOutlinedInput-root': {
                          color: colors.grey[100],
                          '& fieldset': { borderColor: colors.grey[100] },
                          '&:hover fieldset': { borderColor: colors.grey[100] },
                          '&.Mui-focused fieldset': { borderColor: colors.indigo[500] }
                        }
                      }}
                    />
                    <TextField
                      label="Event Date"
                      type="date"
                      value={editForm.date}
                      onChange={(e) => handleFormChange('date', e.target.value)}
                      fullWidth
                      slotProps={{
                        inputLabel: { shrink: true }
                      }}
                      sx={{
                        '& .MuiInputLabel-root': { color: colors.grey[100] },
                        '& .MuiOutlinedInput-root': {
                          color: colors.grey[100],
                          '& fieldset': { borderColor: colors.grey[100] },
                          '&:hover fieldset': { borderColor: colors.grey[100] },
                          '&.Mui-focused fieldset': { borderColor: colors.indigo[500] }
                        }
                      }}
                    />
                    <TextField
                      label="Volunteer Limit (leave empty for unlimited)"
                      type="number"
                      value={editForm.volunteerLimit}
                      onChange={(e) => handleFormChange('volunteerLimit', e.target.value)}
                      fullWidth
                      slotProps={{ htmlInput: { min: 1 } }}
                      sx={{
                        '& .MuiInputLabel-root': { color: colors.grey[100] },
                        '& .MuiOutlinedInput-root': {
                          color: colors.grey[100],
                          '& fieldset': { borderColor: colors.grey[100] },
                          '&:hover fieldset': { borderColor: colors.grey[100] },
                          '&.Mui-focused fieldset': { borderColor: colors.indigo[500] }
                        }
                      }}
                    />
                    <Box display="flex" gap="10px" mt="10px">
                      <Button
                        variant="contained"
                        onClick={() => handleSaveEdit(event.id)}
                        sx={{
                          backgroundColor: colors.green[500],
                          '&:hover': { backgroundColor: colors.green[700] }
                        }}
                      >
                        Save
                      </Button>
                      <Button
                        variant="outlined"
                        onClick={handleCancelEdit}
                        sx={{
                          borderColor: colors.grey[100],
                          color: colors.grey[100],
                          '&:hover': {
                            borderColor: colors.grey[300],
                            backgroundColor: colors.primary[300]
                          }
                        }}
                      >
                        Cancel
                      </Button>
                    </Box>
                  </Box>
                </Box>
              ) : (
                // View Mode
                <Box
                  onClick={() => handleToggleExpand(event.id)}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    p: '20px',
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: colors.grey[700]
                    }
                  }}
                >
                  <Box flex="1">
                    <Box display="flex" alignItems="center" gap="10px">
                      <Typography variant="h4" fontWeight="600" color={colors.green[500]}>
                        {event.name}
                      </Typography>
                      {event.status === 'closed' && (
                        <Typography
                          sx={{
                            px: '10px',
                            py: '3px',
                            backgroundColor: colors.red[500],
                            color: 'white',
                            borderRadius: '12px',
                            fontSize: '0.75rem',
                            fontWeight: '600'
                          }}
                        >
                          CLOSED
                        </Typography>
                      )}
                    </Box>
                    <Typography variant="body2" color={colors.grey[300]} mt="5px">
                      {event.description}
                    </Typography>
                    <Box display="flex" gap="20px" mt="10px" fontSize="14px">
                      <Typography color={colors.grey[100]}>
                        <strong>Date:</strong> {event.date}
                      </Typography>
                      <Typography color={colors.grey[100]}>
                        <strong>Location:</strong> {event.location}
                      </Typography>
                      <Typography color={colors.grey[100]}>
                        <strong>Urgency:</strong> {event.urgency}
                      </Typography>
                      <Typography color={event.status === 'closed' ? colors.red[400] : colors.grey[100]}>
                        <strong>Volunteers:</strong> {event.currentVolunteers || 0}
                        {event.volunteerLimit ? `/${event.volunteerLimit}` : ' (unlimited)'}
                      </Typography>
                    </Box>
                  </Box>

                  <Box display="flex" alignItems="center" gap="10px">
                    <IconButton
                      onClick={(e) => {
                        e.stopPropagation();
                        handleStartEdit(event);
                      }}
                      sx={{ color: colors.indigo[500] }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(event.id);
                      }}
                      sx={{ color: colors.red[500] }}
                    >
                      <DeleteIcon />
                    </IconButton>
                    <IconButton>
                      {expandedEvent === event.id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                  </Box>
                </Box>
              )}

              {/* Expandable Section - Volunteers List */}
              <Collapse in={expandedEvent === event.id}>
                <Box
                  p="20px"
                  sx={{
                    backgroundColor: colors.grey[700],
                    borderTop: `1px solid ${colors.primary[300]}`
                  }}
                >
                  <Typography variant="h5" fontWeight="600" color={colors.grey[100]} mb="15px">
                    Assigned Volunteers
                  </Typography>

                  {!eventVolunteers[event.id] ? (
                    <Typography color={colors.grey[300]}>Loading volunteers...</Typography>
                  ) : eventVolunteers[event.id].length === 0 ? (
                    <Typography color={colors.grey[300]}>No volunteers assigned to this event yet</Typography>
                  ) : (
                    <Box>
                      {eventVolunteers[event.id].map((volunteer) => (
                        <Box
                          key={volunteer.inviteId}
                          display="flex"
                          justifyContent="space-between"
                          alignItems="center"
                          p="15px"
                          mb="10px"
                          sx={{
                            backgroundColor: colors.primary[400],
                            borderRadius: '5px',
                            border: `1px solid ${colors.primary[300]}`
                          }}
                        >
                          <Box>
                            <Typography color={colors.grey[100]} fontWeight="600">
                              {volunteer.name}
                            </Typography>
                            <Typography variant="body2" color={colors.grey[300]}>
                              {volunteer.email}
                            </Typography>
                          </Box>

                          <Box display="flex" alignItems="center" gap="10px">
                            <Typography color={colors.grey[100]}>
                              {volunteer.completed ? 'Completed' : 'Mark as completed:'}
                            </Typography>
                            <Checkbox
                              checked={volunteer.completed}
                              onChange={() => handleToggleCompletion(event.id, volunteer.inviteId, volunteer.completed)}
                              sx={{
                                color: colors.green[500],
                                '&.Mui-checked': {
                                  color: colors.green[500]
                                }
                              }}
                            />
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  )}
                </Box>
              </Collapse>
            </Box>
          ))
        )}
      </Box>
    </Box>
  );
};

export default Events;