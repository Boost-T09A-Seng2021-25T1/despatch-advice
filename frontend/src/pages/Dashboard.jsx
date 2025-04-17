import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import {
  FileText,
  FileOutput,
  Mail,
  BarChart3,
  FileCode,
  ClipboardCheck,
} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import Logo from "@/components/ui/Logo";

const ActionCard = ({ title, to, icon }) => {
  return (
    <Link
      to={to}
      className="flex flex-col items-center bg-[#2B2A2A] rounded-[20px] border-[3px] border-[#A193EE] overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-[#A193EE]/20 hover:scale-[1.02] hover:border-[#9F91E9] p-4"
    >
      <div className="mb-3 p-4 rounded-full bg-[#1A1F2C]/70 flex items-center justify-center">
        {" "}
        {/* smaller padding */}
        {icon}
      </div>
      <h3 className="text-[#D9D9D9] text-base font-medium text-center">
        {title}
      </h3>{" "}
      {/* smaller font */}
    </Link>
  );
};

const Dashboard = () => {
  const actions = [
    {
      title: "Create Order XML",
      to: "/create-order",
      icon: <FileText size={48} className="text-[#A193EE]" />,
    },
    {
      title: "Create Despatch XML",
      to: "/create-despatch",
      icon: <ClipboardCheck size={48} className="text-[#A193EE]" />,
    },
    {
      title: "Create Invoice XML",
      to: "/create-invoice",
      icon: <FileCode size={48} className="text-[#A193EE]" />,
    },
    {
      title: "Convert XML to PDF",
      to: "/convert",
      icon: <FileOutput size={48} className="text-[#A193EE]" />,
    },
    {
      title: "Send Email",
      to: "/send-email",
      icon: <Mail size={48} className="text-[#A193EE]" />,
    },
    {
      title: "Statistics",
      to: "/statistics",
      icon: <BarChart3 size={48} className="text-[#A193EE]" />,
    },
  ];

  return (
    <div style={{ color: "white", padding: "2rem" }}>
      ✅ Dashboard page rendered successfully.
    </div>
  );
};

export default Dashboard;
