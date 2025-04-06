import { useState } from "react";
import { Link } from "react-router-dom";

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="w-full bg-[linear-gradient(180deg,#918C8C_0.01%,#000_98.08%)] py-5">
      <div className="max-w-none mx-auto px-5 max-md:max-w-[991px] max-sm:max-w-screen-sm">
        <div className="flex items-center justify-between">
          <nav className="flex items-center gap-10 max-sm:hidden">
            <Link
              to="/"
              className="text-white text-[0px_4px_4px_rgba(0,0,0,0)]"
            >
              Despatch Advice Generator
            </Link>
            <Link
              to="/"
              className="text-white text-[0px_4px_4px_rgba(0,0,0,0)]"
            >
              XML Converter
            </Link>
            <Link
              to="/"
              className="text-white text-[0px_4px_4px_rgba(0,0,0,0)]"
            >
              About
            </Link>
          </nav>

          <button
            className="block sm:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle menu"
          >
            <i className="ti ti-menu-2 text-white text-3xl" />
          </button>

          <div className="flex items-center gap-5">
            <div className="flex items-center gap-2">
              <img
                src="https://cdn.builder.io/api/v1/image/assets/TEMP/c0ca434b2e22dbf8936d810a4e531a729d238667"
                alt="Country flag"
                className="w-[36px] h-[36px] rounded-full"
              />
              <span className="text-white text-2xl">Australia</span>
              <button aria-label="Select country">
                <svg
                  width="18"
                  height="10"
                  viewBox="0 0 18 10"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-[16px] h-[8px]"
                >
                  <path
                    d="M1 1L9 9L17 1"
                    stroke="white"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  ></path>
                </svg>
              </button>
            </div>

            {/* 🔗 Docs button */}
            <a
              href="https://your-swagger-url.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-white text-3xl bg-[#9F91E9] px-[30px] py-2.5 rounded-full hover:bg-opacity-90 transition-colors"
            >
              Docs
            </a>

            <Link
              to="/signin"
              className="text-white text-3xl bg-[#9F91E9] px-[30px] py-2.5 rounded-full hover:bg-opacity-90 transition-colors"
            >
              Sign in
            </Link>
          </div>
        </div>

        {isMenuOpen && (
          <div className="sm:hidden mt-4 bg-black bg-opacity-90 p-4 rounded-lg">
            <nav className="flex flex-col gap-4">
              <Link to="/" className="text-white text-lg">
                Despatch Advice Generator
              </Link>
              <Link to="/" className="text-white text-lg">
                XML Converter
              </Link>
              <Link to="/" className="text-white text-lg">
                About
              </Link>
              <a
                href="https://docs.d2a6fgkrp6cypv.amplifyapp.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-white text-lg"
              >
                Docs
              </a>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
