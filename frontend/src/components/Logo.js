import PropTypes from 'prop-types';
import { Link as RouterLink } from 'react-router-dom';
// @mui
import { useTheme } from '@mui/material/styles';
import { Box } from '@mui/material';

// ----------------------------------------------------------------------

Logo.propTypes = {
  disabledLink: PropTypes.bool,
  sx: PropTypes.object,
};

export default function Logo({ disabledLink = false, sx }) {
  const theme = useTheme();

  const PRIMARY_LIGHT = theme.palette.primary.light;

  const PRIMARY_MAIN = theme.palette.primary.main;

  const PRIMARY_DARK = theme.palette.primary.dark;

  // OR

  const logo = <Box component="img" src="/static/logo.svg" sx={{ width: 20, height: 20, display: "inline" , ...sx }} />
  const titleStyle = { fontSize: 20, color: PRIMARY_DARK, fontWeight: 'bold', display: "inline", ...sx };
  const title = <Box component="h1" sx={titleStyle}>Smart Contract Check</Box>;

  if (disabledLink) {
    return <>{logo}</>;
  }

  return <RouterLink to="/" style={{ textDecoration: 'none' }}>{logo} {title} </RouterLink>;
}
