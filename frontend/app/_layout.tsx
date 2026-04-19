import { Slot, useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { useEffect } from 'react';
import { Platform } from 'react-native';
import { supabase } from '../src/lib/supabase';
import { useAuthStore } from '../src/store/authStore';

export default function RootLayout() {
  const { session, setSession, setLoading, fetchProfile, setUserProfile, isPinAuthenticated } = useAuthStore();
  const segments = useSegments();
  const router = useRouter();
  const navigationState = useRootNavigationState();

  useEffect(() => {
    // Safety timeout: stop the spinner after 2 seconds no matter what
    const timeoutId = setTimeout(() => {
      setLoading(false);
    }, 2000);

    // 1. Check for an existing session on app launch
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      clearTimeout(timeoutId);
      setLoading(false);
    });

    // 2. Listen for auth state changes (login / logout / token refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);

      if (session) {
        // After login: fetch user profile (role + permissions) from FastAPI
        fetchProfile();
      } else {
        // After logout: clear the profile
        setUserProfile(null);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  // Route guard: redirect based on session state and PIN authentication
  useEffect(() => {
    // 1. Wait until navigation state is initialized
    if (!navigationState?.key) return;

    // 2. Use a small timeout to ensure Slot is mounted
    const timer = setTimeout(() => {
      const isWeb = Platform.OS === 'web';
      const inProtectedGroup = segments[0] === '(protected)';
      const inPinAuth = segments[0] === 'pin-auth';

      if (!session && inProtectedGroup) {
        router.replace('/login');
      } else if (session && !isPinAuthenticated && !inPinAuth && !isWeb) {
        // If logged in but PIN not verified yet, force PIN screen (SKIP ON WEB)
        router.replace('/pin-auth');
      } else if (session && (isPinAuthenticated || isWeb) && !inProtectedGroup) {
        // If fully authenticated or on web, go to dashboard
        router.replace('/(protected)/dashboard');
      }
    }, 1);

    return () => clearTimeout(timer);
  }, [session, isPinAuthenticated, segments, navigationState?.key]);

  return <Slot />;
}

