import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, Alert } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import * as LocalAuthentication from 'expo-local-authentication';
import { useRouter } from 'expo-router';
import { Colors, Spacing, FontSize, BorderRadius } from '../src/utils/theme';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../src/store/authStore';

export default function PinLoginScreen() {
  const router = useRouter();
  const { session, setPinAuthenticated } = useAuthStore();
  const [pin, setPin] = useState('');
  const [storedPin, setStoredPin] = useState<string | null>(null);

  useEffect(() => {
    checkPin();
  }, []);

  const checkPin = async () => {
    const p = await SecureStore.getItemAsync('user_pin');
    setStoredPin(p);
    if (!p) {
      // If no PIN set, allow skip or force setup? 
      // For internal app, usually force setup.
    } else {
      // Auto-trigger biometric if available
      handleBiometric();
    }
  };

  const handleBiometric = async () => {
    const hasHardware = await LocalAuthentication.hasHardwareAsync();
    const isEnrolled = await LocalAuthentication.isEnrolledAsync();
    
    if (hasHardware && isEnrolled) {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Login with Biometrics',
        fallbackLabel: 'Use PIN',
      });
      if (result.success) {
        setPinAuthenticated(true);
        router.replace('/(protected)/dashboard');
      }
    }
  };

  const handlePress = (num: string) => {
    if (pin.length < 4) {
      const newPin = pin + num;
      setPin(newPin);
      if (newPin.length === 4) {
        verifyPin(newPin);
      }
    }
  };

  const verifyPin = async (enteredPin: string) => {
    if (storedPin) {
      if (enteredPin === storedPin) {
        setPinAuthenticated(true);
        router.replace('/(protected)/dashboard');
      } else {
        Alert.alert('Incorrect PIN', 'Please try again.');
        setPin('');
      }
    } else {
      // Setup mode
      await SecureStore.setItemAsync('user_pin', enteredPin);
      Alert.alert('PIN Set', 'Your security PIN has been saved.');
      setPinAuthenticated(true);
      router.replace('/(protected)/dashboard');
    }
  };

  const handleDelete = () => setPin(pin.slice(0, -1));

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Ionicons name="lock-closed" size={48} color={Colors.primary} />
        <Text style={styles.title}>{storedPin ? 'Enter Security PIN' : 'Set Security PIN'}</Text>
        <Text style={styles.subtitle}>Secure your account</Text>
      </View>

      <View style={styles.pinDots}>
        {[1, 2, 3, 4].map((i) => (
          <View key={i} style={[styles.dot, pin.length >= i && styles.dotActive]} />
        ))}
      </View>

      <View style={styles.keypad}>
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => (
          <TouchableOpacity key={num} style={styles.key} onPress={() => handlePress(num.toString())}>
            <Text style={styles.keyText}>{num}</Text>
          </TouchableOpacity>
        ))}
        <TouchableOpacity style={styles.key} onPress={handleBiometric}>
          <Ionicons name="finger-print" size={24} color={Colors.text} />
        </TouchableOpacity>
        <TouchableOpacity style={styles.key} onPress={() => handlePress('0')}>
          <Text style={styles.keyText}>0</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.key} onPress={handleDelete}>
          <Ionicons name="backspace-outline" size={24} color={Colors.text} />
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background, alignItems: 'center', justifyContent: 'center' },
  header: { alignItems: 'center', marginBottom: Spacing.xl * 2 },
  title: { fontSize: FontSize.xl, fontWeight: '700', color: Colors.text, marginTop: Spacing.md },
  subtitle: { fontSize: FontSize.md, color: Colors.textMuted, marginTop: 4 },
  pinDots: { flexDirection: 'row', gap: Spacing.md, marginBottom: Spacing.xl * 2 },
  dot: { width: 16, height: 16, borderRadius: 8, borderWidth: 2, borderColor: Colors.border },
  dotActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  keypad: { width: '80%', flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', gap: Spacing.lg },
  key: { width: '30%', aspectRatio: 1, borderRadius: 50, backgroundColor: Colors.surface, alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: Colors.border },
  keyText: { fontSize: FontSize.xxl, fontWeight: '600', color: Colors.text },
});
