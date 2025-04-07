import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="bg-[linear-gradient(180deg,#000_0%,#918C8C_100%)] mt-20">
      <div className="max-w-none mx-auto px-5 py-10 max-md:max-w-[991px] max-sm:max-w-screen-sm">
        <div className="grid grid-cols-4 gap-10 max-md:grid-cols-2 max-sm:grid-cols-1">
          <div className="flex flex-col gap-5">
            <h3 className="text-white text-[0px_4px_4px_rgba(0,0,0,0)]">
              BoostXchange
            </h3>
            <p className="text-[#9F91E9] text-[25px]">
              The fast lane for invoice-to-despatch conversion
            </p>
          </div>

          <div className="flex flex-col gap-5">
            <h3 className="text-white text-[0px_4px_4px_rgba(0,0,0,0)]">
              Links
            </h3>
            <nav className="text-[#D9D9D9] text-[0px_4px_4px_rgba(0,0,0,0)] flex flex-col gap-2">
              <Link to="/features">Features</Link>
              <Link to="/pricing">Pricing</Link>
              <Link to="/about">About</Link>
            </nav>
          </div>

          <div className="flex flex-col gap-5">
            <h3 className="text-white text-[0px_4px_4px_rgba(0,0,0,0)]">
              Legal
            </h3>
            <nav className="text-[#D9D9D9] text-[0px_4px_4px_rgba(0,0,0,0)] flex flex-col gap-2">
              <Link to="/terms">Terms</Link>
              <Link to="/privacy">Privacy</Link>
              <Link to="/security">Security</Link>
            </nav>
          </div>

          <div className="flex flex-col gap-5">
            <h3 className="text-white text-[0px_4px_4px_rgba(0,0,0,0)]">
              Contact
            </h3>
            <div className="text-[#D9D9D9] text-[0px_4px_4px_rgba(0,0,0,0)] flex flex-col gap-2">
              <a href="mailto:support@boostxchange.com">
                support@boostxchange.com
              </a>
              <a href="tel:+12345678901" className="underline">
                +1 (234) 567-890
              </a>
            </div>
          </div>
        </div>

        <div className="w-full h-px bg-black my-10" />

        <div className="text-black text-[0px_4px_4px_rgba(0,0,0,0)] text-center">
          © 2025 BoostXchange. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
