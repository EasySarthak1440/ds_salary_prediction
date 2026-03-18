import React, { useState } from 'react';
import axios from 'axios';
import { DollarSign, Briefcase, Star, Cpu, Brain, Layers, BarChart3, Cloud } from 'lucide-react';

const App: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    rating: 4.2,
    age: 10,
    python: true,
    spark: false,
    cloud: true,
    ml: true,
    stats: false,
    desc_len: 160,
    job_simp: 'data scientist', // Simplified for UI
    seniority: 'na'
  });

  // This maps the simplified UI inputs to the 118-feature vector the model expects
  // Note: For a production app, we'd want to dynamicall map all categories (Industry, Size, etc.)
  // For this demo, we'll use the core features and default others based on common data.
  const mapFeatures = () => {
    // 118 zeros as a base
    const features = new Array(118).fill(0);
    
    // Core Numerical Features (from building.py)
    features[0] = formData.rating;     // x1: Rating
    // Note: Other indices are inferred from building.py's dummy variables
    // In a real project, we would use a JSON mapping file of the dummy column names.
    // Based on data_input.py [4.2, 0, 49, 0, 0, 0, 0, 0, 160, False, False, True, ...]
    features[2] = formData.age;        // x3: Age
    features[8] = formData.desc_len;   // x9: Description Length
    
    // Skills (Booleans)
    features[9] = formData.python ? 1 : 0;
    features[10] = formData.spark ? 1 : 0;
    features[11] = formData.cloud ? 1 : 0;
    features[12] = formData.ml ? 1 : 0;
    features[13] = formData.stats ? 1 : 0;

    // ... In a real app, we'd map Job Simplification, Seniority, etc. to their specific indices.
    // For now, we'll use the data_input.py sample as a template and update user values.
    const baseSample = [4.2, 0, 49, 0, 0, 0, 0, 0, 160, false, false, true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, true, false, false, false, true, false];
    
    const finalFeatures = baseSample.map((val, idx) => {
        if (idx === 0) return formData.rating;
        if (idx === 2) return formData.age;
        if (idx === 8) return formData.desc_len;
        if (idx === 9) return formData.python ? 1 : 0;
        if (idx === 10) return formData.spark ? 1 : 0;
        if (idx === 11) return formData.cloud ? 1 : 0;
        if (idx === 12) return formData.ml ? 1 : 0;
        if (idx === 13) return formData.stats ? 1 : 0;
        return val ? 1 : 0;
    });

    return finalFeatures;
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const payload = { input: mapFeatures() };
      // Note: In development, we use the Flask server on :5000
      const res = await axios.post('http://127.0.0.1:5000/predict', payload);
      setPrediction(res.data.response);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to get prediction from server. Ensure Flask is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans p-6">
      <div className="max-w-4xl mx-auto">
        <header className="mb-12 text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-blue-600 p-3 rounded-2xl shadow-lg shadow-blue-200">
              <BarChart3 className="text-white w-8 h-8" />
            </div>
          </div>
          <h1 className="text-4xl font-bold tracking-tight mb-2">DS Salary Predictor</h1>
          <p className="text-slate-500">Accurate salary insights for Data Professionals</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
          <form onSubmit={handlePredict} className="bg-white p-8 rounded-3xl shadow-xl shadow-slate-200 border border-slate-100 space-y-6">
            <div className="space-y-4">
              <label className="block">
                <span className="text-sm font-semibold text-slate-700 flex items-center gap-2 mb-2">
                  <Star className="w-4 h-4 text-blue-500" /> Company Rating (1.0 - 5.0)
                </span>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  max="5"
                  value={formData.rating}
                  onChange={(e) => setFormData({...formData, rating: parseFloat(e.target.value)})}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all bg-slate-50"
                />
              </label>

              <label className="block">
                <span className="text-sm font-semibold text-slate-700 flex items-center gap-2 mb-2">
                  <Briefcase className="w-4 h-4 text-blue-500" /> Company Age (Years)
                </span>
                <input
                  type="number"
                  value={formData.age}
                  onChange={(e) => setFormData({...formData, age: parseInt(e.target.value)})}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all bg-slate-50"
                />
              </label>
            </div>

            <div className="space-y-4">
              <span className="text-sm font-semibold text-slate-700 block mb-2">Tech Stack & Skills</span>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { id: 'python', label: 'Python', icon: <Cpu className="w-3 h-3" /> },
                  { id: 'ml', label: 'Machine Learning', icon: <Brain className="w-3 h-3" /> },
                  { id: 'cloud', label: 'Cloud Computing', icon: <Cloud className="w-3 h-3" /> },
                  { id: 'spark', label: 'Apache Spark', icon: <Layers className="w-3 h-3" /> },
                  { id: 'stats', label: 'Statistics', icon: <BarChart3 className="w-3 h-3" /> }
                ].map((skill) => (
                  <button
                    key={skill.id}
                    type="button"
                    onClick={() => setFormData({...formData, [skill.id]: !formData[skill.id as keyof typeof formData]})}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border text-xs font-medium transition-all ${
                      formData[skill.id as keyof typeof formData]
                        ? 'bg-blue-600 border-blue-600 text-white shadow-md shadow-blue-100'
                        : 'bg-white border-slate-200 text-slate-600 hover:border-blue-300'
                    }`}
                  >
                    {skill.icon} {skill.label}
                  </button>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-slate-900 text-white py-4 rounded-2xl font-bold hover:bg-slate-800 active:scale-[0.98] transition-all disabled:opacity-50 disabled:scale-100 flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>Analyze Salary Path <DollarSign className="w-5 h-5" /></>
              )}
            </button>
          </form>

          <div className="space-y-8">
            <div className={`p-8 rounded-3xl transition-all duration-500 ${
              prediction 
                ? 'bg-blue-600 text-white shadow-2xl shadow-blue-200 scale-105' 
                : 'bg-white border-2 border-dashed border-slate-200 text-slate-400 text-center'
            }`}>
              {prediction ? (
                <div className="space-y-2">
                  <p className="text-blue-100 text-sm font-medium uppercase tracking-wider">Estimated Annual Salary</p>
                  <div className="text-6xl font-black flex items-center gap-1">
                    <span className="text-3xl opacity-60">$</span>
                    {prediction.toLocaleString()}
                    <span className="text-3xl opacity-60">K</span>
                  </div>
                  <p className="text-blue-100 text-xs mt-4">Based on market trends and technical attributes</p>
                </div>
              ) : (
                <div className="py-12">
                  <DollarSign className="w-12 h-12 mx-auto mb-4 opacity-20" />
                  <p className="font-medium">Complete the form to see result</p>
                </div>
              )}
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-100 text-red-600 rounded-2xl text-sm flex items-center gap-3">
                <div className="bg-red-500 w-2 h-2 rounded-full animate-pulse" />
                {error}
              </div>
            )}

            <div className="bg-white p-6 rounded-2xl border border-slate-100 space-y-4">
              <h3 className="text-sm font-bold flex items-center gap-2">
                <Cpu className="w-4 h-4 text-blue-600" /> Model Insights
              </h3>
              <ul className="space-y-2">
                <li className="text-xs text-slate-500 flex justify-between">
                  <span>Regression Type</span>
                  <span className="text-slate-900 font-medium">Random Forest Ensemble</span>
                </li>
                <li className="text-xs text-slate-500 flex justify-between">
                  <span>Confidence Level</span>
                  <span className="text-slate-900 font-medium">High (0.76 R²)</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
