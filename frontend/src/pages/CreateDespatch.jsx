import { Helmet } from "react-helmet-async";
import { useState } from "react";
import { FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import Logo from "@/components/ui/Logo";

export default function CreateDespatch() {
  const [file, setFile] = useState(null);
  const [previewContent, setPreviewContent] = useState("");

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) handleFileSelect(droppedFile);
  };

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewContent(e.target?.result);
    };
    reader.readAsText(selectedFile);
  };

  return (
    <>
      <Helmet>
        <title>Create Despatch XML - BoostXchange</title>
      </Helmet>

      <div className="flex flex-col min-h-screen bg-black">
        <header className="w-full bg-[linear-gradient(180deg,#2B2A2A_0.01%,#000_98.08%)] py-4">
          <div className="max-w-none mx-auto px-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center w-1/10">
                <div className="scale-[0.4] origin-left">
                  <Logo />
                </div>
              </div>
              <h2 className="text-white text-xl text-center">
                Welcome to <span className="text-[#9F91E9]">BoostXchange</span>
              </h2>
              <div className="w-1/10" />
            </div>
          </div>
        </header>

        <main className="flex-grow p-6">
          <div className="max-w-6xl mx-auto grid grid-cols-2 gap-8">
            <div
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-[#A193EE] rounded-lg bg-[#2B2A2A] min-h-[400px] hover:border-[#9F91E9] transition-colors"
            >
              <FileText size={48} className="text-[#A193EE] mb-4" />
              <p className="text-white text-center mb-4">
                Drag and drop your XML file here or
              </p>
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".xml"
                onChange={(e) => {
                  if (e.target.files?.[0]) handleFileSelect(e.target.files[0]);
                }}
              />
              <Button
                onClick={() => document.getElementById("file-upload")?.click()}
                className="bg-[#9F91E9] hover:bg-[#8F81D9]"
              >
                Select File
              </Button>
              {file && (
                <p className="mt-4 text-[#A193EE]">Selected: {file.name}</p>
              )}
            </div>

            <Card className="bg-[#2B2A2A] border-[#A193EE] p-6">
              <h3 className="text-white text-xl mb-4">Document Preview</h3>
              <div className="bg-[#1A1F2C] p-4 rounded-md h-[400px] overflow-auto">
                {previewContent ? (
                  <pre className="text-[#D9D9D9] text-sm whitespace-pre-wrap">
                    {previewContent}
                  </pre>
                ) : (
                  <p className="text-[#A193EE] text-center mt-[150px]">
                    Upload a file to see the preview
                  </p>
                )}
              </div>
            </Card>
          </div>
        </main>
      </div>
    </>
  );
}
