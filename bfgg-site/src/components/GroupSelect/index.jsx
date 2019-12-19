import React from 'react';
import PropTypes from 'prop-types';
import {
  Card, FormControl, RadioGroup, Radio, FormControlLabel
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles({
  card: {
    paddingLeft: '1%',
    paddingRight: '1%',
    paddingBottom: '1%',
  },
});

export default function GroupSelect(props) {
  const { groups, setSelectedGroup, selectedGroup } = props;
  const classes = useStyles();

  const handleChange = event => {
    setSelectedGroup(event.target.value);
  };

  return (
      <Card className={classes.card}>
        <FormControl component="fieldset">
          <RadioGroup aria-label="selected-group" name="selected-group" value={selectedGroup} onChange={handleChange} row>
            {groups.map((g, index) => {
              return <FormControlLabel
                  key={g}
                  value={g}
                  control={<Radio color="primary"/>}
                  label={g}
                  labelPlacement="bottom"
              />
            })}
          </RadioGroup>
        </FormControl>
      </Card>
  );
}

GroupSelect.propTypes = {
  groups: PropTypes.array.isRequired,
  setSelectedGroup: PropTypes.func.isRequired,
  selectedGroup: PropTypes.string.isRequired,
};
