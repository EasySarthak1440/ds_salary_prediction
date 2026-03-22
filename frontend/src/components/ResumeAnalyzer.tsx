import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, BarChart2, CheckCircle, AlertCircle } from 'lucide-react';

const ResumeAnalyzer = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [extractedSkills, setExtractedSkills] = useState<string[]>([]);
  const [skillGap, setSkillGap] = useState<any[]>([]);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      // 1. Parse Resume
      const parseResponse = await axios.post('http://localhost:5000/parse_resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const skills = parseResponse.data.extracted_skills;
      setExtractedSkills(skills);

      // 2. Get Skill Gap Analysis
      const gapResponse = await axios.post('http://localhost:5000/skill_gap', {
        skills: skills
      });
      
      setSkillGap(gapResponse.data.suggestions);

    } catch (err: any) {
      console.error(err);
      setError('Failed to analyze resume. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md max-w-4xl mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-6 flex items-center text-gray-800">
        <FileText className="mr-2 text-blue-600" /> Resume Intelligence
      </h2>

      <div className="mb-8 p-6 border-2 border-dashed border-gray-300 rounded-lg text-center hover:border-blue-500 transition-colors">
        <input 
          type="file" 
          accept=".pdf" 
          onChange={handleFileChange} 
          className="hidden" 
          id="resume-upload"
        />
        <label htmlFor="resume-upload" className="cursor-pointer flex flex-col items-center">
          <Upload className="w-12 h-12 text-gray-400 mb-2" />
          <span className="text-gray-600 font-medium">Click to upload your Resume (PDF)</span>
          <span className="text-sm text-gray-400 mt-1">We'll extract your skills automatically</span>
        </label>
        {file && <div className="mt-4 text-sm text-green-600 font-semibold">Selected: {file.name}</div>}
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className={`w-full py-3 rounded-lg font-bold text-white transition-all ${
          !file || loading 
            ? 'bg-gray-400 cursor-not-allowed' 
            : 'bg-blue-600 hover:bg-blue-700 shadow-lg'
        }`}
      >
        {loading ? 'Analyzing...' : 'Analyze Resume'}
      </button>

      {error && <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-lg flex items-center"><AlertCircle className="mr-2"/>{error}</div>}

      {(extractedSkills.length > 0 || skillGap.length > 0) && (
        <div className="mt-10 grid md:grid-cols-2 gap-8">
          {/* Extracted Skills */}
          <div className="bg-gray-50 p-5 rounded-xl border border-gray-200">
            <h3 className="text-lg font-bold mb-4 flex items-center text-gray-700">
              <CheckCircle className="mr-2 text-green-500" /> Detected Skills
            </h3>
            {extractedSkills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {extractedSkills.map((skill, idx) => (
                  <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium border border-green-200">
                    {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">No specific tech skills detected.</p>
            )}
          </div>

          {/* Skill Gap */}
          <div className="bg-blue-50 p-5 rounded-xl border border-blue-200">
            <h3 className="text-lg font-bold mb-4 flex items-center text-gray-700">
              <BarChart2 className="mr-2 text-blue-500" /> Salary Boosters
            </h3>
            <p className="text-sm text-gray-600 mb-4">Learn these to increase your market value:</p>
            <div className="space-y-3">
              {skillGap.map((gap, idx) => (
                <div key={idx} className="flex justify-between items-center bg-white p-3 rounded-lg shadow-sm">
                  <span className="font-semibold text-gray-800">{gap.name}</span>
                  <span className="text-green-600 font-bold">+{gap.value_add}</span>
                </div>
              ))}
              {skillGap.length === 0 && <p className="text-gray-500 italic">You have all the top skills!</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeAnalyzer;
