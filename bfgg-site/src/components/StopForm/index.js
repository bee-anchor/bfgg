import React from 'react';
import axios from 'axios';
import PropTypes from 'prop-types';
import { Card, Button } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';

const styles = {
    card: {
        marginTop: '40px',
        paddingTop: '1%',
        paddingLeft: '1%',
        paddingRight: '1%',
        paddingBottom: '1%',
    },
}

class StopForm extends React.Component  {

    sendStop() {
        axios.post("http://localhost:8000/stop")
        .then()
    }
    
    render() {
        return (
            <Card className={this.props.classes.card}>
            <form noValidate autoComplete="off">
                <Button
                        fullWidth
                        variant="contained"
                        color="secondary"
                        onClick={this.sendStop}
                        size='large'
                    >
                        Stop Test
                    </Button>
            </form>
            </Card>
    );
    }
}

StopForm.propTypes = {
    classes: PropTypes.object.isRequired,
  };

export default withStyles(styles)(StopForm)