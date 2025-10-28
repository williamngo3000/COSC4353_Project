import { Box, Typography, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { tokens } from "../../theme";
import { fakeData } from "../../data/eventFake";
import Header from "../../components/Header";

const Events = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const columns = [
    { 
        field: "id", 
        headerName: "ID",
    },
    {
        field: "name",
        headerName: "Name",
        width: 200,
        cellClassName: "name-column--cell",
    },
    {
        field: "description",
        headerName: "Description",
        headerAlign: "left",
        flex: .5,
        align: "left",
    },
    {
        field: "location",
        headerName: "Location",
        headerAlign: "left",
        align: "left",
    },
    {
        field: "requiredSkills",
        headerName: "Requested Skills",
        headerAlign: "left",
    },
    {
        field: "urgency",
        headerName: "Urgency",
        headerAlign: "left",
        type: "number",
    },
    {
        field: "date",
        headerName: "Date Created",
        headerAlign: "left",
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
            rows={fakeData} 
            columns={columns}
            autoPageSize sx={{'& .MuiDataGrid-columnHeader--name' : { width: 'auto' } }}
        />
      </Box>
    </Box>
  );
};

export default Events;