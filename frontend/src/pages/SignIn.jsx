import { useState } from "react";
import { Helmet } from "react-helmet-async";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";

const SignIn = () => {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleGoogleSuccess = async (credentialResponse) => {
    const decoded = jwtDecode(credentialResponse.credential);

    // Extract profile info
    const userInfo = {
      name: decoded.name,
      email: decoded.email,
      picture: decoded.picture,
    };

    // Store in localStorage
    localStorage.setItem("user", JSON.stringify(userInfo));

    // To-do: send to backend
    // await fetch("https://apiHere.com/auth/google", ...);

    // Redirect to dashboard
    navigate("/dashboard");
  };

  return (
    <>
      <Helmet>
        <title>Sign In - BoostXchange</title>
      </Helmet>

      <div className="flex flex-col min-h-screen bg-black">
        <Header />

        <main className="flex-grow flex items-center justify-center py-12">
          <Card className="w-full max-w-md bg-[#2B2A2A] border-[#A193EE] border-2">
            <CardHeader>
              <CardTitle className="text-[#D9D9D9] text-2xl">Sign In</CardTitle>
              <CardDescription className="text-white">
                Please login with Google using the button below
              </CardDescription>
            </CardHeader>

            <CardContent className="flex justify-center py-4">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={() => console.error("Google Login Failed")}
              />
            </CardContent>
          </Card>
        </main>

        <Footer />
      </div>
    </>
  );
};

export default SignIn;
