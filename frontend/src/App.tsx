import React, { useState } from 'react';
import axios from 'axios';
import { DollarSign, Briefcase, Star, Cpu, Brain, Layers, Cloud, Sparkles } from 'lucide-react';
import './index.css';

const App: React.FC = () => {
  const [market, setMarket] = useState<'US' | 'India'>('India');
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    rating: 4.2,
    yoe: 3,
    age: 10, // Company age for US
    python: true,
    sql: true,
    llm: true,
    cloud: true,
    spark: false,
    ml: true,
    stats: false,
    job_simp: 'data scientist',
    seniority: 'na'
  });

  const mapFeaturesForUS = () => {
    // Original US model expects 118 features based on FlaskAPI/app.py logic
    const baseSample = [4.2, 0, 49, 0, 0, 0, 0, 0, 160, false, false, true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, true, false, false, false, true, false];
    
    return baseSample.map((val, idx) => {
        if (idx === 0) return formData.rating;
        if (idx === 2) return formData.age;
        if (idx === 9) return formData.python ? 1 : 0;
        if (idx === 10) return formData.spark ? 1 : 0;
        if (idx === 11) return formData.cloud ? 1 : 0;
        if (idx === 12) return formData.ml ? 1 : 0;
        if (idx === 13) return formData.stats ? 1 : 0;
        return val ? 1 : 0;
    });
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      if (market === 'India') {
        const res = await axios.post('http://127.0.0.1:5001/predict_india', formData);
        setPrediction(res.data.prediction_lpa);
      } else {
        const payload = { input: mapFeaturesForUS() };
        const res = await axios.post('http://127.0.0.1:5000/predict', payload);
        setPrediction(res.data.response);
      }
    } catch (err: any) {
      console.error(err);
      setError(`Ensure ${market} Flask server is running on port ${market === 'India' ? '5001' : '5000'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans p-6">
      <div className="max-w-4xl mx-auto">
        {/* Market Switcher */}
        <div className="flex justify-center mb-8">
            <div className="bg-white p-1 rounded-2xl shadow-sm border border-slate-200 flex gap-1">
                <button 
                    onClick={() => { setMarket('US'); setPrediction(null); }}
                    className={`px-6 py-2 rounded-xl text-sm font-bold transition-all ${market === 'US' ? 'bg-slate-900 text-white shadow-md' : 'text-slate-400 hover:text-slate-600'}`}
                >
                    🇺🇸 US Market
                </button>
                <button 
                    onClick={() => { setMarket('India'); setPrediction(null); }}
                    className={`px-6 py-2 rounded-xl text-sm font-bold transition-all ${market === 'India' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-600'}`}
                >
                    🇮🇳 India Market
                </button>
            </div>
        </div>

        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold tracking-tight mb-2">2026 Salary Predictor</h1>
          <p className="text-slate-500">Real-time SOTA insights for {market === 'India' ? 'Bengaluru & India' : 'the United States'}</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
          <form onSubmit={handlePredict} className="bg-white p-8 rounded-3xl shadow-xl shadow-slate-200 border border-slate-100 space-y-6">
            <div className="space-y-4">
              {market === 'India' ? (
                <label className="block">
                  <span className="text-sm font-semibold text-slate-700 flex items-center gap-2 mb-2">
                    <Briefcase className="w-4 h-4 text-blue-500" /> Years of Experience
                  </span>
                  <input
                    type="number"
                    value={formData.yoe}
                    onChange={(e) => setFormData({...formData, yoe: parseInt(e.target.value)})}
                    className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all bg-slate-50"
                  />
                </label>
              ) : (
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
              )}
              
              <label className="block">
                <span className="text-sm font-semibold text-slate-700 flex items-center gap-2 mb-2">
                  <Star className="w-4 h-4 text-blue-500" /> {market === 'India' ? 'Company Rating' : 'Employer Rating'}
                </span>
                <input
                  type="number"
                  step="0.1"
                  value={formData.rating}
                  onChange={(e) => setFormData({...formData, rating: parseFloat(e.target.value)})}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all bg-slate-50"
                />
              </label>
            </div>

            <div className="space-y-4">
              <span className="text-sm font-semibold text-slate-700 block mb-2">
                {market === 'India' ? 'SOTA 2026 Skill Stack' : 'Technical Skills'}
              </span>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { id: 'python', label: 'Python', icon: <Cpu className="w-3 h-3" />, show: true },
                  { id: 'llm', label: 'Generative AI', icon: <Brain className="w-3 h-3" />, show: market === 'India' },
                  { id: 'ml', label: 'Machine Learning', icon: <Sparkles className="w-3 h-3" />, show: market === 'US' },
                  { id: 'cloud', label: 'Cloud (AWS/Azure)', icon: <Cloud className="w-3 h-3" />, show: true },
                  { id: 'sql', label: 'SQL', icon: <Layers className="w-3 h-3" />, show: market === 'India' },
                  { id: 'spark', label: 'Apache Spark', icon: <Layers className="w-3 h-3" />, show: market === 'US' },
                ].filter(s => s.show).map((skill) => (
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
              className="w-full bg-slate-900 text-white py-4 rounded-2xl font-bold hover:bg-slate-800 transition-all flex items-center justify-center gap-2"
            >
              {loading ? "Analyzing..." : <>Predict {market === 'India' ? 'Lakhs (₹)' : 'K ($)'} <DollarSign className="w-5 h-5" /></>}
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
                    <span className="text-3xl opacity-60">{market === 'India' ? '₹' : '$'}</span>
                    {Math.round(prediction).toLocaleString()}
                    <span className="text-3xl opacity-60">{market === 'India' ? 'L' : 'K'}</span>
                  </div>
                  <p className="text-blue-100 text-xs mt-4">Based on {market} Market Intelligence</p>
                </div>
              ) : (
                <div className="py-12 text-slate-400">
                  <DollarSign className="w-12 h-12 mx-auto mb-4 opacity-20" />
                  <p className="font-medium">Enter details to see prediction</p>
                </div>
              )}
            </div>
            
            {error && (
              <div className="p-4 bg-red-50 border border-red-100 text-red-600 rounded-2xl text-sm">
                {error}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
