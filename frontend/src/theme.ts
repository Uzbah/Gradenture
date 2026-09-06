import { createTheme } from "@mui/material/styles";

// Mirrors the mono-lime tokens in index.css so MUI components match the
// existing design instead of shipping Material's default blue.
export const theme = createTheme({
  palette: {
    primary:    { main: "#111111", dark: "#2c2c2c", contrastText: "#fdfdfd" },
    secondary:  { main: "#dff15d", dark: "#d4e94c", contrastText: "#3d4413" },
    error:      { main: "#e2574c" },
    success:    { main: "#7a8a1e" },
    background: { default: "#e9e9e9", paper: "#ffffff" },
    text:       { primary: "#111111", secondary: "#555555", disabled: "#a0a0a0" },
    divider:    "#e2e2e2",
  },
  shape: { borderRadius: 11 },
  typography: {
    fontFamily: "inherit",
    fontSize: 13.5,
    fontWeightBold: 800,
    button: { fontWeight: 800, fontSize: 13.5, textTransform: "none" },
  },
  components: {
    MuiButton: { defaultProps: { disableElevation: true } },
    MuiTextField: { defaultProps: { size: "small" } },
  },
});
