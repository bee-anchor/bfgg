import React from 'react';
import PropTypes from 'prop-types';
import Card from '@material-ui/core/Card';
import Typography from '@material-ui/core/Typography';
import ToggleButton from '@material-ui/lab/ToggleButton';
import ToggleButtonGroup from '@material-ui/lab/ToggleButtonGroup';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles( theme => ({
  card: {
    paddingLeft: '1%',
    paddingRight: '1%',
    paddingBottom: '1%',
  },
  toggleRoot: {
    width: '100%',
  },
  toggleButtonRoot: {
    width: '100%',
    '&.Mui-selected': {
      backgroundColor: theme.palette.primary.main,
      color: theme.palette.grey["800"],
    },
    '&.Mui-selected:hover': {
      backgroundColor: theme.palette.primary.light,
      color: theme.palette.grey["800"],
    },
    '&:hover': {
      backgroundColor: theme.palette.primary.light,
      color: theme.palette.grey["800"],
    },
  },
}));

export default function GroupSelect(props) {
  const { groups, setSelectedGroup, selectedGroup } = props;
  const classes = useStyles();

  const handleChange = (event, newGroup) => {
    if (newGroup != null) {
      setSelectedGroup(newGroup);
    }
  };

  return (
    <Card className={classes.card}>
      <Typography variant="h6" gutterBottom>
          Selected Group
      </Typography>
      <ToggleButtonGroup
        exclusive
        onChange={handleChange}
        value={selectedGroup}
        classes={{ root: classes.toggleRoot }}
        aria-label="selected group"
      >

        {groups.map((g) => (
          <ToggleButton
            key={g}
            value={g}
            aria-label={g}
            selected={selectedGroup === g}
            classes={{ root: classes.toggleButtonRoot }}
          >
            {g}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    </Card>
  );
}

GroupSelect.propTypes = {
  groups: PropTypes.arrayOf(PropTypes.string).isRequired,
  setSelectedGroup: PropTypes.func.isRequired,
  selectedGroup: PropTypes.string.isRequired,
};
