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

const SignIn = ({ setUser }) => {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleGoogleSuccess = async (credentialResponse) => {
    const idToken = credentialResponse.credential;
    const decoded = jwtDecode(idToken);

    console.log("Google ID Token:", idToken);
    console.log("Decoded Google User:", decoded);

    try {
      const res = await fetch(
        "https://vm1vgp720e.execute-api.us-east-1.amazonaws.com/v2/google/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ idToken }),
        }
      );

      const rawText = await res.text();
      console.log("Status Code:", res.status);
      console.log("Raw Response:", rawText);

      if (!res.ok) {
        alert("Login failed: " + rawText);
        return;
      }

      const data = JSON.parse(rawText);
      localStorage.setItem("user", JSON.stringify(data.user));
      localStorage.setItem("token", data.token);
      setUser(data.user);
      navigate("/dashboard");
    } catch (err) {
      console.error("Request error:", err);
      alert("Something went wrong. Try again later.");
    }
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
