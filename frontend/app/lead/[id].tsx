import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, SafeAreaView, Linking, ActivityIndicator, Alert } from 'react-native';
import { useLocalSearchParams, useRouter, useFocusEffect } from 'expo-router';
import { api } from '../../src/utils/api';
import { Colors, Spacing, FontSize, BorderRadius, StatusColors } from '../../src/utils/theme';
import { Ionicons } from '@expo/vector-icons';

export default function LeadDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [lead, setLead] = useState<any>(null);
  const [calls, setCalls] = useState<any[]>([]);
  const [followups, setFollowups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [leadData, callsData] = await Promise.all([
        api.get<any>(`/leads/${id}`),
        api.get<any[]>(`/calls/?lead_id=${id}`),
      ]);
      // Map DB field names to what the UI expects
      const lead = {
        ...leadData,
        name: leadData.client_name,
        phone: leadData.client_phone,
        email: leadData.client_email,
      };
      setLead(lead);
      const callsArr = Array.isArray(callsData) ? callsData : (callsData as any).items || [];
      setCalls(callsArr);
      setFollowups([]);  // Phase 2 — populated once follow_ups module is built
    } catch {} finally { setLoading(false); }
  }, [id]);

  useFocusEffect(useCallback(() => { loadData(); }, [loadData]));

  const makeCall = () => { if (lead?.phone) Linking.openURL(`tel:${lead.phone}`); };
  const openWhatsApp = () => {
    if (lead?.phone) {
      const msg = `Hi ${lead.name}, this is regarding your ${lead.insurance_type || 'insurance'} inquiry for vehicle ${lead.vehicle_number || ''}. How can I help you today?`;
      Linking.openURL(`https://wa.me/91${lead.phone.replace(/\D/g, '')}?text=${encodeURIComponent(msg)}`);
    }
  };

  const updateStatus = async (status: string) => {
    try {
      await api.put(`/leads/${id}`, { status });
      setLead({ ...lead, status });
    } catch {}
  };

  if (loading) return <View style={styles.loadingView}><ActivityIndicator size="large" color={Colors.primary} /></View>;
  if (!lead) return <View style={styles.loadingView}><Text style={styles.errorText}>Lead not found</Text></View>;

  const sc = StatusColors[lead.status] || StatusColors.new;

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.headerBar}>
        <TouchableOpacity testID="back-btn" onPress={() => router.back()} style={styles.backBtn}><Ionicons name="arrow-back" size={24} color={Colors.text} /></TouchableOpacity>
        <Text style={styles.headerTitle}>Lead Detail</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView style={styles.scroll}>
        <View style={styles.nameSection}>
          <View style={styles.nameRow}>
            <View style={[styles.avatarLg, { backgroundColor: sc.bg }]}><Text style={[styles.avatarLgText, { color: sc.text }]}>{lead.name?.charAt(0)}</Text></View>
            <View style={styles.nameInfo}>
              <Text style={styles.leadName}>{lead.name}</Text>
              <Text style={styles.leadPhone}>{lead.phone}</Text>
              {lead.email ? <Text style={styles.leadEmail}>{lead.email}</Text> : null}
            </View>
          </View>
          <View style={[styles.statusBadgeLg, { backgroundColor: sc.bg }]}><Text style={[styles.statusTextLg, { color: sc.text }]}>{lead.status?.replace(/_/g, ' ')}</Text></View>
        </View>

        <View style={styles.actionsRow}>
          <TouchableOpacity testID="call-btn" style={[styles.actionBtn, { backgroundColor: Colors.success + '15' }]} onPress={makeCall}>
            <Ionicons name="call" size={22} color={Colors.success} />
            <Text style={[styles.actionLabel, { color: Colors.success }]}>Call</Text>
          </TouchableOpacity>
          <TouchableOpacity testID="whatsapp-btn" style={[styles.actionBtn, { backgroundColor: '#25D36615' }]} onPress={openWhatsApp}>
            <Ionicons name="logo-whatsapp" size={22} color="#25D366" />
            <Text style={[styles.actionLabel, { color: '#25D366' }]}>WhatsApp</Text>
          </TouchableOpacity>
          <TouchableOpacity testID="log-call-btn" style={[styles.actionBtn, { backgroundColor: Colors.primaryLight }]} onPress={() => router.push({ pathname: '/call-log', params: { leadId: id, leadName: lead.name } })}>
            <Ionicons name="create" size={22} color={Colors.primary} />
            <Text style={[styles.actionLabel, { color: Colors.primary }]}>Log Call</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.sectionLabel}>DETAILS</Text>
          <InfoRow label="Vehicle Type" value={lead.vehicle_type} />
          <InfoRow label="Vehicle Number" value={lead.vehicle_number} />
          <InfoRow label="Insurance Type" value={lead.insurance_type} />
          <InfoRow label="Source" value={lead.source} />
          <InfoRow label="Priority" value={lead.priority} />
          <InfoRow label="Company" value={lead.company} />
          {lead.notes ? <InfoRow label="Notes" value={lead.notes} /> : null}
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.sectionLabel}>UPDATE STATUS</Text>
          <View style={styles.statusGrid}>
            {['new','contacted','qualified','proposal','negotiation','won','lost'].map(s => {
              const ssc = StatusColors[s] || StatusColors.new;
              return (
                <TouchableOpacity testID={`status-${s}`} key={s} style={[styles.statusChip, { backgroundColor: lead.status === s ? ssc.bg : Colors.surface, borderColor: lead.status === s ? ssc.dot : Colors.border }]} onPress={() => updateStatus(s)}>
                  <View style={[styles.chipDot, { backgroundColor: ssc.dot }]} />
                  <Text style={[styles.chipText, { color: lead.status === s ? ssc.text : Colors.textMuted }]}>{s.replace(/_/g, ' ')}</Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        {calls.length > 0 && (
          <View style={styles.infoCard}>
            <Text style={styles.sectionLabel}>CALL HISTORY ({calls.length})</Text>
            {calls.slice(0, 5).map((c, i) => (
              <View key={i} style={styles.callItem}>
                <Ionicons name={c.status === 'completed' ? 'call' : 'call-outline'} size={16} color={c.status === 'completed' ? Colors.success : Colors.error} />
                <View style={styles.callInfo}>
                  <Text style={styles.callBy}>{c.caller_name} · {c.duration}</Text>
                  <Text style={styles.callNote}>{c.outcome} - {c.notes}</Text>
                </View>
              </View>
            ))}
          </View>
        )}

        {followups.length > 0 && (
          <View style={styles.infoCard}>
            <Text style={styles.sectionLabel}>FOLLOW-UPS ({followups.length})</Text>
            {followups.slice(0, 5).map((f, i) => {
              const fsc = StatusColors[f.status] || StatusColors.pending;
              return (
                <View key={i} style={styles.callItem}>
                  <View style={[styles.fDot, { backgroundColor: fsc.dot }]} />
                  <View style={styles.callInfo}>
                    <Text style={styles.callBy}>{f.type} · {f.date?.split('T')[0]}</Text>
                    <Text style={styles.callNote}>{f.notes}</Text>
                  </View>
                  <View style={[styles.fBadge, { backgroundColor: fsc.bg }]}><Text style={[styles.fBadgeText, { color: fsc.text }]}>{f.status}</Text></View>
                </View>
              );
            })}
          </View>
        )}
        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value || '-'}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.background },
  loadingView: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: Colors.background },
  errorText: { fontSize: FontSize.lg, color: Colors.textMuted },
  headerBar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: Spacing.md, paddingVertical: Spacing.md, borderBottomWidth: 1, borderBottomColor: Colors.border },
  backBtn: { padding: Spacing.sm },
  headerTitle: { fontSize: FontSize.lg, fontWeight: '700', color: Colors.text },
  scroll: { flex: 1 },
  nameSection: { padding: Spacing.lg, borderBottomWidth: 1, borderBottomColor: Colors.border },
  nameRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md, marginBottom: Spacing.md },
  avatarLg: { width: 56, height: 56, borderRadius: 28, justifyContent: 'center', alignItems: 'center' },
  avatarLgText: { fontSize: FontSize.xxl, fontWeight: '900' },
  nameInfo: { flex: 1 },
  leadName: { fontSize: FontSize.xxl, fontWeight: '900', color: Colors.text },
  leadPhone: { fontSize: FontSize.md, color: Colors.textMuted },
  leadEmail: { fontSize: FontSize.sm, color: Colors.textLight },
  statusBadgeLg: { alignSelf: 'flex-start', paddingHorizontal: Spacing.md, paddingVertical: Spacing.xs, borderRadius: BorderRadius.sm },
  statusTextLg: { fontSize: FontSize.sm, fontWeight: '700', textTransform: 'capitalize' },
  actionsRow: { flexDirection: 'row', padding: Spacing.lg, gap: Spacing.sm, borderBottomWidth: 1, borderBottomColor: Colors.border },
  actionBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: Spacing.md, borderRadius: BorderRadius.sm, gap: Spacing.sm },
  actionLabel: { fontSize: FontSize.sm, fontWeight: '700' },
  infoCard: { padding: Spacing.lg, borderBottomWidth: 1, borderBottomColor: Colors.border },
  sectionLabel: { fontSize: FontSize.xs, fontWeight: '700', color: Colors.textMuted, letterSpacing: 1.5, marginBottom: Spacing.md },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: Spacing.sm, borderBottomWidth: 1, borderBottomColor: Colors.surfaceMuted },
  infoLabel: { fontSize: FontSize.sm, color: Colors.textMuted, fontWeight: '500' },
  infoValue: { fontSize: FontSize.sm, color: Colors.text, fontWeight: '600', textTransform: 'capitalize' },
  statusGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  statusChip: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: Spacing.md, paddingVertical: Spacing.sm, borderRadius: BorderRadius.sm, borderWidth: 1, gap: 6 },
  chipDot: { width: 8, height: 8, borderRadius: 4 },
  chipText: { fontSize: FontSize.xs, fontWeight: '600', textTransform: 'capitalize' },
  callItem: { flexDirection: 'row', alignItems: 'flex-start', paddingVertical: Spacing.sm, borderBottomWidth: 1, borderBottomColor: Colors.surfaceMuted, gap: Spacing.sm },
  callInfo: { flex: 1 },
  callBy: { fontSize: FontSize.sm, fontWeight: '600', color: Colors.text },
  callNote: { fontSize: FontSize.xs, color: Colors.textMuted, marginTop: 2 },
  fDot: { width: 8, height: 8, borderRadius: 4, marginTop: 4 },
  fBadge: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: BorderRadius.sm },
  fBadgeText: { fontSize: FontSize.xs, fontWeight: '600' },
});
