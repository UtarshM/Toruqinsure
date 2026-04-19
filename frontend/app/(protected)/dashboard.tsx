import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, SafeAreaView, RefreshControl, Dimensions } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Spacing, FontSize, BorderRadius } from '../../src/utils/theme';
import { useAuth } from '../../src/context/AuthContext';
import { api } from '../../src/utils/api';

const { width } = Dimensions.get('window');
const CARD_WIDTH = (width - (Spacing.lg * 2) - Spacing.md) / 2;

export default function DashboardScreen() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [stats, setStats] = useState<any>({ leads: 0, revenue: 0, pending: 0, claims: 0 });
  const [refreshing, setRefreshing] = useState(false);

  const loadStats = useCallback(async () => {
    try {
      const data = await api.get('/dashboard/stats');
      setStats(data);
    } catch (e) {
      // Fallback for demo
      setStats({ leads: 124, revenue: '4.2L', pending: 12, claims: 5 });
    }
  }, []);

  useFocusEffect(useCallback(() => { loadStats(); }, [loadStats]));

  const onRefresh = async () => {
    setRefreshing(true);
    await loadStats();
    setRefreshing(false);
  };

  const modules = [
    { name: 'Leads', icon: 'people', color: '#3b82f6', route: '/(protected)/leads' },
    { name: 'Finance', icon: 'wallet', color: '#10b981', route: '/finance' },
    { name: 'CRM', icon: 'person-add', color: '#8b5cf6', route: '/crm' },
    { name: 'Claims', icon: 'document-text', color: '#f59e0b', route: '/claims' },
    { name: 'RTO', icon: 'car', color: '#ef4444', route: '/rto' },
    { name: 'Quotations', icon: 'clipboard', color: '#6366f1', route: '/quotations' },
  ];

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView 
        style={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.primary} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Good Evening,</Text>
            <Text style={styles.userName}>{user?.full_name || 'Admin'}</Text>
          </View>
          <TouchableOpacity onPress={logout} style={styles.logoutBtn}>
            <Ionicons name="log-out-outline" size={24} color={Colors.error} />
          </TouchableOpacity>
        </View>

        {/* Stats Cards */}
        <View style={styles.statsGrid}>
          <View style={[styles.statCard, { backgroundColor: '#eff6ff' }]}>
            <Ionicons name="flash" size={20} color="#3b82f6" />
            <Text style={styles.statValue}>{stats.leads}</Text>
            <Text style={styles.statLabel}>Total Leads</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: '#ecfdf5' }]}>
            <Ionicons name="trending-up" size={20} color="#10b981" />
            <Text style={styles.statValue}>₹{stats.revenue}</Text>
            <Text style={styles.statLabel}>Revenue</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: '#fffbeb' }]}>
            <Ionicons name="time" size={20} color="#f59e0b" />
            <Text style={styles.statValue}>{stats.pending}</Text>
            <Text style={styles.statLabel}>Pending</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: '#fef2f2' }]}>
            <Ionicons name="shield-checkmark" size={20} color="#ef4444" />
            <Text style={styles.statValue}>{stats.claims}</Text>
            <Text style={styles.statLabel}>Claims</Text>
          </View>
        </View>

        {/* Modules Section */}
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Business Modules</Text>
        </View>
        <View style={styles.moduleGrid}>
          {modules.map((m) => (
            <TouchableOpacity 
              key={m.name} 
              style={styles.moduleCard}
              onPress={() => router.push(m.route as any)}
            >
              <View style={[styles.moduleIcon, { backgroundColor: m.color + '15' }]}>
                <Ionicons name={m.icon as any} size={28} color={m.color} />
              </View>
              <Text style={styles.moduleName}>{m.name}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Recent Activity Placeholder */}
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          <TouchableOpacity><Text style={styles.seeAll}>See All</Text></TouchableOpacity>
        </View>
        <View style={styles.activityList}>
          {[1, 2, 3].map((i) => (
            <View key={i} style={styles.activityItem}>
              <View style={styles.activityDot} />
              <View>
                <Text style={styles.activityText}>New lead generated for Car Insurance</Text>
                <Text style={styles.activityTime}>{i * 10} mins ago</Text>
              </View>
            </View>
          ))}
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.background },
  container: { flex: 1 },
  header: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    padding: Spacing.lg,
    paddingTop: Spacing.xl,
  },
  greeting: { fontSize: FontSize.md, color: Colors.textMuted, fontWeight: '500' },
  userName: { fontSize: FontSize.xxl, fontWeight: '900', color: Colors.text, marginTop: 2 },
  logoutBtn: { width: 44, height: 44, borderRadius: 22, backgroundColor: Colors.errorBg, justifyContent: 'center', alignItems: 'center' },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: Spacing.lg, gap: Spacing.md },
  statCard: { width: CARD_WIDTH, padding: Spacing.lg, borderRadius: BorderRadius.lg, gap: 4 },
  statValue: { fontSize: FontSize.xxl, fontWeight: '900', color: Colors.text, marginTop: 4 },
  statLabel: { fontSize: FontSize.xs, color: Colors.textMuted, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.5 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: Spacing.lg, marginTop: Spacing.xxl, marginBottom: Spacing.md },
  sectionTitle: { fontSize: FontSize.lg, fontWeight: '800', color: Colors.text },
  seeAll: { fontSize: FontSize.sm, color: Colors.primary, fontWeight: '700' },
  moduleGrid: { flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: Spacing.lg, gap: Spacing.md },
  moduleCard: { width: CARD_WIDTH, backgroundColor: Colors.surface, padding: Spacing.lg, borderRadius: BorderRadius.lg, alignItems: 'center', borderWidth: 1, borderColor: Colors.border, gap: Spacing.sm },
  moduleIcon: { width: 56, height: 56, borderRadius: BorderRadius.md, justifyContent: 'center', alignItems: 'center' },
  moduleName: { fontSize: FontSize.md, fontWeight: '700', color: Colors.text },
  activityList: { paddingHorizontal: Spacing.lg, gap: Spacing.md },
  activityItem: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md, backgroundColor: Colors.surface, padding: Spacing.md, borderRadius: BorderRadius.sm, borderLeftWidth: 3, borderLeftColor: Colors.primary },
  activityDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: Colors.primary },
  activityText: { fontSize: FontSize.md, fontWeight: '600', color: Colors.text },
  activityTime: { fontSize: FontSize.xs, color: Colors.textLight, marginTop: 2 },
});
