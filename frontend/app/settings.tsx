import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../src/context/AuthContext';
import { Colors, Spacing, FontSize, BorderRadius } from '../src/utils/theme';
import { Ionicons } from '@expo/vector-icons';

export default function SettingsScreen() {
  const router = useRouter();
  const { user, logout } = useAuth();

  const sections = [
    { title: 'Account', items: [
      { label: 'Profile', icon: 'person-outline', desc: 'Manage your profile information' },
      { label: 'Change PIN', icon: 'keypad-outline', desc: 'Update your 4-digit PIN' },
      { label: 'Security', icon: 'shield-outline', desc: 'Password and authentication' },
    ]},
    { title: 'App Settings', items: [
      { label: 'Notifications', icon: 'notifications-outline', desc: 'Manage push notifications' },
      { label: 'Data & Storage', icon: 'cloud-outline', desc: 'Cache and data management' },
      { label: 'Language', icon: 'language-outline', desc: 'App language preferences' },
    ]},
    { title: 'About', items: [
      { label: 'Help & Support', icon: 'help-circle-outline', desc: 'Get help and FAQs' },
      { label: 'Terms of Service', icon: 'document-outline', desc: 'Terms and conditions' },
      { label: 'Privacy Policy', icon: 'lock-closed-outline', desc: 'How we handle your data' },
      { label: 'Version', icon: 'information-circle-outline', desc: 'AutoInsure v1.0.0' },
    ]},
  ];

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <TouchableOpacity testID="back-btn" onPress={() => router.back()}><Ionicons name="arrow-back" size={24} color={Colors.text} /></TouchableOpacity>
        <Text style={styles.title}>Settings</Text>
      </View>
      <ScrollView style={styles.scroll}>
        {sections.map((sec, si) => (
          <View key={si}>
            <Text style={styles.sectionTitle}>{sec.title.toUpperCase()}</Text>
            {sec.items.map((item, ii) => (
              <TouchableOpacity key={ii} testID={`setting-${item.label.toLowerCase().replace(/\s+/g, '-')}`} style={styles.item} activeOpacity={0.7}>
                <Ionicons name={item.icon as any} size={22} color={Colors.textMuted} />
                <View style={styles.itemInfo}>
                  <Text style={styles.itemLabel}>{item.label}</Text>
                  <Text style={styles.itemDesc}>{item.desc}</Text>
                </View>
                <Ionicons name="chevron-forward" size={18} color={Colors.textLight} />
              </TouchableOpacity>
            ))}
          </View>
        ))}
        <TouchableOpacity testID="logout-btn" style={styles.logoutBtn} onPress={async () => { await logout(); router.replace('/'); }}>
          <Ionicons name="log-out-outline" size={20} color={Colors.error} />
          <Text style={styles.logoutText}>Sign Out</Text>
        </TouchableOpacity>
        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.background },
  header: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: Spacing.lg, paddingTop: Spacing.lg, paddingBottom: Spacing.md, borderBottomWidth: 1, borderBottomColor: Colors.border, gap: Spacing.md },
  title: { flex: 1, fontSize: FontSize.xxl, fontWeight: '900', color: Colors.text },
  scroll: { flex: 1 },
  sectionTitle: { fontSize: FontSize.xs, fontWeight: '700', color: Colors.textMuted, letterSpacing: 1.5, paddingHorizontal: Spacing.lg, paddingTop: Spacing.xxl, paddingBottom: Spacing.sm },
  item: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: Spacing.lg, paddingVertical: Spacing.lg, borderBottomWidth: 1, borderBottomColor: Colors.border, gap: Spacing.md },
  itemInfo: { flex: 1 },
  itemLabel: { fontSize: FontSize.md, fontWeight: '600', color: Colors.text },
  itemDesc: { fontSize: FontSize.xs, color: Colors.textMuted, marginTop: 2 },
  logoutBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginHorizontal: Spacing.lg, marginTop: Spacing.xxl, paddingVertical: Spacing.lg, borderWidth: 1, borderColor: Colors.error, borderRadius: BorderRadius.sm, gap: Spacing.sm },
  logoutText: { fontSize: FontSize.md, fontWeight: '600', color: Colors.error },
});
