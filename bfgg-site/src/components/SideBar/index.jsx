import Drawer from '@material-ui/core/Drawer';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Divider from '@material-ui/core/Divider';
import PlayCircleFilledOutlinedIcon from '@material-ui/icons/PlayCircleFilledOutlined';
import TimelineIcon from '@material-ui/icons/Timeline';
import React from 'react';
import PropTypes from 'prop-types';

const useStyles = makeStyles(theme => ({
  drawer: {
    width: '160px',
  },
  drawerPaper: {
    width: '160px',
    background: theme.palette.grey["400"],
  },
  tabsIndicator: {
    width: '0px',
  },
  tabSelected: {
    backgroundColor: theme.palette.grey["800"],
    color: theme.palette.grey["100"],
  },
}));

export default function SideBar(props) {
  const classes = useStyles();
  const { tabValue, setTabValue } = props;

  return (
    <Drawer
      variant="permanent"
      anchor="left"
      className={classes.drawer}
      classes={{
        paper: classes.drawerPaper,
      }}
    >
      <Typography variant="h2" align="center" color="textSecondary">BFGG</Typography>
      <Divider variant="middle" />
      <Tabs
        classes={{ indicator: classes.tabsIndicator }}
        orientation="vertical"
        value={tabValue}
        onChange={(event, newValue) => { setTabValue(newValue); }}
      >
        <Tab
          classes={{ selected: classes.tabSelected }}
          icon={<PlayCircleFilledOutlinedIcon />}
          label="Run"
          id="tab-0"
          aria-controls="tabpanel-0"
        />
        <Tab
          classes={{ selected: classes.tabSelected }}
          icon={<TimelineIcon />}
          label="Past Tests"
          id="tab-1"
          aria-controls="tabpanel-1"
        />
      </Tabs>
    </Drawer>
  );
}

SideBar.propTypes = {
  tabValue: PropTypes.number.isRequired,
  setTabValue: PropTypes.func.isRequired,
};
