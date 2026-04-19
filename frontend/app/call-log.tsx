import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, SafeAreaView, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { api } from '../src/utils/api';
import { Colors, Spacing, FontSize, BorderRadius } from '../src/utils/theme';
import { Ionicons } from '@expo/vector-icons';

export default function CallLogScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ leadId: string; leadName: string }>();
  const [form, setForm] = useState({ lead_id: params.leadId || '', lead_name: params.leadName || '', duration: '', status: 'completed', outcome: 'interested', notes: '', follow_up_date: '' });
  const [loading, setLoading] = useState(false);

  const update = (key: string, val: string) => setForm(p => ({ ...p, [key]: val }));

  const submit = async () => {
    if (!form.lead_name) { Alert.alert('Error', 'Lead name is required'); return; }
    setLoading(true);
    try {
      await api.post('/calls/', form);
      router.back();
    } catch (e: any) { Alert.alert('Error', e.message); }
    finally { setLoading(false); }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <TouchableOpacity testID="back-btn" onPress={() => router.back()} style={styles.backBtn}><Ionicons name="close" size={24} color={Colors.text} /></TouchableOpacity>
        <Text style={styles.headerTitle}>Log Call</Text>
        <TouchableOpacity testID="save-call-btn" onPress={submit} disabled={loading} style={styles.saveBtn}><Text style={styles.saveBtnText}>{loading ? 'Saving...' : 'Save'}</Text></TouchableOpacity>
      </View>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
          {params.leadName ? (
            <View style={styles.leadBanner}><Ionicons name="person" size={18} color={Colors.primary} /><Text style={styles.leadBannerText}>{params.leadName}</Text></View>
          ) : (
            <><Text style={styles.label}>LEAD NAME</Text><TextInput testID="call-lead-name" style={styles.input} placeholder="Enter lead name" placeholderTextColor={Colors.textLight} value={form.lead_name} onChangeText={v => update('lead_name', v)} /></>
          )}

          <Text style={styles.label}>CALL DURATION</Text>
          <TextInput testID="call-duration" style={styles.input} placeholder="e.g., 5 min" placeholderTextColor={Colors.textLight} value={form.duration} onChangeText={v => update('duration', v)} />

          <Text style={styles.label}>CALL STATUS</Text>
          <View style={styles.chipRow}>
            {['completed', 'missed', 'no_answer'].map(t => (
              <TouchableOpacity key={t} style={[styles.chip, form.status === t && styles.chipActive]} onPress={() => update('status', t)}>
                <Text style={[styles.chipText, form.status === t && styles.chipTextActive]}>{t.replace(/_/g, ' ')}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.label}>OUTCOME</Text>
          <View style={styles.chipRow}>
            {['interested', 'not_interested', 'callback', 'meeting_scheduled', 'no_answer', 'wrong_number'].map(t => (
              <TouchableOpacity key={t} style={[styles.chip, form.outcome === t && styles.chipActive]} onPress={() => update('outcome', t)}>
                <Text style={[styles.chipText, form.outcome === t && styles.chipTextActive]}>{t.replace(/_/g, ' ')}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.label}>NOTES / REMARKS</Text>
          <TextInput testID="call-notes" style={[styles.input, styles.textArea]} placeholder="Call summary..." placeholderTextColor={Colors.textLight} value={form.notes} onChangeText={v => update('notes', v)} multiline numberOfLines={3} />

          <Text style={styles.label}>FOLLOW-UP DATE (OPTIONAL)</Text>
          <TextInput testID="call-followup-date" style={styles.input} placeholder="YYYY-MM-DD" placeholderTextColor={Colors.textLight} value={form.follow_up_date} onChangeText={v => update('follow_up_date', v)} />
          <View style={{ height: 40 }} />
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.background },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: Spacing.md, paddingVertical: Spacing.md, borderBottomWidth: 1, borderBottomColor: Colors.border },
  backBtn: { padding: Spacing.sm },
  headerTitle: { fontSize: FontSize.lg, fontWeight: '700', color: Colors.text },
  saveBtn: { backgroundColor: Colors.primary, paddingHorizontal: Spacing.lg, paddingVertical: Spacing.sm, borderRadius: BorderRadius.sm },
  saveBtnText: { color: Colors.white, fontWeight: '700', fontSize: FontSize.sm },
  scroll: { flex: 1 },
  scrollContent: { padding: Spacing.lg },
  leadBanner: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, backgroundColor: Colors.primaryLight, padding: Spacing.lg, borderRadius: BorderRadius.sm },
  leadBannerText: { fontSize: FontSize.lg, fontWeight: '700', color: Colors.primary },
  label: { fontSize: FontSize.xs, fontWeight: '700', color: Colors.textMuted, letterSpacing: 1.5, marginTop: Spacing.lg, marginBottom: Spacing.sm },
  input: { borderWidth: 1, borderColor: Colors.border, borderRadius: BorderRadius.sm, backgroundColor: Colors.surface, paddingHorizontal: Spacing.lg, height: 48, fontSize: FontSize.md, color: Colors.text },
  textArea: { height: 80, paddingTop: Spacing.md, textAlignVertical: 'top' },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  chip: { paddingHorizontal: Spacing.md, paddingVertical: Spacing.sm, borderRadius: BorderRadius.sm, borderWidth: 1, borderColor: Colors.border, backgroundColor: Colors.surface },
  chipActive: { backgroundColor: Colors.primary, borderColor: Colors.primary },
  chipText: { fontSize: FontSize.xs, fontWeight: '600', color: Colors.textMuted, textTransform: 'capitalize' },
  chipTextActive: { color: Colors.white },
});
