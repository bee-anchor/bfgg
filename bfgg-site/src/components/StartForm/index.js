import React from 'react';
import axios from 'axios';
import PropTypes from 'prop-types';
import { Card, TextField, Button } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';

const styles = {
    card: {
        marginTop: '40px',
        paddingLeft: '1%',
        paddingRight: '1%',
        paddingBottom: '1%',
    },
    button: {
        marginTop: '1%'
    }
}

class StartForm extends React.Component  {
    constructor(props) {
        super(props);
        this.state = {
            name: '',
            test: '',
            javaOpts: ''
        };

        this.handleChange = this.handleChange.bind(this);
        this.sendStart = this.sendStart.bind(this);
    }

    sendStart() {
        console.log({
            "project": this.state.name,
            "testClass": this.state.test,
            "javaOpts": this.state.javaOpts
        });
        axios.post("http://localhost:8000/start", {
            "project": this.state.name,
            "testClass": this.state.test,
            "javaOpts": this.state.javaOpts
        })
        .then()
    }

    handleChange(fieldType) {
        return (event) => {
            this.setState({[fieldType]: event.target.value})
        }
    }

    
    render() {
        return (
            <Card className={this.props.classes.card}>
            <form noValidate autoComplete="off">
                <TextField
                    id="project-name"
                    label="Project"
                    placeholder="super6-perf"
                    helperText="The name of the repo containing the tests"
                    fullWidth
                    margin="normal"
                    variant="filled"
                    onChange={this.handleChange('name')}
                />
                <TextField
                    id="test-class"
                    label="Test Class"
                    placeholder="InPlayWebSpiking_custom"
                    helperText="The test class to be run"
                    fullWidth
                    margin="normal"
                    variant="filled"
                    onChange={this.handleChange('test')}
                />
                <TextField
                    id="java-opts"
                    label="JavaOpts"
                    placeholder="-Xmx14G -DUSERS=33 -DDURATION=10minutes"
                    helperText="Additional javaOpts to be passed to the test"
                    fullWidth
                    margin="normal"
                    variant="filled"
                    onChange={this.handleChange('javaOpts')}
                />
                <Button
                        fullWidth
                        variant="contained"
                        color="primary"
                        onClick={this.sendStart}
                        size='large'
                        className={this.props.classes.button}
                        onClick={this.sendStart}
                    >
                        Start Test
                    </Button>
            </form>
            </Card>
    );
    }
}

StartForm.propTypes = {
    classes: PropTypes.object.isRequired,
  };

export default withStyles(styles)(StartForm)