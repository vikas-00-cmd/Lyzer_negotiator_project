import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock ResizeObserver (not available in jsdom)
global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
} as unknown as typeof ResizeObserver;

// Mock scrollIntoView (not available in jsdom)
Element.prototype.scrollIntoView = vi.fn();
