import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, SafeAreaView, RefreshControl, TextInput } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import { api } from '../../../src/utils/api';
import { Colors, Spacing, FontSize, BorderRadius, StatusColors } from '../../../src/utils/theme';
import { Ionicons } from '@expo/vector-icons';

export default function LeadsScreen() {
  const router = useRouter();
  const [leads, setLeads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState('');

  const loadLeads = useCallback(async () => {
    try {
      const data = await api.get<any[]>('/leads/');
      const arr = Array.isArray(data) ? data : (data as any).items || [];
      setLeads(arr);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(useCallback(() => { loadLeads(); }, [loadLeads]));

  const onRefresh = async () => {
    setRefreshing(true);
    await loadLeads();
    setRefreshing(false);
  };

  const filteredLeads = leads.filter(l => 
    (l.client_name || '').toLowerCase().includes(search.toLowerCase()) ||
    (l.vehicle_number || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={styles.title}>Leads Master</Text>
        <TouchableOpacity onPress={() => router.push('/lead/new')} style={styles.addBtn}>
          <Ionicons name="add" size={24} color={Colors.white} />
        </TouchableOpacity>
      </View>

      <View style={styles.searchContainer}>
        <Ionicons name="search" size={18} color={Colors.textLight} style={styles.searchIcon} />
        <TextInput 
          placeholder="Search leads or vehicle no..." 
          style={styles.searchInput}
          value={search}
          onChangeText={setSearch}
          placeholderTextColor={Colors.textLight}
        />
      </View>

      <FlatList
        data={filteredLeads}
        keyExtractor={(item) => item.id}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.primary} />}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="people-outline" size={64} color={Colors.textLight} />
            <Text style={styles.emptyText}>{loading ? 'Loading leads...' : 'No leads found'}</Text>
          </View>
        }
        renderItem={({ item }) => {
          const sc = StatusColors[item.status] || StatusColors.new;
          return (
            <TouchableOpacity 
              style={styles.card}
              onPress={() => router.push(`/lead/${item.id}`)}
            >
              <View style={styles.cardHeader}>
                <View style={[styles.avatar, { backgroundColor: sc.bg }]}>
                  <Text style={[styles.avatarText, { color: sc.text }]}>{item.client_name?.charAt(0)}</Text>
                </View>
                <View style={styles.leadInfo}>
                  <Text style={styles.leadName}>{item.client_name}</Text>
                  <Text style={styles.leadMeta}>{item.insurance_type} · {item.vehicle_number || 'N/A'}</Text>
                </View>
                <View style={[styles.badge, { backgroundColor: sc.bg }]}>
                  <Text style={[styles.badgeText, { color: sc.text }]}>{item.status}</Text>
                </View>
              </View>
              
              <View style={styles.cardFooter}>
                <View style={styles.footerItem}>
                  <Ionicons name="time-outline" size={14} color={Colors.textLight} />
                  <Text style={styles.footerText}>{new Date(item.created_at).toLocaleDateString()}</Text>
                </View>
                <Ionicons name="chevron-forward" size={16} color={Colors.textLight} />
              </View>
            </TouchableOpacity>
          );
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.background },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: Spacing.lg, paddingVertical: Spacing.md },
  backBtn: { width: 40, height: 40, justifyContent: 'center' },
  title: { fontSize: FontSize.xxl, fontWeight: '900', color: Colors.text },
  addBtn: { width: 40, height: 40, borderRadius: 20, backgroundColor: Colors.primary, justifyContent: 'center', alignItems: 'center' },
  searchContainer: { flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.surface, marginHorizontal: Spacing.lg, paddingHorizontal: Spacing.md, borderRadius: BorderRadius.md, height: 44, borderWidth: 1, borderColor: Colors.border, marginBottom: Spacing.md },
  searchIcon: { marginRight: Spacing.sm },
  searchInput: { flex: 1, fontSize: FontSize.md, color: Colors.text },
  listContent: { padding: Spacing.lg, gap: Spacing.md },
  card: { backgroundColor: Colors.surface, borderRadius: BorderRadius.lg, padding: Spacing.lg, borderWidth: 1, borderColor: Colors.border, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.05, shadowRadius: 10, elevation: 2 },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  avatar: { width: 48, height: 48, borderRadius: 24, justifyContent: 'center', alignItems: 'center' },
  avatarText: { fontSize: FontSize.xl, fontWeight: '900' },
  leadInfo: { flex: 1 },
  leadName: { fontSize: FontSize.lg, fontWeight: '800', color: Colors.text },
  leadMeta: { fontSize: FontSize.xs, color: Colors.textMuted, marginTop: 2, textTransform: 'uppercase', letterSpacing: 0.5 },
  badge: { paddingHorizontal: Spacing.md, paddingVertical: 4, borderRadius: BorderRadius.sm },
  badgeText: { fontSize: 10, fontWeight: '800', textTransform: 'uppercase' },
  cardFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: Spacing.lg, paddingTop: Spacing.md, borderTopWidth: 1, borderTopColor: Colors.border },
  footerItem: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  footerText: { fontSize: FontSize.xs, color: Colors.textLight },
  empty: { alignItems: 'center', marginTop: 100, gap: Spacing.md },
  emptyText: { fontSize: FontSize.md, color: Colors.textMuted, fontWeight: '600' },
});
