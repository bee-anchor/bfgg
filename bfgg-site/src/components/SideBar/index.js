import {Box,Drawer, Grid, List, ListItem, ListItemIcon, ListItemText, Typography, withStyles} from "@material-ui/core";
import HomeIcon from "@material-ui/icons/Home";
import TimelineIcon from "@material-ui/icons/Timeline";
import React from "react";
import PropTypes from "prop-types";
import { grey } from '@material-ui/core/colors';

const styles = {
    drawer: {
        background: grey["800"],
        width: "20%"
    },
    drawerPaper: {
        width: "20%"
    }
};

class SideBar extends React.Component {
    render() {
        return <Drawer
            variant="permanent"
            anchor="left"
            className={this.props.classes.drawer}
            classes={{
                paper: this.props.classes.drawerPaper,
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
}

SideBar.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(SideBar)