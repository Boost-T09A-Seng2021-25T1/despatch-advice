import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import Index from "./pages/index";
import SignIn from "./pages/SignIn";
import Dashboard from "./pages/Dashboard";
import LoggedOut from "./pages/LoggedOut";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { useState, useEffect } from "react";

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

const queryClient = new QueryClient();

const App = () => {
  const [user, setUser] = useState(null);

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <QueryClientProvider client={queryClient}>
        <HelmetProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/signin" element={<SignIn setUser={setUser} />} />
                <Route path="/dashboard" element={<Dashboard user={user} />} />
                <Route path="/logged-out" element={<LoggedOut />} />
              </Routes>
            </BrowserRouter>
          </TooltipProvider>
        </HelmetProvider>
      </QueryClientProvider>
    </GoogleOAuthProvider>
  );
};

export default App;
