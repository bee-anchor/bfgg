import React from 'react';
import { makeStyles, createMuiTheme, ThemeProvider } from '@material-ui/core/styles';
import { CssBaseline, Typography, Container } from '@material-ui/core';
import logo from './logo.svg';
import AgentStatus from './components/AgentsStatus'

const theme = createMuiTheme({
  palette: {
    type: 'dark',
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
    <Container maxWidth="xl">
    <Typography component="div">
      <Typography component='h1' variant='h1' align='center' gutterBottom={true}>BFGG</Typography>
        <AgentStatus />
        </Typography>
        </Container>
        </CssBaseline>
        </ThemeProvider>
  );
}


