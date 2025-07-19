import { useState } from 'react';
import axios from 'axios';
import { API_ENDPOINTS } from './config';

function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [fileName, setFileName] = useState('');
  const [reformulatedText, setReformulatedText] = useState('');
  const [isReformulating, setIsReformulating] = useState(false);
  const [showReformulation, setShowReformulation] = useState(false);
  const [reformulationMethod, setReformulationMethod] = useState('');

  const simulateProgress = () => {
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) {
          clearInterval(interval);
          return 95; // On s'arrête à 95% et on finit quand la réponse arrive
        }
        return prev + Math.random() * 15;
      });
    }, 200);
    return interval;
  };

  const handleCheck = async () => {
    if (!text.trim()) return;
    
    setIsLoading(true);
    setResult(null);
    const progressInterval = simulateProgress();
    
    try {
      const res = await axios.post(API_ENDPOINTS.check, { text });
      setProgress(100);
      setTimeout(() => {
        setResult(res.data);
        setIsLoading(false);
        setProgress(0);
      }, 500);
    } catch (error) {
      console.error('Error:', error);
      setIsLoading(false);
      setProgress(0);
    }
    clearInterval(progressInterval);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setFileName(file.name);
    setIsLoading(true);
    setResult(null);
    const progressInterval = simulateProgress();
    
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await axios.post(API_ENDPOINTS.upload, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      setProgress(100);
      setTimeout(() => {
        setResult(res.data);
        setIsLoading(false);
        setProgress(0);
      }, 500);
    } catch (error) {
      console.error('Error:', error);
      setIsLoading(false);
      setProgress(0);
    }
    clearInterval(progressInterval);
  };

  const handleReformulate = async (useAI = true) => {
    if (!text.trim()) return;
    
    setIsReformulating(true);
    setReformulatedText('');
    
    try {
      const res = await axios.post(API_ENDPOINTS.reformulate, { 
        text, 
        use_ai: useAI 
      });
      setReformulatedText(res.data.reformulated);
      setReformulationMethod(res.data.method || (useAI ? 'AI' : 'Basic'));
      setShowReformulation(true);
    } catch (error) {
      console.error('Error:', error);
    }
    setIsReformulating(false);
  };

  const useReformulated = () => {
    setText(reformulatedText);
    setShowReformulation(false);
    setResult(null); // Reset les résultats précédents
  };

  const styles = {
    container: {
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh',
    },
    card: {
      background: 'white',
      borderRadius: '16px',
      padding: '40px',
      boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
      backdropFilter: 'blur(10px)',
    },
    title: {
      fontSize: '2.5rem',
      fontWeight: '700',
      color: '#2d3748',
      textAlign: 'center',
      marginBottom: '40px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
    section: {
      marginBottom: '30px',
    },
    sectionTitle: {
      fontSize: '1.3rem',
      fontWeight: '600',
      color: '#4a5568',
      marginBottom: '15px',
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
    },
    textarea: {
      width: '100%',
      minHeight: '150px',
      padding: '16px',
      border: '2px solid #e2e8f0',
      borderRadius: '12px',
      fontSize: '1rem',
      lineHeight: '1.5',
      resize: 'vertical',
      transition: 'all 0.3s ease',
      fontFamily: 'inherit',
    },
    textareaFocus: {
      outline: 'none',
      borderColor: '#667eea',
      boxShadow: '0 0 0 3px rgba(102, 126, 234, 0.1)',
    },
    button: {
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      border: 'none',
      padding: '12px 24px',
      borderRadius: '8px',
      fontSize: '0.9rem',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      marginTop: '15px',
      position: 'relative',
      overflow: 'hidden',
      minWidth: '180px',
      height: '44px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
    buttonHover: {
      transform: 'translateY(-2px)',
      boxShadow: '0 10px 20px rgba(102, 126, 234, 0.3)',
    },
    buttonDisabled: {
      opacity: 0.6,
      cursor: 'not-allowed',
      transform: 'none',
    },
    fileInput: {
      display: 'none',
    },
    fileLabel: {
      display: 'inline-block',
      padding: '12px 24px',
      background: '#f7fafc',
      border: '2px dashed #cbd5e0',
      borderRadius: '12px',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      textAlign: 'center',
      width: '100%',
      boxSizing: 'border-box',
    },
    fileLabelHover: {
      borderColor: '#667eea',
      background: '#edf2f7',
    },
    progressContainer: {
      margin: '20px 0',
      padding: '20px',
      background: '#f8f9fa',
      borderRadius: '12px',
      border: '1px solid #e9ecef',
    },
    progressBar: {
      width: '100%',
      height: '8px',
      background: '#e9ecef',
      borderRadius: '4px',
      overflow: 'hidden',
      marginBottom: '10px',
    },
    progressFill: {
      height: '100%',
      background: 'linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%)',
      borderRadius: '4px',
      transition: 'width 0.3s ease',
      backgroundSize: '200% 100%',
      animation: 'moveGradient 2s ease-in-out infinite',
    },
    resultCard: {
      background: '#f8f9fa',
      padding: '25px',
      borderRadius: '12px',
      marginTop: '25px',
      border: '1px solid #e9ecef',
    },
    scoreHigh: {
      color: '#e53e3e',
      fontSize: '1.8rem',
      fontWeight: '700',
    },
    scoreMedium: {
      color: '#dd6b20',
      fontSize: '1.8rem',
      fontWeight: '700',
    },
    scoreLow: {
      color: '#38a169',
      fontSize: '1.8rem',
      fontWeight: '700',
    },
    sourcesList: {
      marginTop: '20px',
    },
    sourceItem: {
      padding: '12px',
      background: 'white',
      borderRadius: '8px',
      marginBottom: '8px',
      border: '1px solid #e2e8f0',
      transition: 'all 0.2s ease',
    },
    sourceLink: {
      color: '#667eea',
      textDecoration: 'none',
      fontWeight: '500',
    },
    icon: {
      fontSize: '1.2rem',
    },
    reformulationCard: {
      background: '#fff3cd',
      border: '1px solid #ffeaa7',
      borderRadius: '12px',
      padding: '20px',
      marginTop: '20px',
    },
    reformulationTitle: {
      color: '#856404',
      fontSize: '1.2rem',
      fontWeight: '600',
      marginBottom: '15px',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
    },
    comparisonContainer: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '20px',
      marginBottom: '20px',
    },
    textBox: {
      background: 'white',
      border: '1px solid #ddd',
      borderRadius: '8px',
      padding: '15px',
      minHeight: '150px',
      fontSize: '0.9rem',
      lineHeight: '1.6',
    },
    buttonSecondary: {
      background: '#f8f9fa',
      color: '#495057',
      border: '2px solid #dee2e6',
      padding: '10px 20px',
      borderRadius: '8px',
      fontSize: '0.9rem',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      marginRight: '10px',
    },
    buttonSuccess: {
      background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
      color: 'white',
      border: 'none',
      padding: '12px 24px',
      borderRadius: '8px',
      fontSize: '0.9rem',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      minWidth: '180px',
      height: '44px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
    buttonAdvanced: {
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      border: 'none',
      padding: '12px 24px',
      borderRadius: '8px',
      fontSize: '0.9rem',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      marginRight: '10px',
      minWidth: '180px',
      height: '44px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
    footer: {
      marginTop: '40px',
      padding: '20px',
      textAlign: 'center',
      borderTop: '1px solid rgba(255, 255, 255, 0.1)',
    },
    footerText: {
      color: 'rgba(255, 255, 255, 0.8)',
      fontSize: '0.9rem',
      margin: 0,
      fontWeight: '500',
    },
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>🔍 Détecteur de Plagiat</h1>

        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>
            <span style={styles.icon}>📝</span>
            Analyser du texte
          </h2>
          <textarea
            rows="8"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Collez votre texte ici pour vérifier s'il contient du plagiat..."
            style={{
              ...styles.textarea,
              ...(text ? styles.textareaFocus : {})
            }}
          />
          <div style={{display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '15px'}} className="button-group">
            <button 
              onClick={handleCheck}
              disabled={isLoading || !text.trim()}
              style={{
                ...styles.button,
                ...(isLoading || !text.trim() ? styles.buttonDisabled : {})
              }}
              onMouseEnter={(e) => {
                if (!isLoading && text.trim()) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 10px 20px rgba(102, 126, 234, 0.3)';
                }
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = 'none';
              }}
            >
              {isLoading ? 'Analyse en cours...' : 'Analyser le texte'}
            </button>
            
            <button 
              onClick={() => handleReformulate(true)}
              disabled={isReformulating || !text.trim()}
              style={{
                ...styles.buttonAdvanced,
                ...(isReformulating || !text.trim() ? styles.buttonDisabled : {})
              }}
              title="Reformulation avancée avec IA (T5)"
              onMouseEnter={(e) => {
                if (!isReformulating && text.trim()) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 10px 20px rgba(102, 126, 234, 0.3)';
                }
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = 'none';
              }}
            >
              {isReformulating ? '🤖 IA en cours...' : '🤖 Reformulation IA'}
            </button>
            
            <button 
              onClick={() => handleReformulate(false)}
              disabled={isReformulating || !text.trim()}
              style={{
                ...styles.buttonSuccess,
                ...(isReformulating || !text.trim() ? styles.buttonDisabled : {})
              }}
              title="Reformulation rapide avec synonymes"
              onMouseEnter={(e) => {
                if (!isReformulating && text.trim()) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 10px 20px rgba(40, 167, 69, 0.3)';
                }
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = 'none';
              }}
            >
              {isReformulating ? '✨ Reformulation...' : '✨ Reformulation rapide'}
            </button>
          </div>
        </div>

        <div style={{textAlign: 'center', margin: '30px 0', color: '#a0aec0', fontWeight: '600'}}>
          ── ou ──
        </div>

        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>
            <span style={styles.icon}>📎</span>
            Importer un fichier
          </h2>
          <input 
            type="file" 
            accept=".pdf,.docx" 
            onChange={handleFileUpload}
            disabled={isLoading}
            style={styles.fileInput}
            id="fileInput"
          />
          <label 
            htmlFor="fileInput" 
            style={{
              ...styles.fileLabel,
              ...(isLoading ? styles.buttonDisabled : {})
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.target.style.borderColor = '#667eea';
                e.target.style.background = '#edf2f7';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading) {
                e.target.style.borderColor = '#cbd5e0';
                e.target.style.background = '#f7fafc';
              }
            }}
          >
            {fileName ? `📄 ${fileName}` : '📁 Choisir un fichier PDF ou DOCX'}
          </label>
        </div>

        {isLoading && (
          <div style={styles.progressContainer}>
            <div style={{textAlign: 'center', marginBottom: '15px', fontWeight: '600', color: '#4a5568'}}>
              🔄 Analyse en cours... {Math.round(progress)}%
            </div>
            <div style={styles.progressBar}>
              <div 
                style={{
                  ...styles.progressFill,
                  width: `${progress}%`
                }}
              />
            </div>
            <div style={{textAlign: 'center', fontSize: '0.9rem', color: '#718096'}}>
              Recherche de contenus similaires sur le web...
            </div>
          </div>
        )}

        {result && !isLoading && (
          <div style={styles.resultCard}>
            <h3 style={{marginBottom: '15px', color: '#2d3748'}}>📊 Résultats de l'analyse</h3>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px'}}>
              <span>Score de plagiat :</span>
              <span style={
                result.plagiarism_score > 70 ? styles.scoreHigh :
                result.plagiarism_score > 30 ? styles.scoreMedium :
                styles.scoreLow
              }>
                {result.plagiarism_score}%
              </span>
            </div>
            
            {result.plagiarism_score > 50 && (
              <div style={{
                background: '#fff3cd',
                border: '1px solid #ffeaa7',
                borderRadius: '8px',
                padding: '15px',
                marginBottom: '20px'
              }}>
                <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px'}}>
                  <span style={{fontSize: '1.2rem'}}>⚠️</span>
                  <span style={{fontWeight: '600', color: '#856404'}}>
                    Score de plagiat élevé détecté !
                  </span>
                </div>
                <p style={{margin: '0 0 15px 0', color: '#856404', fontSize: '0.9rem'}}>
                  Nous recommandons de reformuler votre texte pour réduire les similitudes.
                </p>
                <div style={{display: 'flex', gap: '10px', flexWrap: 'wrap'}} className="button-group">
                  <button 
                    onClick={() => handleReformulate(true)}
                    disabled={isReformulating}
                    style={{
                      ...styles.buttonAdvanced,
                      ...(isReformulating ? styles.buttonDisabled : {})
                    }}
                    title="Reformulation intelligente avec IA"
                  >
                    {isReformulating ? '🤖 IA en cours...' : '🤖 Reformulation IA'}
                  </button>
                  <button 
                    onClick={() => handleReformulate(false)}
                    disabled={isReformulating}
                    style={{
                      ...styles.buttonSuccess,
                      ...(isReformulating ? styles.buttonDisabled : {})
                    }}
                    title="Reformulation rapide avec synonymes"
                  >
                    {isReformulating ? '✨ Reformulation...' : '✨ Reformulation rapide'}
                  </button>
                </div>
              </div>
            )}
            
            {result.sources && result.sources.length > 0 && (
              <div style={styles.sourcesList}>
                <h4 style={{marginBottom: '15px', color: '#4a5568'}}>🔗 Sources détectées :</h4>
                {result.sources.map((source, i) => (
                  <div key={i} style={styles.sourceItem}>
                    <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                      <a 
                        href={source.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={styles.sourceLink}
                      >
                        {source.url.length > 60 ? source.url.substring(0, 60) + '...' : source.url}
                      </a>
                      <span style={{fontWeight: '600', color: source.score > 70 ? '#e53e3e' : source.score > 30 ? '#dd6b20' : '#38a169'}}>
                        {source.score}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {showReformulation && reformulatedText && (
          <div style={styles.reformulationCard}>
            <h3 style={styles.reformulationTitle}>
              <span>{reformulationMethod === 'AI' ? '🤖' : '✨'}</span>
              Texte reformulé {reformulationMethod === 'AI' ? 'par IA (T5)' : 'avec synonymes'} pour éviter le plagiat
            </h3>
            
            <div style={styles.comparisonContainer} className="comparison-container">
              <div>
                <h4 style={{marginBottom: '10px', color: '#6c757d'}}>📄 Texte original</h4>
                <div style={styles.textBox}>
                  {text}
                </div>
              </div>
              
              <div>
                <h4 style={{marginBottom: '10px', color: '#28a745'}}>✨ Texte reformulé</h4>
                <div style={{...styles.textBox, borderColor: '#28a745'}}>
                  {reformulatedText}
                </div>
              </div>
            </div>
            
            <div style={{textAlign: 'center'}}>
              <button 
                onClick={() => setShowReformulation(false)}
                style={styles.buttonSecondary}
              >
                Fermer
              </button>
              <button 
                onClick={useReformulated}
                style={styles.buttonSuccess}
              >
                ✅ Utiliser le texte reformulé
              </button>
            </div>
          </div>
        )}
      </div>
      
      {/* Footer avec mention du créateur */}
      <footer style={styles.footer}>
        <p style={styles.footerText}>
          Créé avec ❤️ par <strong>Juvenal MALECOU</strong>
        </p>
      </footer>
    </div>
  );
}

export default App;
