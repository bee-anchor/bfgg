import React from 'react';
import { createMuiTheme, ThemeProvider } from '@material-ui/core/styles';
import { CssBaseline } from '@material-ui/core';
import { amber, lightGreen } from '@material-ui/core/colors';
import SideBar from './components/SideBar'
import MainBody from './components/MainBody'

const theme = createMuiTheme({
  palette: {
    primary: lightGreen,
    secondary: amber,
  }
});

export default function App() {

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline>

        <head>
          <meta
            name="viewport"
            content="minimum-scale=1, initial-scale=1, width=device-width, shrink-to-fit=no"
          />
          <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
        </head>

          <SideBar />
          <MainBody />

      </CssBaseline>
    </ThemeProvider>
  );
}


