import { Link } from "react-router-dom";

const SignInButton = ({ className = "" }) => {
  return (
    <Link
      to="/signin"
      className={`text-white text-3xl bg-[#9F91E9] px-[30px] py-2.5 rounded-full hover:bg-opacity-90 transition-colors ${className}`}
    >
      Sign in
    </Link>
  );
};

export default SignInButton;
