// Loading States
export const Spinner = () => <div className="spinner" />;
export const Skeleton = () => <div className="skeleton"><div className="line" /><div className="line short" /></div>;
export const withLoading = (Component) => ({isLoading, ...props}) => isLoading ? <Spinner /> : <Component {...props} />;
