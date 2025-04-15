import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const ConversionForm = () => {
  const [file, setFile] = useState(null);
  const [isConverting, setIsConverting] = useState(false);
  const [conversionType, setConversionType] = useState("despatch");

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) return;

    setIsConverting(true);

    setTimeout(() => {
      setIsConverting(false);
      alert(`File ${file.name} converted successfully!`);
      setFile(null);
    }, 2000);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto bg-[#2B2A2A] border-[#A193EE] border-2">
      <CardHeader>
        <CardTitle className="text-[#D9D9D9]">Document Conversion</CardTitle>
        <CardDescription className="text-white">
          Upload your XML document to convert it to the format you need
        </CardDescription>
      </CardHeader>

      <Tabs defaultValue="despatch" onValueChange={setConversionType}>
        <TabsList className="grid w-full grid-cols-2 bg-[#1A1A1A]">
          <TabsTrigger
            value="despatch"
            className="data-[state=active]:bg-[#9F91E9]"
          >
            Despatch Advice
          </TabsTrigger>
          <TabsTrigger value="pdf" className="data-[state=active]:bg-[#9F91E9]">
            PDF Conversion
          </TabsTrigger>
        </TabsList>

        <CardContent className="pt-6">
          <form onSubmit={handleSubmit}>
            <div className="grid w-full items-center gap-4">
              <div className="flex flex-col space-y-1.5">
                <Label htmlFor="xml-file" className="text-white">
                  Upload XML File
                </Label>
                <Input
                  id="xml-file"
                  type="file"
                  accept=".xml"
                  onChange={handleFileChange}
                  className="bg-[#3A3B3A] text-white border-[#A193EE]"
                />
              </div>

              {conversionType === "despatch" && (
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="reference" className="text-white">
                    Reference Number
                  </Label>
                  <Input
                    id="reference"
                    placeholder="Enter reference number"
                    className="bg-[#3A3B3A] text-white border-[#A193EE]"
                  />
                </div>
              )}

              {file && (
                <div className="text-white">Selected file: {file.name}</div>
              )}
            </div>

            <CardFooter className="flex justify-end pt-6 px-0">
              <Button
                type="submit"
                disabled={!file || isConverting}
                className="bg-[#9F91E9] hover:bg-[#8F81D9] text-white"
              >
                {isConverting
                  ? "Converting..."
                  : `Convert to ${
                      conversionType === "despatch" ? "Despatch Advice" : "PDF"
                    }`}
              </Button>
            </CardFooter>
          </form>
        </CardContent>
      </Tabs>
    </Card>
  );
};

export default ConversionForm;
