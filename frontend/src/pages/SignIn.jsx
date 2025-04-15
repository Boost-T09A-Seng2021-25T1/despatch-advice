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
    }, 1500);
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

            <CardContent>
              <form onSubmit={handleSubmit}>
                <div className="grid w-full items-center gap-6">
                  <div className="flex flex-col space-y-1.5">
                    <Label htmlFor="email" className="text-white">
                      Email
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="bg-[#3A3B3A] text-white border-[#A193EE]"
                    />
                  </div>

                  <div className="flex flex-col space-y-1.5">
                    <Label htmlFor="password" className="text-white">
                      Password
                    </Label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="bg-[#3A3B3A] text-white border-[#A193EE]"
                    />
                  </div>

                  <div className="flex justify-end">
                    <Link
                      to="/forgot-password"
                      className="text-[#9F91E9] hover:underline text-sm"
                    >
                      Forgot password?
                    </Link>
                  </div>
                </div>

                <CardFooter className="flex flex-col gap-4 pt-6 px-0">
                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-[#9F91E9] hover:bg-[#8F81D9] text-white"
                  >
                    {isLoading ? "Signing in..." : "Sign in"}
                  </Button>

                  <div className="text-white text-center">
                    Don't have an account?{" "}
                    <Link
                      to="/signup"
                      className="text-[#9F91E9] hover:underline"
                    >
                      Sign up
                    </Link>
                  </div>
                </CardFooter>
              </form>
            </CardContent>
          </Card>
        </main>

        <Footer />
      </div>
    </>
  );
};

export default SignIn;
