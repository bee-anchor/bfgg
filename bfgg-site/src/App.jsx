import React, { useState } from 'react';
import { createMuiTheme, ThemeProvider } from '@material-ui/core/styles';
import { CssBaseline } from '@material-ui/core';
import { amber, lightGreen } from '@material-ui/core/colors';
import SideBar from './components/SideBar';
import MainBody from './components/MainBody';

const theme = createMuiTheme({
  palette: {
    primary: lightGreen,
    secondary: amber,
  },
});

export default function App() {
  const [tabValue, setTabValue] = useState(0);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline>
        <SideBar tabValue={tabValue} setTabValue={setTabValue} />
        <MainBody tabValue={tabValue} />
      </CssBaseline>
    </ThemeProvider>
  );
}
