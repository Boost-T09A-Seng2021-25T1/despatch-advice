import { useState } from "react";

const CountrySelector = () => {
  const countries = [
    {
      id: 1,
      name: "Australia",
      flagUrl:
        "https://cdn.builder.io/api/v1/image/assets/TEMP/c0ca434b2e22dbf8936d810a4e531a729d238667",
    },
    {
      id: 2,
      name: "United States",
      flagUrl:
        "https://cdn.builder.io/api/v1/image/assets/TEMP/c0ca434b2e22dbf8936d810a4e531a729d238667",
    },
    {
      id: 3,
      name: "United Kingdom",
      flagUrl:
        "https://cdn.builder.io/api/v1/image/assets/TEMP/c0ca434b2e22dbf8936d810a4e531a729d238667",
    },
    {
      id: 4,
      name: "Canada",
      flagUrl:
        "https://cdn.builder.io/api/v1/image/assets/TEMP/c0ca434b2e22dbf8936d810a4e531a729d238667",
    },
  ];

  const [selectedCountry, setSelectedCountry] = useState(countries[0]);
  const [isOpen, setIsOpen] = useState(false);

  const toggleDropdown = () => setIsOpen(!isOpen);

  const selectCountry = (country) => {
    setSelectedCountry(country);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        className="flex items-center gap-2"
        onClick={toggleDropdown}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <img
          src={selectedCountry.flagUrl}
          alt={`${selectedCountry.name} flag`}
          className="w-[57px] h-[56px] rounded-full"
        />
        <span className="text-white text-3xl">{selectedCountry.name}</span>
        <svg
          width="18"
          height="10"
          viewBox="0 0 18 10"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={`w-[16px] h-[8px] transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
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

      {isOpen && (
        <ul
          className="absolute z-10 mt-2 w-full bg-[#2A2B2A] rounded-lg shadow-lg py-2"
          role="listbox"
        >
          {countries.map((country) => (
            <li
              key={country.id}
              className="px-4 py-2 hover:bg-[#3A3B3A] cursor-pointer flex items-center gap-2"
              onClick={() => selectCountry(country)}
              role="option"
              aria-selected={selectedCountry.id === country.id}
            >
              <img
                src={country.flagUrl}
                alt={`${country.name} flag`}
                className="w-8 h-8 rounded-full"
              />
              <span className="text-white">{country.name}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default CountrySelector;
