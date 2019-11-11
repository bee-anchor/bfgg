import { Drawer, List, ListItem, ListItemIcon, ListItemText, Typography } from "@material-ui/core";
import { makeStyles } from '@material-ui/core/styles';
import HomeIcon from "@material-ui/icons/Home";
import TimelineIcon from "@material-ui/icons/Timeline";
import React from "react";
import { grey } from '@material-ui/core/colors';

const useStyles = makeStyles({
    drawer: {
        width: "20%"
    },
    drawerPaper: {
        width: "20%",
        background: grey["400"],
    }
});

export default function SideBar() {
    const classes = useStyles();

    return <Drawer
        variant="permanent"
        anchor="left"
        className={classes.drawer}
        classes={{
            paper: classes.drawerPaper,
        }}
    >
            <List component="nav">
                <ListItem>
                    <Typography variant="h2">BFGG</Typography>
                </ListItem>
                <ListItem button>
                    <ListItemIcon>
                        <HomeIcon/>
                    </ListItemIcon>
                    <ListItemText primary="Home"/>
                </ListItem>
                <ListItem button>
                    <ListItemIcon>
                        <TimelineIcon/>
                    </ListItemIcon>
                    <ListItemText primary="Past Tests"/>
                </ListItem>
            </List>
    </Drawer>
}
