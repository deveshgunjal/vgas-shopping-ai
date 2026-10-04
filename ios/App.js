import React, { useState } from 'react';
import {
  StyleSheet, Text, View, TextInput, TouchableOpacity,
  ScrollView, ActivityIndicator, Linking, StatusBar, SafeAreaView
} from 'react-native';

const BACKEND = 'http://localhost:8000';

export default function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState('search'); // search | deals | earn | wallet

  async function searchProducts() {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND}/api/v1/search/?query=${encodeURIComponent(query)}&limit=6&sort_by=price_asc`);
      const data = await res.json();
      setResults(data.results || []);
    } catch {
      setResults([{ name: 'Server offline - Try again', price: 0, store: 'N/A', url: '#' }]);
    } finally { setLoading(false); }
  }

  async function loadDeals() {
    setLoading(true); setTab('deals');
    try {
      const res = await fetch(`${BACKEND}/api/v1/search/loot-deals?limit=6`);
      const data = await res.json();
      setResults(Array.isArray(data) ? data : data.results || []);
    } catch { setResults([]); }
    finally { setLoading(false); }
  }

  const formatPrice = (p) => `₹${Number(p || 0).toLocaleString('en-IN')}`;

  const ProductCard = ({ item }) => (
    <TouchableOpacity style={styles.card} onPress={() => item.url && item.url !== '#' && Linking.openURL(item.url)}>
      <Text style={styles.productName} numberOfLines={2}>{item.name}</Text>
      <View style={styles.cardRow}>
        <Text style={styles.price}>{formatPrice(item.price)}</Text>
        {item.discount_percentage > 0 && <Text style={styles.discount}>{item.discount_percentage}% OFF</Text>}
      </View>
      <View style={styles.cardRow}>
        <Text style={styles.store}>🏪 {item.store || 'Online'}</Text>
        {item.rating && <Text style={styles.rating}>⭐ {item.rating}</Text>}
      </View>
      {item.fake_discount && <Text style={styles.fakeAlert}>⚠️ FAKE DISCOUNT DETECTED!</Text>}
      <Text style={styles.buyBtn}>Buy Now →</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0a0a1a" />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🛍️ VGAS Shopping AI</Text>
        <Text style={styles.headerSub}>Vikas Gunjal Advance System</Text>
      </View>

      {/* Tabs */}
      <View style={styles.tabs}>
        {['search', 'deals', 'earn', 'wallet'].map(t => (
          <TouchableOpacity key={t} style={[styles.tab, tab === t && styles.activeTab]}
            onPress={() => { setTab(t); if (t === 'deals') loadDeals(); }}>
            <Text style={[styles.tabText, tab === t && styles.activeTabText]}>
              {t === 'search' ? '🔍' : t === 'deals' ? '🔥' : t === 'earn' ? '💰' : '👛'} {t.toUpperCase()}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Search Tab */}
      {tab === 'search' && (
        <View style={styles.searchBox}>
          <TextInput style={styles.input} placeholder="Product शोधा..." placeholderTextColor="#555"
            value={query} onChangeText={setQuery} onSubmitEditing={searchProducts} />
          <TouchableOpacity style={styles.searchBtn} onPress={searchProducts}>
            <Text style={styles.searchBtnText}>SEARCH</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Earn Tab */}
      {tab === 'earn' && (
        <ScrollView style={styles.infoPanel}>
          <Text style={styles.infoTitle}>💰 पैसे कसे कमवाल?</Text>
          {[
            { store: 'Amazon.in', commission: '4-10%', color: '#ff9900' },
            { store: 'Flipkart', commission: '5-10%', color: '#2874f0' },
            { store: 'Myntra', commission: '6-12%', color: '#ff3f6c' },
            { store: 'Meesho', commission: '15%', color: '#9f2089' },
          ].map((s, i) => (
            <View key={i} style={[styles.earnRow, { borderLeftColor: s.color }]}>
              <Text style={styles.earnStore}>{s.store}</Text>
              <Text style={[styles.earnCommission, { color: s.color }]}>{s.commission} Commission</Text>
            </View>
          ))}
          <TouchableOpacity style={styles.whatsappBtn}
            onPress={() => Linking.openURL('https://wa.me/919881300933?text=VGAS%20Affiliate%20Join')}>
            <Text style={styles.whatsappText}>📱 WhatsApp वर Join करा</Text>
          </TouchableOpacity>
        </ScrollView>
      )}

      {/* Wallet Tab */}
      {tab === 'wallet' && (
        <ScrollView style={styles.infoPanel}>
          <Text style={styles.infoTitle}>👛 Cashback Wallet</Text>
          <View style={styles.walletCard}>
            <Text style={styles.walletBalance}>₹450.50</Text>
            <Text style={styles.walletLabel}>Available Balance</Text>
          </View>
          <View style={styles.walletStats}>
            <View style={styles.walletStat}><Text style={styles.statVal}>₹2,850</Text><Text style={styles.statLabel}>Total Earned</Text></View>
            <View style={styles.walletStat}><Text style={styles.statVal}>₹125</Text><Text style={styles.statLabel}>Pending</Text></View>
          </View>
          <TouchableOpacity style={styles.withdrawBtn}>
            <Text style={styles.withdrawText}>💸 Withdraw to UPI</Text>
          </TouchableOpacity>
          <Text style={styles.walletNote}>Minimum withdrawal: ₹100 | Paid every week</Text>
        </ScrollView>
      )}

      {/* Results */}
      {(tab === 'search' || tab === 'deals') && (
        loading ? <ActivityIndicator size="large" color="#00d4ff" style={{ marginTop: 40 }} />
          : <ScrollView style={styles.results}>
              {results.map((item, i) => <ProductCard key={i} item={item} />)}
              {!results.length && !loading && (
                <Text style={styles.emptyText}>
                  {tab === 'search' ? '👆 उपर product शोधा' : '🔥 Loading deals...'}
                </Text>
              )}
            </ScrollView>
      )}

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>📞 +91 9881300933 | gunjalvikas786@gmail.com</Text>
      </View>
    </SafeAreaView>
  );
}

const C = { bg: '#0a0a1a', card: '#111128', accent: '#00d4ff', text: '#ffffff', sub: '#888' };

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: C.bg },
  header: { padding: 16, alignItems: 'center', borderBottomWidth: 1, borderBottomColor: '#1a1a3a' },
  headerTitle: { fontSize: 22, fontWeight: '800', color: C.accent },
  headerSub: { fontSize: 11, color: C.sub, marginTop: 2 },
  tabs: { flexDirection: 'row', backgroundColor: '#0d0d20', borderBottomWidth: 1, borderBottomColor: '#1a1a3a' },
  tab: { flex: 1, padding: 12, alignItems: 'center' },
  activeTab: { borderBottomWidth: 2, borderBottomColor: C.accent },
  tabText: { fontSize: 11, color: C.sub, fontWeight: '600' },
  activeTabText: { color: C.accent },
  searchBox: { flexDirection: 'row', padding: 12, gap: 8 },
  input: { flex: 1, backgroundColor: '#111128', color: C.text, borderRadius: 10, padding: 12, fontSize: 14, borderWidth: 1, borderColor: '#1a1a3a' },
  searchBtn: { backgroundColor: C.accent, borderRadius: 10, paddingHorizontal: 16, justifyContent: 'center' },
  searchBtnText: { color: '#000', fontWeight: '800', fontSize: 13 },
  results: { flex: 1, padding: 8 },
  card: { backgroundColor: C.card, borderRadius: 14, padding: 14, marginBottom: 10, borderWidth: 1, borderColor: '#1a1a3a' },
  productName: { color: C.text, fontSize: 14, fontWeight: '600', marginBottom: 8 },
  cardRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  price: { color: C.accent, fontSize: 18, fontWeight: '800' },
  discount: { color: '#00ff88', fontSize: 12, fontWeight: '700', backgroundColor: 'rgba(0,255,136,0.1)', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8 },
  store: { color: C.sub, fontSize: 12 },
  rating: { color: '#ffd700', fontSize: 12 },
  fakeAlert: { color: '#ff4444', fontSize: 12, fontWeight: '700', marginTop: 4 },
  buyBtn: { color: C.accent, fontSize: 13, fontWeight: '700', marginTop: 8, textAlign: 'right' },
  emptyText: { textAlign: 'center', color: C.sub, marginTop: 60, fontSize: 16 },
  infoPanel: { flex: 1, padding: 16 },
  infoTitle: { color: C.text, fontSize: 20, fontWeight: '800', marginBottom: 16 },
  earnRow: { backgroundColor: C.card, borderRadius: 10, padding: 14, marginBottom: 10, borderLeftWidth: 4 },
  earnStore: { color: C.text, fontSize: 15, fontWeight: '700' },
  earnCommission: { fontSize: 13, fontWeight: '600', marginTop: 4 },
  whatsappBtn: { backgroundColor: '#25D366', borderRadius: 12, padding: 16, alignItems: 'center', marginTop: 16 },
  whatsappText: { color: '#fff', fontWeight: '800', fontSize: 15 },
  walletCard: { backgroundColor: 'rgba(0,212,255,0.1)', borderRadius: 20, padding: 30, alignItems: 'center', borderWidth: 1, borderColor: C.accent, marginBottom: 16 },
  walletBalance: { color: C.accent, fontSize: 42, fontWeight: '900' },
  walletLabel: { color: C.sub, fontSize: 14, marginTop: 4 },
  walletStats: { flexDirection: 'row', gap: 12, marginBottom: 16 },
  walletStat: { flex: 1, backgroundColor: C.card, borderRadius: 12, padding: 16, alignItems: 'center' },
  statVal: { color: C.text, fontSize: 20, fontWeight: '800' },
  statLabel: { color: C.sub, fontSize: 12, marginTop: 4 },
  withdrawBtn: { backgroundColor: '#7c3aed', borderRadius: 12, padding: 16, alignItems: 'center' },
  withdrawText: { color: '#fff', fontWeight: '800', fontSize: 15 },
  walletNote: { color: C.sub, fontSize: 12, textAlign: 'center', marginTop: 12 },
  footer: { padding: 10, alignItems: 'center', borderTopWidth: 1, borderTopColor: '#1a1a3a' },
  footerText: { color: C.sub, fontSize: 11 },
});
