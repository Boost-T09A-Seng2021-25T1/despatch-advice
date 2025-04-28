import { Helmet } from "react-helmet-async";
import { useState } from "react";
import { FileText, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import Logo from "@/components/ui/Logo";

export default function CreateDespatch() {
  const [file, setFile] = useState(null);
  const [previewContent, setPreviewContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailInput, setEmailInput] = useState("");

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
    setError("");
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewContent(e.target?.result);
    };
    reader.readAsText(selectedFile);
  };

  const handleSubmit = async () => {
    if (!previewContent) {
      setError("Please upload a valid XML file first.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        "https://uj1acngyia.execute-api.us-east-1.amazonaws.com/v2/apiEndPoint",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ xmlDoc: previewContent }),
        }
      );

      const data = await response.json();

      if (response.ok && data?.despatch_xml) {
        setPreviewContent(data.despatch_xml);
      } else {
        setError(data?.error || "Something went wrong.");
      }
    } catch (err) {
      setError("Network error. Try again later.");
    } finally {
      setLoading(false);
    }
  };

  const handleSendEmailClick = () => {
    setShowEmailModal(true);
  };

  const handleSendEmailConfirm = async () => {
    if (!emailInput || !previewContent) {
      setError("Please provide an email and generate XML first.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(previewContent, "text/xml");

      const idElement = xmlDoc.getElementsByTagName("cbc:ID")[0];
      const issueDateElement = xmlDoc.getElementsByTagName("cbc:IssueDate")[0];

      const despatchId = idElement?.textContent || "UnknownID";
      const issueDate = issueDateElement?.textContent || "UnknownDate";

      const payload = {
        recipient_email: emailInput, // ✅ Corrected key name
        despatch_info: {
          ID: despatchId,
          IssueDate: issueDate,
        },
        despatch_xml: btoa(unescape(encodeURIComponent(previewContent))), // ✅ Corrected key name
      };

      const response = await fetch(
        "https://uj1acngyia.execute-api.us-east-1.amazonaws.com/v2/sendEmail",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();

      if (response.ok) {
        alert(`Email sent successfully to ${emailInput}!`);
        setShowEmailModal(false);
        setEmailInput("");
      } else {
        setError(data?.error || "Something went wrong while sending email.");
      }
    } catch (err) {
      setError("Network error. Try again later.");
    } finally {
      setLoading(false);
    }
  };

  const handleConvertPDF = () => {
    alert("Convert to PDF functionality not yet implemented.");
  };

  return (
    <>
      <Helmet>
        <title>Create Despatch XML - BoostXchange</title>
      </Helmet>

      {/* Email Modal */}
      {showEmailModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-[#2B2A2A] p-8 rounded-lg w-[400px] max-w-[90%]">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-white text-lg">Send Email</h2>
              <button onClick={() => setShowEmailModal(false)}>
                <X className="text-white" />
              </button>
            </div>
            <input
              type="email"
              placeholder="Enter recipient email"
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              className="w-full p-2 mb-4 rounded bg-[#1A1F2C] text-white border border-[#A193EE]"
            />
            <Button
              onClick={handleSendEmailConfirm}
              className="w-full bg-[#6EE7B7] hover:bg-[#34D399] text-black"
              disabled={loading}
            >
              {loading ? "Sending..." : "Send Email"}
            </Button>
          </div>
        </div>
      )}

      {/* Main Page */}
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

        <main className="flex-grow flex">
          {/* Left Panel */}
          <div className="flex-1 bg-[#2B2A2A] p-6 overflow-auto">
            <h3 className="text-white text-xl mb-4">Document Preview</h3>
            <div className="bg-[#1A1F2C] p-4 rounded-md h-[80vh] overflow-auto">
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
          </div>

          {/* Right Sidebar */}
          <div className="w-[300px] bg-[#1A1F2C] p-6 border-l border-[#A193EE] flex flex-col">
            <div
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-[#A193EE] rounded-lg bg-[#2B2A2A] hover:border-[#9F91E9] transition-colors mb-6"
            >
              <FileText size={32} className="text-[#A193EE] mb-2" />
              <p className="text-white text-sm text-center mb-2">
                Drag and drop
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
                className="bg-[#9F91E9] hover:bg-[#8F81D9] text-xs px-4 py-2"
              >
                Select File
              </Button>
              {file && (
                <p className="mt-2 text-[#A193EE] text-xs text-center">
                  {file.name}
                </p>
              )}
            </div>

            {/* Buttons */}
            <Button
              onClick={handleSubmit}
              className="w-full mb-4 bg-[#6EE7B7] hover:bg-[#34D399] text-black"
              disabled={loading}
            >
              {loading ? "Processing..." : "Generate Despatch XML"}
            </Button>

            <Button
              onClick={handleSendEmailClick}
              className="w-full mb-4 bg-[#9F91E9] hover:bg-[#8F81D9]"
            >
              Send Email
            </Button>

            <Button
              onClick={handleConvertPDF}
              className="w-full bg-[#FBBF24] hover:bg-[#F59E0B] text-black"
            >
              Convert to PDF
            </Button>

            {error && (
              <p className="text-red-400 mt-4 text-center text-sm">{error}</p>
            )}
          </div>
        </main>
      </div>
    </>
  );
}
