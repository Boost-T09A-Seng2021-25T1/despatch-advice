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
    const idToken = credentialResponse?.credential;
    if (!idToken) {
      alert("Missing Google credential. Please try again.");
      return;
    }

    setIsLoading(true);

    const decoded = jwtDecode(idToken);

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
    } finally {
      setIsLoading(false);
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
              {isLoading ? (
                <div className="text-white text-center">
                  <svg
                    className="animate-spin h-6 w-6 mr-2 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8v8H4z"
                    ></path>
                  </svg>
                  Logging in...
                </div>
              ) : (
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={() => {
                    console.error("Google Login Failed");
                    alert("Google login failed. Please try again.");
                  }}
                />
              )}
            </CardContent>
          </Card>
        </main>

        <Footer />
      </div>
    </>
  );
};

export default SignIn;
