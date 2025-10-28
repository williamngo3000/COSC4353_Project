import { Box, Button, TextField, Select, MenuItem, FormControl, InputLabel, FormHelperText, Checkbox, ListItemText } from "@mui/material";
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { Formik } from "formik";
import * as yup from "yup";
import useMediaQuery from "@mui/material/useMediaQuery";
import Header from "../../../components/Header";

const Form = () => {
  const isNonMobile = useMediaQuery("(min-width:600px)");

  const handleFormSubmit = (values) => {
    console.log(values);
  };

  return (
    <Box m="20px">
      <Header title="CREATE EVENT" subtitle="" />

      <Formik
        onSubmit={handleFormSubmit}
        initialValues={initialValues}
        validationSchema={checkoutSchema}
      >
        {({
          values,
          errors,
          touched,
          handleBlur,
          handleChange,
          handleSubmit,
          setFieldValue,
        }) => (
          <form onSubmit={handleSubmit}>
            <Box
              display="grid"
              gap="30px"
              gridTemplateColumns="repeat(4, minmax(0, 1fr))"
              sx={{
                "& > div": { gridColumn: isNonMobile ? undefined : "span 4" },
              }}
            >
                {/* Limit event name to 100 chars*/}
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="Event Name"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.eventName}
                name="eventName"
                error={!!touched.eventName && !!errors.eventName}
                helperText={touched.eventName && errors.eventName}
                sx={{ gridColumn: "span 4" }}
              />
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="Event Description"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.eventDescription}
                name="eventDescription"
                error={!!touched.eventDescription && !!errors.eventDescription}
                helperText={touched.eventDescription && errors.eventDescription}
                sx={{ gridColumn: "span 4" }}
              />
              <TextField
                fullWidth
                variant="filled"
                type="text"
                label="Email"
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.email}
                name="email"
                error={!!touched.email && !!errors.email}
                helperText={touched.email && errors.email}
                sx={{ gridColumn: "span 4" }}
              />
              <FormControl
                fullWidth
                variant="filled"
                sx={{ gridColumn: "span 4" }}
                error={!!touched.location && !!errors.location}
              >
                <InputLabel>Location</InputLabel>
                <Select
                  name="location"
                  value={values.location}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  MenuProps={{
                    PaperProps: {
                        style: {
                            maxHeight: 300,
                        },
                    },
                  }}
                >
                  <MenuItem value="AL">Alabama (AL)</MenuItem>
                  <MenuItem value="AK">Alaska (AK)</MenuItem>
                  <MenuItem value="AZ">Arizona (AZ)</MenuItem>
                  <MenuItem value="AR">Arkansas (AR)</MenuItem>
                  <MenuItem value="CA">California (CA)</MenuItem>
                  <MenuItem value="CO">Colorado (CO)</MenuItem>
                  <MenuItem value="CT">Connecticut (CT)</MenuItem>
                  <MenuItem value="DE">Delaware (DE)</MenuItem>
                  <MenuItem value="FL">Florida (FL)</MenuItem>
                  <MenuItem value="GA">Georgia (GA)</MenuItem>
                  <MenuItem value="HI">Hawaii (HI)</MenuItem>
                  <MenuItem value="ID">Idaho (ID)</MenuItem>
                  <MenuItem value="IL">Illinois (IL)</MenuItem>
                  <MenuItem value="IN">Indiana (IN)</MenuItem>
                  <MenuItem value="IA">Iowa (IA)</MenuItem>
                  <MenuItem value="KS">Kansas (KS)</MenuItem>
                  <MenuItem value="KY">Kentucky (KY)</MenuItem>
                  <MenuItem value="LA">Louisiana (LA)</MenuItem>
                  <MenuItem value="ME">Maine (ME)</MenuItem>
                  <MenuItem value="MD">Maryland (MD)</MenuItem>
                  <MenuItem value="MA">Massachusetts (MA)</MenuItem>
                  <MenuItem value="MI">Michigan (MI)</MenuItem>
                  <MenuItem value="MN">Minnesota (MN)</MenuItem>
                  <MenuItem value="MS">Mississippi (MS)</MenuItem>
                  <MenuItem value="MO">Missouri (MO)</MenuItem>
                  <MenuItem value="MT">Montana (MT)</MenuItem>
                  <MenuItem value="NE">Nebraska (NE)</MenuItem>
                  <MenuItem value="NV">Nevada (NV)</MenuItem>
                  <MenuItem value="NH">New Hampshire (NH)</MenuItem>
                  <MenuItem value="NJ">New Jersey (NJ)</MenuItem>
                  <MenuItem value="NM">New Mexico (NM)</MenuItem>
                  <MenuItem value="NY">New York (NY)</MenuItem>
                  <MenuItem value="NC">North Carolina (NC)</MenuItem>
                  <MenuItem value="ND">North Dakota (ND)</MenuItem>
                  <MenuItem value="OH">Ohio (OH)</MenuItem>
                  <MenuItem value="OK">Oklahoma (OK)</MenuItem>
                  <MenuItem value="OR">Oregon (OR)</MenuItem>
                  <MenuItem value="PA">Pennsylvania (PA)</MenuItem>
                  <MenuItem value="RI">Rhode Island (RI)</MenuItem>
                  <MenuItem value="SC">South Carolina (SC)</MenuItem>
                  <MenuItem value="SD">South Dakota (SD)</MenuItem>
                  <MenuItem value="TN">Tennessee (TN)</MenuItem>
                  <MenuItem value="TX">Texas (TX)</MenuItem>
                  <MenuItem value="UT">Utah (UT)</MenuItem>
                  <MenuItem value="VT">Vermont (VT)</MenuItem>
                  <MenuItem value="VA">Virginia (VA)</MenuItem>
                  <MenuItem value="WA">Washington (WA)</MenuItem>
                  <MenuItem value="WV">West Virginia (WV)</MenuItem>
                  <MenuItem value="WI">Wisconsin (WI)</MenuItem>
                  <MenuItem value="WY">Wyoming (WY)</MenuItem>
                </Select>
                {touched.location && errors.location && (
                  <FormHelperText>{errors.location}</FormHelperText>
                )}
              </FormControl>
              {/* Multi-selection dropdown for Skills */}
              <FormControl
                fullWidth
                variant="filled"
                sx={{ gridColumn: "span 4" }}
                error={!!touched.requiredSkills && !!errors.requiredSkills}
              >
                <InputLabel>Required Skills</InputLabel>
                <Select
                  multiple
                  name="requiredSkills"
                  value={values.requiredSkills}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  renderValue={(selected) => selected.join(', ')}
                  MenuProps={{
                    PaperProps: {
                      style: {
                        maxHeight: 300,
                      },
                    },
                  }}
                >
                  <MenuItem value="Communication">
                    <Checkbox checked={values.requiredSkills.indexOf("Communication") > -1} />
                    <ListItemText primary="Communication" />
                  </MenuItem>
                  <MenuItem value="Leadership">
                    <Checkbox checked={values.requiredSkills.indexOf("Leadership") > -1} />
                    <ListItemText primary="Leadership" />
                  </MenuItem>
                  <MenuItem value="Teamwork">
                    <Checkbox checked={values.requiredSkills.indexOf("Teamwork") > -1} />
                    <ListItemText primary="Teamwork" />
                  </MenuItem>
                  <MenuItem value="Problem Solving">
                    <Checkbox checked={values.requiredSkills.indexOf("Problem Solving") > -1} />
                    <ListItemText primary="Problem Solving" />
                  </MenuItem>
                  <MenuItem value="Physical Labor">
                    <Checkbox checked={values.requiredSkills.indexOf("Physical Labor") > -1} />
                    <ListItemText primary="Physical Labor" />
                  </MenuItem>
                  <MenuItem value="Customer Service">
                    <Checkbox checked={values.requiredSkills.indexOf("Customer Service") > -1} />
                    <ListItemText primary="Customer Service" />
                  </MenuItem>
                  <MenuItem value="Teaching/Mentoring">
                    <Checkbox checked={values.requiredSkills.indexOf("Teaching/Mentoring") > -1} />
                    <ListItemText primary="Teaching/Mentoring" />
                  </MenuItem>
                  <MenuItem value="Technical Skills">
                    <Checkbox checked={values.requiredSkills.indexOf("Technical Skills") > -1} />
                    <ListItemText primary="Technical Skills" />
                  </MenuItem>
                  <MenuItem value="Creative Skills">
                    <Checkbox checked={values.requiredSkills.indexOf("Creative Skills") > -1} />
                    <ListItemText primary="Creative Skills" />
                  </MenuItem>
                </Select>
                {touched.requiredSkills && errors.requiredSkills && (
                  <FormHelperText>{errors.requiredSkills}</FormHelperText>
                )}
              </FormControl>
              {/* Date, maybe have a calendar popup to browse through to select a date? */}
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DatePicker
                  label="Event Date"
                  value={values.date}
                  onChange={(newValue) => setFieldValue('date', newValue)}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      variant: 'filled',
                      error: !!touched.date && !!errors.date,
                      helperText: touched.date && errors.date,
                      onBlur: handleBlur,
                      name: 'date',
                      sx: { gridColumn: "span 4" }
                    }
                  }}
                />
              </LocalizationProvider>
            </Box>
            <Box display="flex" justifyContent="end" mt="20px">
              <Button type="submit" color="secondary" variant="contained">
                Create New Event
              </Button>
            </Box>
          </form>
        )}
      </Formik>
    </Box>
  );
};

const emailRegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const checkoutSchema = yup.object().shape({
  eventName: yup.string().required("Required"),
  eventDescription: yup.string().required("Required"),
  email: yup
    .string()
    .matches(emailRegExp, "Invalid email")
    .required("Required"),
  location: yup.string().required("Required"),
  requiredSkills: yup.array().min(1, "Select at least one skill").required("Required"),
  urgency: yup.number().required("Required"),
  date: yup.date().required("Required").nullable()
});
const initialValues = {
  eventName: "",
  eventDescription: "",
  email: "",
  location: "",
  requiredSkills: [],
  urgency: "",
  date: null,
};

export default Form;
