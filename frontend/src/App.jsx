import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import Index from "./pages/index";
import SignIn from "./pages/SignIn";
import { GoogleOAuthProvider } from "@react-oauth/google";

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

const queryClient = new QueryClient();

const App = () => (
  <GoogleOAuthProvider clientId={clientId}>
    <QueryClientProvider client={queryClient}>
      <HelmetProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/signin" element={<SignIn />} />
              <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </HelmetProvider>
    </QueryClientProvider>
  </GoogleOAuthProvider>
);

export default App;
