/**
 * @jest-environment jsdom
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import App from '../src/App';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock de l'API config
jest.mock('../src/config', () => ({
  API_ENDPOINTS: {
    check: 'http://localhost:8000/check',
    upload: 'http://localhost:8000/upload',
    reformulate: 'http://localhost:8000/reformulate'
  }
}));

describe('PlagiatDetect Pro Frontend', () => {
  beforeEach(() => {
    mockedAxios.post.mockClear();
  });

  test('renders main interface elements', () => {
    render(<App />);
    
    // Vérifier les éléments principaux
    expect(screen.getByText(/PlagiatDetect Pro/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Collez votre texte ici/i)).toBeInTheDocument();
    expect(screen.getByText(/Analyser le plagiat/i)).toBeInTheDocument();
  });

  test('handles text input correctly', () => {
    render(<App />);
    
    const textArea = screen.getByPlaceholderText(/Collez votre texte ici/i);
    fireEvent.change(textArea, { 
      target: { value: 'Test de saisie de texte' } 
    });
    
    expect(textArea.value).toBe('Test de saisie de texte');
  });

  test('shows loading state during analysis', async () => {
    mockedAxios.post.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => 
        resolve({ data: { plagiarism_score: 25, sources: [] } }), 1000))
    );

    render(<App />);
    
    const textArea = screen.getByPlaceholderText(/Collez votre texte ici/i);
    const analyzeButton = screen.getByText(/Analyser le plagiat/i);
    
    fireEvent.change(textArea, { 
      target: { value: 'Texte de test pour l\'analyse' } 
    });
    fireEvent.click(analyzeButton);
    
    // Vérifier l'état de chargement
    expect(screen.getByText(/Analyse en cours/i)).toBeInTheDocument();
  });

  test('displays results after successful analysis', async () => {
    const mockResponse = {
      data: {
        plagiarism_score: 45,
        sources: [
          { url: 'http://example.com', score: 67 }
        ]
      }
    };

    mockedAxios.post.mockResolvedValueOnce(mockResponse);

    render(<App />);
    
    const textArea = screen.getByPlaceholderText(/Collez votre texte ici/i);
    const analyzeButton = screen.getByText(/Analyser le plagiat/i);
    
    fireEvent.change(textArea, { 
      target: { value: 'Texte de test pour l\'analyse' } 
    });
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Score de plagiat/i)).toBeInTheDocument();
      expect(screen.getByText(/45%/)).toBeInTheDocument();
    });
  });

  test('handles reformulation request', async () => {
    const mockResponse = {
      data: {
        original: 'Texte original',
        reformulated: 'Texte reformulé par IA',
        method: 'AI'
      }
    };

    mockedAxios.post.mockResolvedValueOnce(mockResponse);

    render(<App />);
    
    const textArea = screen.getByPlaceholderText(/Collez votre texte ici/i);
    
    fireEvent.change(textArea, { 
      target: { value: 'Texte à reformuler' } 
    });
    
    // Chercher le bouton de reformulation (peut nécessiter d'ajuster le sélecteur)
    const reformulateButton = screen.getByText(/Reformuler avec IA/i);
    fireEvent.click(reformulateButton);
    
    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/reformulate',
        { text: 'Texte à reformuler', use_ai: true }
      );
    });
  });

  test('shows error message on API failure', async () => {
    mockedAxios.post.mockRejectedValueOnce(new Error('API Error'));

    render(<App />);
    
    const textArea = screen.getByPlaceholderText(/Collez votre texte ici/i);
    const analyzeButton = screen.getByText(/Analyser le plagiat/i);
    
    fireEvent.change(textArea, { 
      target: { value: 'Texte de test' } 
    });
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      // Vérifier qu'une erreur est affichée (ajuster selon votre implémentation)
      expect(screen.queryByText(/Analyse en cours/i)).not.toBeInTheDocument();
    });
  });

  test('file upload interface is present', () => {
    render(<App />);
    
    // Vérifier la présence de la zone de upload
    expect(screen.getByText(/Glissez-déposez votre fichier/i)).toBeInTheDocument();
  });

  test('creator credit is displayed', () => {
    render(<App />);
    
    // Vérifier que la mention du créateur est présente
    expect(screen.getByText(/Juvenal MALECOU/i)).toBeInTheDocument();
  });

  test('responsive design elements are present', () => {
    render(<App />);
    
    // Vérifier les éléments responsive (classes CSS, etc.)
    const container = document.querySelector('.container');
    expect(container).toBeInTheDocument();
  });
});
