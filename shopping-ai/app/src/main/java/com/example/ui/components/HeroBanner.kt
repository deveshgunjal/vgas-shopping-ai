package com.example.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Verified
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.AppLanguage
import com.example.model.LocalizedStrings
import com.example.ui.theme.AlertOrange
import com.example.ui.theme.CyberBorder
import com.example.ui.theme.CyberSurface
import com.example.ui.theme.NeonCyan
import com.example.ui.theme.NeonEmerald
import com.example.ui.theme.WhatsAppGreen

@Composable
fun HeroBanner(
  strings: LocalizedStrings,
  selectedLang: AppLanguage,
  isBotOnline: Boolean,
  onLanguageSelected: (AppLanguage) -> Unit,
  onBotClick: () -> Unit,
  modifier: Modifier = Modifier
) {
  Card(
    modifier = modifier.fillMaxWidth(),
    shape = RoundedCornerShape(20.dp),
    colors = CardDefaults.cardColors(containerColor = CyberSurface),
    elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
  ) {
    Box(
      modifier = Modifier
        .fillMaxWidth()
        .background(
          Brush.linearGradient(
            colors = listOf(
              Color(0xFF131A2A),
              Color(0xFF1E283F),
              Color(0xFF0F2027)
            )
          )
        )
        .border(1.dp, CyberBorder, RoundedCornerShape(20.dp))
        .padding(16.dp)
    ) {
      Column(modifier = Modifier.fillMaxWidth()) {
        // Top Row: Title + Language Switcher
        Row(
          modifier = Modifier.fillMaxWidth(),
          horizontalArrangement = Arrangement.SpaceBetween,
          verticalAlignment = Alignment.CenterVertically
        ) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
              imageVector = Icons.Default.Shield,
              contentDescription = "AI Shield",
              tint = NeonCyan,
              modifier = Modifier.size(28.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Column {
              Text(
                text = strings.appTitle,
                style = MaterialTheme.typography.titleLarge,
                color = Color.White,
                fontWeight = FontWeight.Bold
              )
              Text(
                text = "FastAPI Scraper • WhatsApp Bridge • Room DB",
                style = MaterialTheme.typography.labelSmall,
                color = NeonEmerald
              )
            }
          }

          // Language Selector Pills
          Row(
            modifier = Modifier
              .background(Color(0xFF0B0F19), RoundedCornerShape(16.dp))
              .border(1.dp, CyberBorder, RoundedCornerShape(16.dp))
              .padding(4.dp),
            verticalAlignment = Alignment.CenterVertically
          ) {
            Icon(
              imageVector = Icons.Default.Language,
              contentDescription = "Language",
              tint = NeonCyan,
              modifier = Modifier
                .size(16.dp)
                .padding(start = 4.dp)
            )
            Spacer(modifier = Modifier.width(4.dp))
            AppLanguage.values().forEach { lang ->
              val isSelected = lang == selectedLang
              Surface(
                modifier = Modifier
                  .clip(RoundedCornerShape(12.dp))
                  .clickable { onLanguageSelected(lang) },
                color = if (isSelected) NeonCyan else Color.Transparent
              ) {
                Text(
                  text = lang.code.uppercase(),
                  style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                  color = if (isSelected) Color.Black else Color(0xFF94A3B8),
                  modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
              }
            }
          }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Metrics Row
        Row(
          modifier = Modifier.fillMaxWidth(),
          horizontalArrangement = Arrangement.SpaceBetween
        ) {
          MetricBox(
            label = strings.totalSavingsLabel,
            value = "₹48,250",
            valueColor = NeonEmerald,
            modifier = Modifier.weight(1f)
          )
          Spacer(modifier = Modifier.width(8.dp))
          MetricBox(
            label = strings.fakeCaughtLabel,
            value = "14 Blocked",
            valueColor = AlertOrange,
            modifier = Modifier.weight(1f)
          )
          Spacer(modifier = Modifier.width(8.dp))
          MetricBox(
            label = "Affiliate Tag",
            value = "shoppingai-21",
            valueColor = Color(0xFFB388FF),
            modifier = Modifier.weight(1f)
          )
        }

        Spacer(modifier = Modifier.height(12.dp))

        // WhatsApp Bot Status Pill
        Surface(
          modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .clickable { onBotClick() },
          color = Color(0xFF0B0F19),
          shape = RoundedCornerShape(12.dp),
          border = androidx.compose.foundation.BorderStroke(1.dp, if (isBotOnline) WhatsAppGreen else Color.Gray)
        ) {
          Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
          ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
              Box(
                modifier = Modifier
                  .size(10.dp)
                  .background(if (isBotOnline) WhatsAppGreen else Color.Red, CircleShape)
              )
              Spacer(modifier = Modifier.width(8.dp))
              Text(
                text = if (isBotOnline) strings.botStatusOnline else strings.botStatusOffline,
                style = MaterialTheme.typography.labelMedium,
                color = if (isBotOnline) Color.White else Color(0xFF94A3B8)
              )
            }
            Text(
              text = "External bridge status: active",
              style = MaterialTheme.typography.labelSmall,
              color = NeonCyan,
              fontWeight = FontWeight.Bold
            )
          }
        }
      }
    }
  }
}

@Composable
private fun MetricBox(
  label: String,
  value: String,
  valueColor: Color,
  modifier: Modifier = Modifier
) {
  Column(
    modifier = modifier
      .background(Color(0xFF0B0F19).copy(alpha = 0.6f), RoundedCornerShape(10.dp))
      .border(1.dp, CyberBorder.copy(alpha = 0.5f), RoundedCornerShape(10.dp))
      .padding(8.dp),
    horizontalAlignment = Alignment.CenterHorizontally
  ) {
    Text(
      text = value,
      style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
      color = valueColor
    )
    Text(
      text = label,
      style = MaterialTheme.typography.labelSmall,
      color = Color(0xFF94A3B8),
      maxLines = 1
    )
  }
}
