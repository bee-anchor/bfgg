import React from 'react';
import axios from 'axios';
import PropTypes from 'prop-types';
import { Card, Grid, FormControl, TextField, Button } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';

const styles = {
    button: {
        height: '100%',
    },
    buttonFC: {
        height: '70%',
    },
    card: {
        marginTop: '40px',
        paddingLeft: '1%',
        paddingRight: '1%',
        paddingBottom: '1%',

    }
};

class CloneForm extends React.Component  {
    constructor(props) {
        super(props);
        this.state = {url: ''};

        this.handleChange = this.handleChange.bind(this)
        this.sendClone = this.sendClone.bind(this)
    }

    handleChange(event) {
        this.setState({url: event.target.value})
    }

    sendClone() {
        axios.post("http://localhost:8000/clone", {
            "repo": this.state.url
        })
        .then()
    }
    
    render() {
        return (
            <Card className={this.props.classes.card}>
                <Grid container spacing={3}>
                <Grid item xs={9}>
                    <TextField
                        id="clone-repo-url"
                        label="clone repo url"
                        fullWidth
                        margin="normal"
                        variant="outlined"
                        onChange={this.handleChange}
                    />
                </Grid>
                <Grid item xs>
                <FormControl fullWidth margin='normal' className={this.props.classes.buttonFC}>
                    <Button
                        fullWidth
                        variant="contained"
                        color="primary"
                        onClick={this.sendClone}
                        className={this.props.classes.button}
                    >
                        Clone
                    </Button>
                    </FormControl>
                </Grid>
                </Grid>
                
            </Card>
    );
    }
}

CloneForm.propTypes = {
    classes: PropTypes.object.isRequired,
  };

export default withStyles(styles)(CloneForm)