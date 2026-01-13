import { useState } from "react";
import FileUpload from "./components/FileUpload";
import ResultsView from "./components/ResultsView";
import { Search } from "lucide-react";
import { AnalysisResponse } from "./types/api";
import { UI_TEXT } from "./constants";

function App() {
  // Keep track of whether we're uploading or showing results
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(
    null
  );
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  // When the backend finishes processing the file
  const handleAnalysisComplete = (result: AnalysisResponse): void => {
    setAnalysisResult(result);
    setIsAnalyzing(false);
  };

  // When user drops a file or clicks upload
  const handleAnalysisStart = (): void => {
    setIsAnalyzing(true);
    setAnalysisResult(null); // wipe out any previous results
  };

  // Go back to upload screen
  const handleReset = (): void => {
    setAnalysisResult(null);
    setIsAnalyzing(false);
  };

  // Show results if we have them, otherwise show upload screen
  if (analysisResult) {
    return <ResultsView result={analysisResult} onReset={handleReset} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center items-center gap-3 mb-6">
            <Search className="w-10 h-10 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">
              {UI_TEXT.APP_TITLE}
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            {UI_TEXT.APP_DESCRIPTION}
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <FileUpload
            onAnalysisComplete={handleAnalysisComplete}
            onAnalysisStart={handleAnalysisStart}
            isAnalyzing={isAnalyzing}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
