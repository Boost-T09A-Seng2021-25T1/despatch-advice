import { Helmet } from "react-helmet-async";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import HeroSection from "@/components/home/HeroSection";
import FeaturesSection from "@/components/home/FeaturesSection";
import ConversionSection from "@/components/home/ConversionSection";
import Logo from "@/components/ui/Logo";

// Certain parts of this code was generated using AI tools

const Index = () => {
  return (
    <>
      <Helmet>
        <link
          href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Archivo+Black&display=swap"
          rel="stylesheet"
        />
        <title>BoostXchange - Invoice to Despatch Conversion</title>
      </Helmet>

      <div className="flex flex-col min-h-screen bg-black">
        <Header />

        <main className="flex-grow">
          <div className="max-w-none mx-auto px-5 py-10 max-md:max-w-[991px] max-sm:max-w-screen-sm">
            <Logo />
            <HeroSection />
            <FeaturesSection />
            <ConversionSection />
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
};

export default Index;
