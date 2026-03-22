import React, { useState } from 'react';
import axios from 'axios';
import { 
  DollarSign, Briefcase, Star, Cpu, Brain, Layers, Cloud, Sparkles, 
  FileText, TrendingUp, MapPin 
} from 'lucide-react';
import ResumeAnalyzer from './components/ResumeAnalyzer';
import './index.css';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'predict' | 'resume' | 'insights'>('predict');

  // --- Predictor State ---
  const [market, setMarket] = useState<'US' | 'India'>('India');
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [explanation, setExplanation] = useState<any[] | null>(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

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
    // This is a simplified mapping for the demo. In a real app, we'd map all fields correctly.
    // For now, we use the base sample and update key fields.
    const baseSample = [4.2, 0, 49, 0, 0, 0, 0, 0, 160, false, false, true, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, true, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, true, false, true, false, false, false, true, false];
    
    return baseSample.map((val, idx) => {
        if (idx === 0) return formData.rating;
        if (idx === 2) return formData.age;
        if (idx === 9) return formData.python ? 1 : 0;
        if (idx === 10) return formData.spark ? 1 : 0;
        if (idx === 11) return formData.cloud ? 1 : 0;
        if (idx === 12) return formData.ml ? 1 : 0;
        if (idx === 13) return formData.stats ? 1 : 0;
        return val; // Keep original value if not overwritten
    });
  };

  const handleExplain = async () => {
    setLoadingExplanation(true);
    try {
        const payload = { input: mapFeaturesForUS() };
        const res = await axios.post('http://localhost:5000/explain_us', payload);
        // Sort by absolute importance
        const sorted = res.data.explanation.sort((a: any, b: any) => Math.abs(b.shap_value) - Math.abs(a.shap_value));
        setExplanation(sorted);
    } catch (err) {
        console.error(err);
    } finally {
        setLoadingExplanation(false);
    }
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      // Pointing to the unified API on port 5000
      const baseUrl = 'http://localhost:5000'; 
      
      if (market === 'India') {
        const res = await axios.post(`${baseUrl}/predict_india`, formData);
        setPrediction(res.data.prediction_lpa);
      } else {
        const payload = { input: mapFeaturesForUS() };
        const res = await axios.post(`${baseUrl}/predict_us`, payload);
        setPrediction(res.data.prediction);
      }
    } catch (err: any) {
      console.error(err);
      setError('Connection failed. Please ensure the Docker API service is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Navigation Bar */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="bg-blue-600 text-white p-2 rounded-lg">
                <Briefcase className="w-5 h-5" />
              </div>
              <span className="font-bold text-xl tracking-tight">Salary<span className="text-blue-600">AI</span></span>
            </div>
            
            <div className="flex gap-1 bg-slate-100 p-1 rounded-xl">
              <button 
                onClick={() => setActiveTab('predict')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === 'predict' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <DollarSign className="w-4 h-4" /> Predictor
              </button>
              <button 
                onClick={() => setActiveTab('resume')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === 'resume' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <FileText className="w-4 h-4" /> Resume Intel
              </button>
              <button 
                onClick={() => setActiveTab('insights')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === 'insights' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <TrendingUp className="w-4 h-4" /> Insights
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto p-6">
        
        {/* --- SALARY PREDICTOR TAB --- */}
        {activeTab === 'predict' && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <header className="mb-10 text-center max-w-2xl mx-auto">
              <h1 className="text-4xl font-bold tracking-tight mb-4 text-slate-800">
                Predict Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">2026 Compensation</span>
              </h1>
              <p className="text-slate-500 text-lg">
                Leverage our SOTA Random Forest models trained on thousands of data points from Glassdoor & LinkedIn.
              </p>
            </header>

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

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-start">
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
                  {loading ? "Calculating..." : <>Predict Salary <DollarSign className="w-5 h-5" /></>}
                </button>
              </form>

              <div className="space-y-6">
                <div className={`p-8 rounded-3xl transition-all duration-500 flex flex-col items-center justify-center min-h-[300px] ${
                  prediction 
                    ? 'bg-blue-600 text-white shadow-2xl shadow-blue-200' 
                    : 'bg-white border-2 border-dashed border-slate-200 text-slate-400'
                }`}>
                  {prediction ? (
                    <div className="space-y-4 text-center animate-in zoom-in duration-300">
                      <p className="text-blue-100 text-sm font-medium uppercase tracking-wider">Estimated Annual Salary</p>
                      <div className="text-7xl font-black flex items-center justify-center gap-1">
                        <span className="text-4xl opacity-60">{market === 'India' ? '₹' : '$'}</span>
                        {Math.round(prediction).toLocaleString()}
                        <span className="text-4xl opacity-60">{market === 'India' ? 'L' : 'K'}</span>
                      </div>
                      <div className="inline-block bg-blue-500/30 px-4 py-2 rounded-lg text-sm">
                        Top {market === 'India' ? '10%' : '15%'} of market
                      </div>
                      
                      {market === 'US' && (
                        <div className="mt-4 pt-4 border-t border-blue-400/30">
                          <button 
                            onClick={handleExplain}
                            disabled={loadingExplanation}
                            className="text-sm font-semibold bg-white/20 hover:bg-white/30 px-4 py-2 rounded-full transition-all flex items-center gap-2 mx-auto"
                          >
                             {loadingExplanation ? 'Analyzing...' : <><Sparkles className="w-4 h-4" /> Explain AI Decision</>}
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center">
                      <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <DollarSign className="w-10 h-10 text-slate-300" />
                      </div>
                      <p className="font-medium text-slate-500">Enter details to see prediction</p>
                      <p className="text-sm text-slate-400 mt-2">AI-powered estimates based on<br/>real-time market data.</p>
                    </div>
                  )}
                </div>
                
                {explanation && (
                    <div className="bg-white p-6 rounded-2xl shadow-lg border border-slate-100 animate-in slide-in-from-top-4">
                        <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                            <Brain className="w-5 h-5 text-purple-600" /> What drove this number?
                        </h3>
                        <div className="space-y-3">
                            {explanation.slice(0, 5).map((item: any, idx: number) => (
                                <div key={idx} className="flex items-center justify-between text-sm">
                                    <span className="text-slate-600 font-medium">Factor #{item.feature_index}</span>
                                    <span className={`font-bold ${item.shap_value > 0 ? 'text-green-600' : 'text-red-500'}`}>
                                        {item.shap_value > 0 ? '+' : ''}{Math.round(item.shap_value * 100) / 100}k
                                    </span>
                                </div>
                            ))}
                            <p className="text-xs text-slate-400 mt-2 text-center italic">Top contributors based on SHAP analysis</p>
                        </div>
                    </div>
                )}
                
                {error && (
                  <div className="p-4 bg-red-50 border border-red-100 text-red-600 rounded-2xl text-sm flex items-center gap-2">
                     <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                    {error}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* --- RESUME INTELLIGENCE TAB --- */}
        {activeTab === 'resume' && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <header className="mb-8 text-center max-w-2xl mx-auto">
              <h1 className="text-3xl font-bold tracking-tight mb-2 text-slate-800">
                AI Resume Analysis
              </h1>
              <p className="text-slate-500">
                Upload your resume to automatically extract skills and get personalized salary-boosting recommendations.
              </p>
            </header>
            <ResumeAnalyzer />
          </div>
        )}

        {/* --- INSIGHTS TAB (Placeholder for now) --- */}
        {activeTab === 'insights' && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
             <header className="mb-10 text-center max-w-2xl mx-auto">
              <h1 className="text-3xl font-bold tracking-tight mb-4 text-slate-800">
                Market Insights <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded ml-2 align-middle">Beta</span>
              </h1>
            </header>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                        <MapPin className="text-blue-500 w-5 h-5"/> Regional Demand
                    </h3>
                    <div className="aspect-video bg-slate-100 rounded-xl flex items-center justify-center text-slate-400">
                        Interactive Heatmap Coming Soon
                    </div>
                </div>
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                        <TrendingUp className="text-green-500 w-5 h-5"/> Salary Trends (2025-2026)
                    </h3>
                    <div className="aspect-video bg-slate-100 rounded-xl flex items-center justify-center text-slate-400">
                        Trend Graph Coming Soon
                    </div>
                </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
};

export default App;
