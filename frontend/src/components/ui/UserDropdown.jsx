import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const UserDropdown = ({ user }) => {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/logged-out");
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <div className="cursor-pointer" onClick={() => setOpen((prev) => !prev)}>
        <Avatar>
          <AvatarImage src={user?.picture} alt={user?.name} />
          <AvatarFallback>{user?.name?.[0]}</AvatarFallback>
        </Avatar>
      </div>

      {open && (
        <div className="absolute right-0 mt-2 w-40 bg-[#2B2A2A] border border-[#A193EE] rounded shadow-md z-50">
          <button
            onClick={handleLogout}
            className="w-full text-left px-4 py-2 text-white hover:bg-[#3A3B3A]"
          >
            Log out
          </button>
        </div>
      )}
    </div>
  );
};

export default UserDropdown;
