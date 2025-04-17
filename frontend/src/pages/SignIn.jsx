import { useState } from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";

const SignIn = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate authentication process
    setTimeout(() => {
      setIsLoading(false);
      console.log("Sign in attempt with:", { email, password });
    }, 10500);
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
                Enter your credentials to access your account
              </CardDescription>
            </CardHeader>

            <CardContent className="flex justify-center py-4">
              <GoogleLogin
                onSuccess={(credentialResponse) => {
                  const decoded = jwtDecode(credentialResponse.credential);
                  console.log("Google user:", decoded);

                  // TO-DO - ATTACH BACKEND HERE
                  fetch("https://apiHere.com/auth/google", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                      idToken: credentialResponse.credential,
                    }),
                  })
                    .then((res) => res.json())
                    .then((data) => {
                      console.log("Backend login success:", data);
                    });
                }}
                onError={() => {
                  console.error("Google Login Failed");
                }}
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
