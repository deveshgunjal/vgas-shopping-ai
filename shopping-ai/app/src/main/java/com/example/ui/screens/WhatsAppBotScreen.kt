package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
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
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Campaign
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.LocalizedStrings
import com.example.model.WhatsAppLog
import com.example.ui.theme.AlertOrange
import com.example.ui.theme.CyberBorder
import com.example.ui.theme.CyberSurface
import com.example.ui.theme.NeonCyan
import com.example.ui.theme.NeonEmerald
import com.example.ui.theme.ScamRed
import com.example.ui.theme.WhatsAppGreen

@Composable
fun WhatsAppBotScreen(
  strings: LocalizedStrings,
  isBotOnline: Boolean,
  autoBroadcast: Boolean,
  autoConvert: Boolean,
  logs: List<WhatsAppLog>,
  onToggleBot: () -> Unit,
  onToggleBroadcast: (Boolean) -> Unit,
  onToggleConvert: (Boolean) -> Unit,
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
        border = androidx.compose.foundation.BorderStroke(1.dp, WhatsAppGreen)
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Chat, contentDescription = null, tint = WhatsAppGreen, modifier = Modifier.size(26.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text(
              text = "WhatsApp Bridge Status",
              style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
              color = Color.White
            )
          }
          Spacer(modifier = Modifier.height(6.dp))
          Text(
            text = "Bridge service status for remote WhatsApp delivery and verified discount alerts.",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFF94A3B8)
          )
        }
      }
    }

    // Bot Connection & Bridge Service Status
    item {
      Surface(
        modifier = Modifier.fillMaxWidth(),
        color = Color(0xFF131A2A),
        shape = RoundedCornerShape(16.dp),
        border = androidx.compose.foundation.BorderStroke(1.5.dp, if (isBotOnline) WhatsAppGreen else AlertOrange)
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
          ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
              Box(
                modifier = Modifier
                  .size(12.dp)
                  .background(if (isBotOnline) WhatsAppGreen else Color.Red, CircleShape)
              )
              Spacer(modifier = Modifier.width(8.dp))
              Text(
                text = if (isBotOnline) strings.botStatusOnline else strings.botStatusOffline,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                color = if (isBotOnline) WhatsAppGreen else Color(0xFF94A3B8)
              )
            }
            Button(
              onClick = onToggleBot,
              colors = ButtonDefaults.buttonColors(
                containerColor = if (isBotOnline) Color(0xFF1E283F) else WhatsAppGreen,
                contentColor = if (isBotOnline) Color(0xFF94A3B8) else Color.Black
              ),
              shape = RoundedCornerShape(8.dp)
            ) {
              Text(if (isBotOnline) "Disconnect" else "Set Bot Online", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
            }
          }
        }
      }
    }

    // Bot Automation Settings & Bridge Details
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = CyberSurface),
        border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder)
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Text("🤖 Bot Automation & Auto-Formatting", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = NeonCyan)
          Spacer(modifier = Modifier.height(12.dp))
          Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
          ) {
            Column(modifier = Modifier.weight(1f)) {
              Text(strings.autoBroadcastLabel, style = MaterialTheme.typography.bodyMedium, color = Color.White)
              Text("Delivers price drop notifications and verified alerts through the connected bridge.", style = MaterialTheme.typography.labelSmall, color = Color(0xFF64748B))
            }
            Switch(
              checked = autoBroadcast,
              onCheckedChange = onToggleBroadcast,
              colors = SwitchDefaults.colors(checkedThumbColor = WhatsAppGreen, checkedTrackColor = WhatsAppGreen.copy(alpha = 0.3f))
            )
          }

          Spacer(modifier = Modifier.height(12.dp))

          Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
          ) {
            Column(modifier = Modifier.weight(1f)) {
              Text(strings.affiliateConvertTitle, style = MaterialTheme.typography.bodyMedium, color = Color.White)
              Text("Auto-appends commission tags to Amazon & Flipkart links before broadcast.", style = MaterialTheme.typography.labelSmall, color = Color(0xFF64748B))
            }
            Switch(
              checked = autoConvert,
              onCheckedChange = onToggleConvert,
              colors = SwitchDefaults.colors(checkedThumbColor = Color(0xFFB388FF), checkedTrackColor = Color(0xFFB388FF).copy(alpha = 0.3f))
            )
          }

          Spacer(modifier = Modifier.height(16.dp))

          Text(
            "WhatsApp bot automation is available when the external bridge service is deployed and connected.",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFF94A3B8)
          )
        }
      }
    }

    // Live WhatsApp Broadcast Activity Log
    item {
      Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(Icons.Default.Campaign, contentDescription = null, tint = WhatsAppGreen, modifier = Modifier.size(20.dp))
        Spacer(modifier = Modifier.width(6.dp))
        Text("🟢 Live WhatsApp Broadcast Log:", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
      }
    }

    items(logs, key = { it.id }) { log ->
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF131A2A)),
        border = androidx.compose.foundation.BorderStroke(1.dp, if (log.isFakeWarning) ScamRed.copy(alpha = 0.5f) else WhatsAppGreen.copy(alpha = 0.5f))
      ) {
        Column(modifier = Modifier.padding(14.dp)) {
          Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Row(verticalAlignment = Alignment.CenterVertically) {
              Icon(
                imageVector = Icons.Default.Send,
                contentDescription = null,
                tint = if (log.isFakeWarning) ScamRed else WhatsAppGreen,
                modifier = Modifier.size(14.dp)
              )
              Spacer(modifier = Modifier.width(6.dp))
              Text(log.productTitle, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
            }
            Text(log.timestamp, style = MaterialTheme.typography.labelSmall, color = Color(0xFF64748B))
          }
          Spacer(modifier = Modifier.height(6.dp))
          Surface(
            color = if (log.isFakeWarning) ScamRed.copy(alpha = 0.15f) else WhatsAppGreen.copy(alpha = 0.15f),
            shape = RoundedCornerShape(8.dp)
          ) {
            Text(
              text = log.priceDropText,
              style = MaterialTheme.typography.bodyMedium,
              color = if (log.isFakeWarning) Color(0xFFFF8A80) else Color(0xFFB9F6CA),
              modifier = Modifier.padding(10.dp)
            )
          }
          Spacer(modifier = Modifier.height(8.dp))
          Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text("Delivered via verified bridge service", style = MaterialTheme.typography.labelSmall, color = Color(0xFF64748B))
            Text("👥 Sent to ${log.recipientCount} active subscribers", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = NeonCyan)
          }
        }
      }
    }
  }
}
