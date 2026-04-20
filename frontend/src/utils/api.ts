/**
 * src/utils/api.ts
 * ─────────────────
 * Thin fetch wrapper that automatically attaches the Supabase JWT to every request.
 * Used by all the existing screen files (users.tsx, quotations.tsx, etc.)
 * 
 * The base URL points at your FastAPI backend (set EXPO_PUBLIC_BACKEND_URL in .env).
 */
import { Platform } from 'react-native';
import { supabase } from '../lib/supabase';

const getBaseUrl = () => {
  if (Platform.OS === 'web' && typeof window !== 'undefined') {
    return 'http://localhost:3000';
  }
  // Point directly to Next.js admin panel backend
  return (process.env.EXPO_PUBLIC_API_URL || 'http://localhost:3000').replace(/\/api\/v1\/?$/, '').replace(/\/$/, '');
};

const BASE_URL = getBaseUrl();

async function getToken(): Promise<string | null> {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token ?? null;
}

async function request<T = any>(method: string, path: string, body?: any): Promise<T> {
  const token = await getToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config: RequestInit = { method, headers };
  if (body && method !== 'GET') {
    config.body = JSON.stringify(body);
  }

  // Always prefix with /api/v1 so callers use short paths like '/leads'
  // Trim trailing slashes from the path to avoid Next.js redirects
  const cleanPath = path.replace(/\/$/, '');
  const url = `${BASE_URL}/api/v1${cleanPath}`;
  const response = await fetch(url, config);

  if (!response.ok) {
    const errData = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail));
  }

  return response.json() as Promise<T>;
}

export const api = {
  get:    <T = any>(path: string)              => request<T>('GET',    path),
  post:   <T = any>(path: string, body?: any)  => request<T>('POST',   path, body),
  put:    <T = any>(path: string, body?: any)  => request<T>('PUT',    path, body),
  patch:  <T = any>(path: string, body?: any)  => request<T>('PATCH',  path, body),
  delete: <T = any>(path: string)              => request<T>('DELETE', path),
};
