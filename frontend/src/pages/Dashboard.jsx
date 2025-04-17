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

const Dashboard = ({ user }) => {
  const userName = user?.name || "User";
  const userImage = user?.picture || "https://via.placeholder.com/150";

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
    <>
      <Helmet>
        <title>Dashboard - BoostXchange</title>
      </Helmet>

      <div className="flex flex-col min-h-screen bg-black">
        <header className="w-full bg-[linear-gradient(180deg,#2B2A2A_0.01%,#000_98.08%)] py-4">
          <div className="flex items-center justify-between max-w-[1440px] mx-auto px-6">
            {/* Logo (shrinked) */}
            <div className="flex items-center">
              <div className="scale-[0.3] origin-left">
                <Logo />
              </div>
            </div>

            {/* Centered welcome text */}
            <div className="flex flex-col items-center flex-grow text-center -ml-28">
              <h2 className="text-white text-xl font-medium">
                Welcome to <span className="text-[#9F91E9]">BoostXchange</span>
              </h2>
              <p className="text-[#CCCCCC] text-sm italic">
                Signed in as <strong>{userName}</strong>
              </p>
            </div>

            {/* Profile avatar */}
            <div className="flex items-center">
              <Avatar>
                <AvatarImage src={userImage} alt="User profile" />
                <AvatarFallback>{userName[0]}</AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>

        <main className="flex-grow">
          <div className="max-w-none mx-auto px-5 py-10 max-md:max-w-[991px] max-sm:max-w-screen-sm">
            <div className="flex flex-col items-center gap-6 mb-8">
              <h1 className="text-[#D9D9D9] text-3xl font-medium">Dashboard</h1>
              <p className="text-white text-lg max-w-2xl text-center">
                Select an action below to get started with your document
                processing
              </p>
              <div className="w-[250px] h-px bg-[#A193EE]" />
            </div>

            <div className="grid grid-cols-3 gap-8 max-xl:grid-cols-2 max-md:grid-cols-1">
              {actions.map((action, index) => (
                <ActionCard
                  key={index}
                  title={action.title}
                  to={action.to}
                  icon={action.icon}
                />
              ))}
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
};

export default Dashboard;
