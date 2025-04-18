import { Link } from "react-router-dom";

const LoggedOut = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white">
      <h1 className="text-3xl mb-4">You’ve been logged out</h1>
      <Link to="/signin" className="text-[#9F91E9] hover:underline">
        Sign in again
      </Link>
    </div>
  );
};

export default LoggedOut;
