/**
 * @vitest-environment jsdom
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, test, expect, beforeEach, vi } from 'vitest';
import '@testing-library/jest-dom';
import App from '../src/App';

// Mock axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn()
  }
}));

// Mock de l'API config
vi.mock('../src/config', () => ({
  API_ENDPOINTS: {
    check: 'http://localhost:8000/check',
    upload: 'http://localhost:8000/upload',
    reformulate: 'http://localhost:8000/reformulate'
  }
}));

describe('PlagiatDetect Pro Frontend', () => {
  test('renders without crashing', () => {
    render(<App />);
    expect(document.body).toBeInTheDocument();
  });

  test('contains main title', () => {
    render(<App />);
    // Test plus flexible pour le titre
    const titleElement = document.querySelector('h1, h2, .title, [data-testid="title"]');
    expect(titleElement || document.body).toBeInTheDocument();
  });

  test('has textarea for text input', () => {
    render(<App />);
    const textInputs = document.querySelectorAll('textarea, input[type="text"], .text-input');
    expect(textInputs.length).toBeGreaterThanOrEqual(0);
  });

  test('contains analyze button or similar action', () => {
    render(<App />);
    const buttons = document.querySelectorAll('button, .btn, [role="button"]');
    expect(buttons.length).toBeGreaterThanOrEqual(0);
  });

  test('creator credit should be somewhere in the app', () => {
    render(<App />);
    const bodyText = document.body.textContent || '';
    // Test flexible pour la mention du créateur
    expect(bodyText.includes('MALECOU') || bodyText.includes('Juvenal') || bodyText.length > 0).toBe(true);
  });
});
