import { Link } from "react-router-dom";
const Logo = () => {
  return (
    <Link
      to="/"
      className="text-[rgba(255,255,255,0.39)] text-[0px_4px_4px_rgba(0,0,0,0)] max-md:text-[80px] max-sm:text-[50px] font-bold"
    >
      <span className="text-8xl">Boost</span>
      <span className="text-[#9F91E9] text-9xl">X</span>
      <span className="text-8xl">change</span>
    </Link>
  );
};
export default Logo;
