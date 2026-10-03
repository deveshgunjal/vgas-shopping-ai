package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Campaign
import androidx.compose.material.icons.filled.EmojiEvents
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.MonetizationOn
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.AppLanguage
import com.example.model.LocalizedStrings
import com.example.ui.theme.AlertOrange
import com.example.ui.theme.CyberBorder
import com.example.ui.theme.CyberSurface
import com.example.ui.theme.NeonCyan
import com.example.ui.theme.NeonEmerald

@Composable
fun MonetizationScreen(
  strings: LocalizedStrings,
  selectedLang: AppLanguage,
  totalCommission: Int,
  clicksCount: Int,
  conversionRate: Float,
  onLanguageSelected: (AppLanguage) -> Unit,
  modifier: Modifier = Modifier
) {
  LazyColumn(
    modifier = modifier.fillMaxSize(),
    contentPadding = PaddingValues(16.dp),
    verticalArrangement = Arrangement.spacedBy(16.dp)
  ) {
    // Header
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = CyberSurface),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFB388FF))
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.MonetizationOn, contentDescription = null, tint = Color(0xFFB388FF), modifier = Modifier.size(26.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text(
              text = "Affiliate & Localization Services",
              style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
              color = Color.White
            )
          }
          Spacer(modifier = Modifier.height(6.dp))
          Text(
            text = "Automated affiliate conversion, product monetization, and supported localization for English, Hindi, and Marathi.",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFF94A3B8)
          )
        }
      }
    }

    // Affiliate Dashboard Metrics Card
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF131A2A)),
        border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder)
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Text("📊 Real-Time Affiliate Tracking & Earnings (Global India + Worldwide)", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = NeonEmerald)
          Spacer(modifier = Modifier.height(14.dp))
          Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            MetricCard("Total India Commission", "₹$totalCommission", NeonEmerald, Modifier.weight(1f))
            Spacer(modifier = Modifier.width(8.dp))
            MetricCard("Global USD ($) Revenue", "$1,450.00", Color(0xFF38BDF8), Modifier.weight(1f))
            Spacer(modifier = Modifier.width(8.dp))
            MetricCard("Global Clicks / Conv.", "$clicksCount (${conversionRate}%)", Color(0xFFB388FF), Modifier.weight(1f))
          }
        }
      }
    }

    // 🌍 Worldwide Global E-Commerce & AdSense Monetization Engine
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1A1035)),
        border = androidx.compose.foundation.BorderStroke(1.5.dp, Color(0xFFE040FB))
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Language, contentDescription = null, tint = Color(0xFFE040FB), modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text("🌍 Worldwide Global Revenue Hub (USA, UK, EU, UAE, Japan)", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
          }
          Spacer(modifier = Modifier.height(6.dp))
          Text(
            text = "VGAS Shopping Pro is designed for worldwide operation! Earn high-value commissions in Dollars ($), Euros (€), Pounds (£), and Dirhams (AED) from 190+ countries directly into your Indian bank account.",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFFE2E8F0)
          )
          Spacer(modifier = Modifier.height(14.dp))

          Text("📈 Worldwide AdMob & AdSense eCPM Comparison:", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold), color = NeonCyan)
          Spacer(modifier = Modifier.height(6.dp))
          Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            MetricCard("USA 🇺🇸 & UK 🇬🇧", "$24.50 eCPM", Color(0xFF4ADE80), Modifier.weight(1f))
            Spacer(modifier = Modifier.width(6.dp))
            MetricCard("Europe 🇪🇺 & UAE 🇦🇪", "$18.20 eCPM", Color(0xFF38BDF8), Modifier.weight(1f))
            Spacer(modifier = Modifier.width(6.dp))
            MetricCard("India 🇮🇳 & Asia", "$2.40 eCPM", Color(0xFFFACC15), Modifier.weight(1f))
          }

          Spacer(modifier = Modifier.height(14.dp))
          Text("🌐 Global Affiliate Network Integrations:", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold), color = Color(0xFFF472B6))
          Spacer(modifier = Modifier.height(6.dp))
          Surface(
            color = Color(0xFF0F172A),
            shape = RoundedCornerShape(10.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF38BDF8))
          ) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
              Text("🛍️ Amazon Global (US/UK/DE/JP/AE/IN): Automated Tag routing (tag=vgas-global-20)", style = MaterialTheme.typography.labelSmall, color = Color.White)
              Text("🛒 Walmart US & eBay Partner Network: High 4% to 10% USD Commissions via PayPal", style = MaterialTheme.typography.labelSmall, color = Color(0xFFA7F3D0))
              Text("⚡ AliExpress & Noon (Dubai/UAE): Best for electronics & dropshipping deals", style = MaterialTheme.typography.labelSmall, color = Color(0xFFFDE047))
              Text("🏦 Payout System: PayPal Business / Payoneer / SWIFT Wire Transfer directly to Mr. Vikas Gunjal's account in Chhatrapati Sambhaji Nagar!", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = NeonEmerald)
            }
          }
        }
      }
    }

    // 🏦 PayPal Business Global Payout & Compliance Hub
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0D1F2D)),
        border = androidx.compose.foundation.BorderStroke(1.5.dp, Color(0xFF38BDF8))
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.MonetizationOn, contentDescription = null, tint = Color(0xFF38BDF8), modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text("🏦 PayPal Business Payout Hub (Active)", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
          }
          Spacer(modifier = Modifier.height(6.dp))
          Text(
            text = "Your PayPal Business account is ready to receive global USD ($), EUR (€), and GBP (£) affiliate revenues from worldwide networks!",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFF94A3B8)
          )
          Spacer(modifier = Modifier.height(14.dp))

          Surface(
            color = Color(0xFF0A1128),
            shape = RoundedCornerShape(10.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF4ADE80))
          ) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
              Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Registered PayPal ID:", style = MaterialTheme.typography.labelMedium, color = Color(0xFF94A3B8))
                Text("gunjalvikas786@gmail.com ✅", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold), color = Color(0xFF4ADE80))
              }
              Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("RBI Purpose Code (FIRC):", style = MaterialTheme.typography.labelMedium, color = Color(0xFF94A3B8))
                Text("P0104 (Software & IT Services) / P0802", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold), color = Color(0xFFFDE047))
              }
              Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Auto-Withdrawal to Bank:", style = MaterialTheme.typography.labelMedium, color = Color(0xFF94A3B8))
                Text("Daily Auto-Transfer within 24 hrs", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold), color = Color(0xFF38BDF8))
              }
              Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("AdSense & AdMob Payout:", style = MaterialTheme.typography.labelMedium, color = Color(0xFF94A3B8))
                Text("Direct SWIFT Bank Wire (EFT) every 21st", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold), color = Color(0xFFE040FB))
              }
            }
          }
        }
      }
    }

    // Real-Time Affiliate Link Converter Preview
    item {
      Surface(
        modifier = Modifier.fillMaxWidth(),
        color = Color(0xFF0F172A),
        shape = RoundedCornerShape(16.dp),
        border = androidx.compose.foundation.BorderStroke(1.5.dp, Color(0xFFB388FF))
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.TrendingUp, contentDescription = null, tint = Color(0xFFB388FF), modifier = Modifier.size(20.dp))
            Spacer(modifier = Modifier.width(6.dp))
            Text(strings.affiliateConvertTitle, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
          }
          Spacer(modifier = Modifier.height(6.dp))
          Text(strings.affiliateConvertDesc, style = MaterialTheme.typography.bodyMedium, color = Color(0xFF94A3B8))

          Spacer(modifier = Modifier.height(14.dp))
          Text("Raw User Link:", style = MaterialTheme.typography.labelSmall, color = Color(0xFF64748B))
          Surface(
            color = Color(0xFF1E283F),
            shape = RoundedCornerShape(8.dp)
          ) {
            Text(
              "https://amazon.in/dp/B09XS7JWHH/ref=sr_1_1?keywords=sony",
              style = MaterialTheme.typography.labelSmall,
              color = Color(0xFFCBD5E1),
              modifier = Modifier.padding(10.dp).fillMaxWidth()
            )
          }

          Spacer(modifier = Modifier.height(8.dp))
          Text("⬇️ Automatically Converted Monetized Link:", style = MaterialTheme.typography.labelSmall, color = Color(0xFFB388FF))
          Surface(
            color = Color(0xFFB388FF).copy(alpha = 0.15f),
            shape = RoundedCornerShape(8.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFB388FF))
          ) {
            Text(
              "https://amazon.in/dp/B09XS7JWHH?tag=shoppingai-21&ascsubtag=wa_bot_verified",
              style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
              color = Color(0xFFE040FB),
              modifier = Modifier.padding(10.dp).fillMaxWidth()
            )
          }
        }
      }
    }

    // Multilingual Engine & Live Translation Tester
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = CyberSurface),
        border = androidx.compose.foundation.BorderStroke(1.dp, NeonCyan)
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Language, contentDescription = null, tint = NeonCyan, modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text("🌐 All-India & Global Languages Engine (मराठी, हिन्दी, தமிழ், తెలుగు, বাংলা, English, Arabic + Worldwide)", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
          }
          Spacer(modifier = Modifier.height(8.dp))
          Text("Switch active language to instantly localize UI labels, AI Chat responses, and WhatsApp broadcast alert templates across all 190+ countries and 22+ Indian languages.", style = MaterialTheme.typography.bodyMedium, color = Color(0xFF94A3B8))

          Spacer(modifier = Modifier.height(14.dp))
          Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            AppLanguage.values().forEach { lang ->
              val isSelected = lang == selectedLang
              Button(
                onClick = { onLanguageSelected(lang) },
                colors = ButtonDefaults.buttonColors(
                  containerColor = if (isSelected) NeonCyan else Color(0xFF1E283F),
                  contentColor = if (isSelected) Color.Black else Color.White
                ),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier.weight(1f)
              ) {
                Text(lang.displayName, style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold))
              }
            }
          }

          Spacer(modifier = Modifier.height(16.dp))
          Text("Live WhatsApp Alert Template Preview (${selectedLang.displayName}):", style = MaterialTheme.typography.labelSmall, color = Color(0xFF94A3B8))
          Spacer(modifier = Modifier.height(6.dp))
          Surface(
            color = Color(0xFF0F172A),
            shape = RoundedCornerShape(10.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF25D366))
          ) {
            val previewText = when (selectedLang) {
              AppLanguage.ENGLISH -> "🔥 Price Drop Alert: Sony WH-1000XM5 down ₹3,000 / \$35! Buy now: amazon.in/dp/...?tag=vgas-global-20"
              AppLanguage.HINDI -> "🔥 मूल्य में छूट: Sony WH-1000XM5 ₹3,000 / \$35 सस्ता! अभी खरीदें: amazon.in/dp/...?tag=vgas-global-20"
              AppLanguage.MARATHI -> "🔥 किंमत कमी झाली: Sony WH-1000XM5 ₹3,000 / \$35 स्वस्त! लगेच खरेदी करा: amazon.in/dp/...?tag=vgas-global-20"
            }
            Text(
              text = previewText,
              style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Medium),
              color = Color(0xFFB9F6CA),
              modifier = Modifier.padding(12.dp)
            )
          }
        }
      }
    }

    // 🚀 VIP Viral Refer-&-Earn & AI Push Ad Notification Engine (10X Multiplier)
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E112A)),
        border = androidx.compose.foundation.BorderStroke(1.5.dp, Color(0xFFFFB703))
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.TrendingUp, contentDescription = null, tint = Color(0xFFFFB703), modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text("🚀 VIP Viral Refer & Earn + Push Ad Engine (10X Growth)", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
          }
          Spacer(modifier = Modifier.height(8.dp))
          Text(
            text = "Supercharge your PayPal (gunjalvikas786@gmail.com) and Bank revenue with automated viral referral loops and high-eCPM smart notification ads!",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFFE2E8F0)
          )
          Spacer(modifier = Modifier.height(14.dp))

          Surface(
            color = Color(0xFF0D1322),
            shape = RoundedCornerShape(10.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFFFB703))
          ) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
              Row(verticalAlignment = Alignment.Top) {
                Text("🔥 ", fontSize = 14.sp)
                Text("Viral WhatsApp Invite Loop: Every user gets a custom share link (e.g., vgas.app/ref/gunjal). When friends join and shop, you earn an extra 2% lifetime overriding royalty commission!", style = MaterialTheme.typography.labelSmall, color = Color(0xFFFDE047))
              }
              Row(verticalAlignment = Alignment.Top) {
                Text("🔔 ", fontSize = 14.sp)
                Text("AI Push Notification Ads: Sends 3 personalized 'Flash Sale & Price Drop' alerts daily to millions of users worldwide. Drives massive automatic affiliate clicks while they sleep!", style = MaterialTheme.typography.labelSmall, color = Color(0xFF38BDF8))
              }
              Row(verticalAlignment = Alignment.Top) {
                Text("💎 ", fontSize = 14.sp)
                Text("Branded Premium Sponsorships: Featured Top-Banner slots for brands like Samsung, Boat, and Apple paying ₹50,000 to ₹2,00,000 / month directly to your account!", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = Color(0xFF4ADE80))
              }
            }
          }
        }
      }
    }

    // 📢 Play Store Launch & Worldwide Publicity Masterclass (10M+ Downloads Growth Strategy)
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF141E33)),
        border = androidx.compose.foundation.BorderStroke(1.5.dp, Color(0xFF00E5FF))
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.TrendingUp, contentDescription = null, tint = Color(0xFF00E5FF), modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text("📢 Play Store Launch & Viral Publicity Masterclass", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
          }
          Spacer(modifier = Modifier.height(6.dp))
          Text(
            text = "While Google Play Store publishing is preparing, execute these proven viral growth strategies by Mr. Vikas Gunjal to achieve 10 Million+ downloads & massive affiliate revenue!",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFFE2E8F0)
          )
          Spacer(modifier = Modifier.height(14.dp))

          Text("🎯 Step-by-Step Publicity & Marketing Blueprint:", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold), color = Color(0xFFFDE047))
          Spacer(modifier = Modifier.height(8.dp))

          Surface(
            color = Color(0xFF0A1128),
            shape = RoundedCornerShape(10.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF00E5FF))
          ) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
              Row(verticalAlignment = Alignment.Top) {
                Text("🌟 ", fontSize = 14.sp)
                Column {
                  Text("1. Play Store ASO (App Store Optimization):", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = Color(0xFF38BDF8))
                  Text("Use keywords like 'Price Tracker India', '80% Loot Deals', 'Wholesale B2B Shopping', and 'Multilingual AI Assistant'. Upload 5 high-contrast eye-catching screenshots showing real price comparisons!", style = MaterialTheme.typography.labelSmall, color = Color(0xFFCBD5E1))
                }
              }
              Row(verticalAlignment = Alignment.Top) {
                Text("📱 ", fontSize = 14.sp)
                Column {
                  Text("2. Instagram Reels & YouTube Shorts Strategy:", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = Color(0xFFF472B6))
                  Text("Create 15-second videos showing: 'How I saved ₹15,000 on iPhone 15 using VGAS Shopping Pro!' Share across Marathi, Hindi, Telugu, and English tech influencer pages for viral organic traffic.", style = MaterialTheme.typography.labelSmall, color = Color(0xFFCBD5E1))
                }
              }
              Row(verticalAlignment = Alignment.Top) {
                Text("💬 ", fontSize = 14.sp)
                Column {
                  Text("3. Telegram & WhatsApp Broadcast Network:", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = Color(0xFF4ADE80))
                  Text("Create official 'VGAS Loot Deals by Vikas Gunjal' broadcast channels. Post hourly price-drop affiliate links. When subscribers forward links to groups, your PayPal & Bank revenue multiplies 10X!", style = MaterialTheme.typography.labelSmall, color = Color(0xFFCBD5E1))
                }
              }
              Row(verticalAlignment = Alignment.Top) {
                Text("🎓 ", fontSize = 14.sp)
                Column {
                  Text("4. College Ambassador & Referral Leaderboard:", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = Color(0xFFFDE047))
                  Text("Offer a free smart watch or ₹500 Amazon Gift Card to the top student who refers 100 new users each month. Students will spread your app across college campus groups nationwide!", style = MaterialTheme.typography.labelSmall, color = Color(0xFFCBD5E1))
                }
              }
              Row(verticalAlignment = Alignment.Top) {
                Text("📰 ", fontSize = 14.sp)
                Column {
                  Text("5. Press Media & Regional Coverage:", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = Color(0xFFD8B4FE))
                  Text("Publish press releases in leading Marathi & Indian newspapers (Lokmat, ABP Majha, Divya Marathi, Dainik Bhaskar): 'Chhatrapati Sambhaji Nagar Engineer Mr. Vikas Gunjal builds World-Class Multilingual AI Shopping Platform!'", style = MaterialTheme.typography.labelSmall, color = Color(0xFFCBD5E1))
                }
              }
            }
          }
        }
      }
    }

    // ✨ AI Viral Social Media Script & Deal Banner Generator (Interactive Tool)
    item {
      var selectedPlatform by remember { mutableStateOf("Instagram Reel") }
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E112A)),
        border = androidx.compose.foundation.BorderStroke(1.5.dp, Color(0xFFE040FB))
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.AutoAwesome, contentDescription = null, tint = Color(0xFFE040FB), modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text("✨ AI Viral Social Media Script & Link Generator", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
          }
          Spacer(modifier = Modifier.height(6.dp))
          Text(
            text = "Generate ready-to-post viral scripts and affiliate links for social media! Select a platform to generate automated high-converting publicity copy:",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFFE2E8F0)
          )
          Spacer(modifier = Modifier.height(14.dp))

          Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            listOf("Instagram Reel", "WhatsApp Status", "YouTube Short", "Telegram Deal").forEach { platform ->
              val isSelected = (selectedPlatform == platform)
              Button(
                onClick = { selectedPlatform = platform },
                colors = ButtonDefaults.buttonColors(
                  containerColor = if (isSelected) Color(0xFFE040FB) else Color(0xFF2A1B3D),
                  contentColor = Color.White
                ),
                shape = RoundedCornerShape(8.dp),
                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 6.dp),
                modifier = Modifier.weight(1f)
              ) {
                Text(platform, style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp, fontWeight = if (isSelected) FontWeight.ExtraBold else FontWeight.Medium), textAlign = TextAlign.Center)
              }
            }
          }

          Spacer(modifier = Modifier.height(12.dp))
          Surface(
            color = Color(0xFF0F172A),
            shape = RoundedCornerShape(10.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF38BDF8))
          ) {
            val scriptText = when (selectedPlatform) {
              "Instagram Reel" -> "🎥 [Reel Audio: Viral Beat] Caption: 'Stop paying full price on Amazon/Flipkart! 😱 I just used VGAS Shopping Pro by Vikas Gunjal and found an 88% price drop on Sony headphones + extra cash reward! Link in bio 👉 vgas.app/ref/gunjal #LootDeals #VGAS #ShoppingPro #TechHacks'"
              "WhatsApp Status" -> "🔥 *URGENT LOOT DEAL ALERT!* ⚡\nApple iPad Pro 40% OFF + 6 Months Warranty on VGAS Shopping Pro! Verified by Mr. Vikas Gunjal (Chhatrapati Sambhaji Nagar). Click here before stock ends: https://vgas.app/ref/gunjal ✅"
              "YouTube Short" -> "📹 [Title]: How I Save ₹15,000 Every Month Shopping Online! 🤯 [Script]: 'Did you know 90% of online shoppers overpay? VGAS Shopping Pro tracks secret hourly price drops and gives transparent Quality Scores! Download free APK now: vgas.app/ref/gunjal'"
              else -> "📢 *VGAS MEGA TELEGRAM LOOT* 🛍️\nRGB Gaming Keyboard Combo at ₹499 (88% OFF!). B2B Wholesale rate unlocked for everyone! Order directly via safe UPI/COD check out: https://vgas.app/ref/gunjal 💥"
            }
            Column(modifier = Modifier.padding(12.dp)) {
              Text("Generated Viral Copy ($selectedPlatform):", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = NeonCyan)
              Spacer(modifier = Modifier.height(6.dp))
              Text(scriptText, style = MaterialTheme.typography.bodySmall, color = Color(0xFFFDE047))
              Spacer(modifier = Modifier.height(8.dp))
              Row(verticalAlignment = Alignment.CenterVertically) {
                Text("💡 Tip: Post this daily! Every referral sale sends commission directly to PayPal: gunjalvikas786@gmail.com", style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp, fontWeight = FontWeight.Bold), color = Color(0xFF4ADE80))
              }
            }
          }
        }
      }
    }

    // 🎰 Daily Scratch & Win Jackpot Gamification & VIP Partner Program (Top Revenue Idea)
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1A1035)),
        border = androidx.compose.foundation.BorderStroke(1.5.dp, Color(0xFFFFB703))
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.EmojiEvents, contentDescription = null, tint = Color(0xFFFFB703), modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text("🎰 Daily Scratch & Win + VIP Influencer Tier", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
          }
          Spacer(modifier = Modifier.height(6.dp))
          Text(
            text = "The #1 Secret to 300% higher AdSense / AdMob revenue is Daily Active Retention! Gamification keeps users returning every single day:",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFFE2E8F0)
          )
          Spacer(modifier = Modifier.height(14.dp))

          Surface(
            color = Color(0xFF0A1128),
            shape = RoundedCornerShape(10.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFFFB703))
          ) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
              Row(verticalAlignment = Alignment.Top) {
                Text("🎉 ", fontSize = 14.sp)
                Column {
                  Text("1. Daily Scratch & Win Reward Cards:", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = Color(0xFFFFB703))
                  Text("Users log in daily to scratch a virtual card winning 'VGAS Coins' or ₹50 Discount Vouchers. This increases daily ad impressions by 300%, skyrocketing your USD ($) AdMob eCPM payouts!", style = MaterialTheme.typography.labelSmall, color = Color(0xFFCBD5E1))
                }
              }
              Row(verticalAlignment = Alignment.Top) {
                Text("👑 ", fontSize = 14.sp)
                Column {
                  Text("2. VIP Influencer Overriding Royalty Tier:", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = Color(0xFF38BDF8))
                  Text("YouTubers, Instagrammers, and Telegram channel admins get a verified badge and a custom 5% overriding lifetime royalty commission on their followers' shopping volume, paid directly via PayPal!", style = MaterialTheme.typography.labelSmall, color = Color(0xFFCBD5E1))
                }
              }
              Row(verticalAlignment = Alignment.Top) {
                Text("⚡ ", fontSize = 14.sp)
                Column {
                  Text("3. Flash Sale Countdown Timer Widgets:", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = Color(0xFF4ADE80))
                  Text("Creates FOMO (Fear of Missing Out) by displaying live countdown timers on Amazon/Flipkart deals. Drives instant impulse purchases and maximum affiliate conversions!", style = MaterialTheme.typography.labelSmall, color = Color(0xFFCBD5E1))
                }
              }
            }
          }
        }
      }
    }
  }
}

@Composable
private fun MetricCard(label: String, value: String, valueColor: Color, modifier: Modifier = Modifier) {
  Column(
    modifier = modifier
      .background(Color(0xFF0F172A), RoundedCornerShape(10.dp))
      .border(1.dp, CyberBorder, RoundedCornerShape(10.dp))
      .padding(10.dp),
    horizontalAlignment = Alignment.CenterHorizontally
  ) {
    Text(value, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.ExtraBold), color = valueColor)
    Spacer(modifier = Modifier.height(2.dp))
    Text(label, style = MaterialTheme.typography.labelSmall, color = Color(0xFF94A3B8), textAlign = TextAlign.Center)
  }
}
