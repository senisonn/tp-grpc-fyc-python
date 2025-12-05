// Error Handling
const ERROR_MSG = {3: 'Invalid', 5: 'Not found', 13: 'Server error', 16: 'Auth required'};
export const ErrorDisplay = ({error}) => error ? <div>Error {error.code}: {ERROR_MSG[error.code]}</div> : null;
export const useError = () => {
  const [error, setError] = React.useState(null);
  return {error, handleError: (e) => setError({code: e.code, message: e.message})};
};
