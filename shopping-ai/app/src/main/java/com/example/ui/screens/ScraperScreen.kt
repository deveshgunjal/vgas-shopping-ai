package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material.icons.filled.Public
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Verified
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.model.LocalizedStrings
import com.example.ui.theme.AlertOrange
import com.example.ui.theme.CyberBorder
import com.example.ui.theme.CyberSurface
import com.example.ui.theme.NeonCyan
import com.example.ui.theme.NeonEmerald
import com.example.ui.theme.ScamRed

@Composable
fun ScraperScreen(
  strings: LocalizedStrings,
  isScraping: Boolean,
  urlInput: String,
  scraperSteps: List<com.example.model.ScraperLogStep>,
  onUrlInputChanged: (String) -> Unit,
  onStartScrape: (String) -> Unit,
  modifier: Modifier = Modifier
) {
  var localUrl by remember { mutableStateOf(urlInput) }

  LazyColumn(
    modifier = modifier.fillMaxSize(),
    contentPadding = PaddingValues(16.dp),
    verticalArrangement = Arrangement.spacedBy(16.dp)
  ) {
    // Header Banner
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = CyberSurface),
        border = androidx.compose.foundation.BorderStroke(1.dp, NeonCyan)
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Public, contentDescription = null, tint = NeonCyan, modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text(
              text = "Backend Scraper Core Engine",
              style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
              color = Color.White
            )
          }
          Spacer(modifier = Modifier.height(6.dp))
          Text(
            text = "Powered by FastAPI, Playwright Headless Browser, Redis caching, and AI discount verification.",
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFF94A3B8)
          )
        }
      }
    }

    // Scrape Trigger Card
    item {
      Surface(
        modifier = Modifier.fillMaxWidth(),
        color = Color(0xFF131A2A),
        shape = RoundedCornerShape(16.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder)
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Text("Product Scraping & Verification", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold), color = NeonEmerald)
          Spacer(modifier = Modifier.height(8.dp))
          Row(verticalAlignment = Alignment.CenterVertically) {
            OutlinedTextField(
              value = localUrl,
              onValueChange = { localUrl = it; onUrlInputChanged(it) },
              placeholder = { Text("https://amazon.in/dp/...", color = Color(0xFF64748B)) },
              modifier = Modifier.weight(1f),
              singleLine = true,
              colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = NeonCyan,
                unfocusedBorderColor = CyberBorder,
                focusedTextColor = Color.White,
                unfocusedTextColor = Color.White
              ),
              shape = RoundedCornerShape(10.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Button(
              onClick = { if (localUrl.isNotBlank()) onStartScrape(localUrl) },
              enabled = !isScraping && localUrl.isNotBlank(),
              colors = ButtonDefaults.buttonColors(containerColor = NeonCyan, contentColor = Color.Black),
              shape = RoundedCornerShape(10.dp),
              modifier = Modifier.height(54.dp)
            ) {
              if (isScraping) {
                CircularProgressIndicator(modifier = Modifier.size(20.dp), color = Color.Black, strokeWidth = 2.dp)
              } else {
                Icon(Icons.Default.PlayArrow, contentDescription = null)
                Spacer(modifier = Modifier.width(4.dp))
                Text("Execute", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
              }
            }
          }
        }
      }
    }

    // Live Animated Scraper Pipeline Steps
    if (scraperSteps.isNotEmpty()) {
      item {
        Text("⚡ Real-Time Pipeline Execution:", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
      }
      items(scraperSteps) { step ->
        val stepColor = when (step.status) {
          "COMPLETED" -> NeonEmerald
          "CACHED" -> NeonCyan
          "ACTIVE" -> AlertOrange
          else -> Color(0xFF475569)
        }
        val stepIcon = when (step.status) {
          "COMPLETED" -> Icons.Default.CheckCircle
          "CACHED" -> Icons.Default.Memory
          "ACTIVE" -> Icons.Default.Schedule
          else -> Icons.Default.Schedule
        }

        Card(
          modifier = Modifier.fillMaxWidth(),
          shape = RoundedCornerShape(12.dp),
          colors = CardDefaults.cardColors(containerColor = Color(0xFF131A2A)),
          border = androidx.compose.foundation.BorderStroke(1.dp, stepColor.copy(alpha = 0.5f))
        ) {
          Row(
            modifier = Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
          ) {
            if (step.status == "ACTIVE") {
              CircularProgressIndicator(modifier = Modifier.size(22.dp), color = AlertOrange, strokeWidth = 2.5.dp)
            } else {
              Icon(imageVector = stepIcon, contentDescription = null, tint = stepColor, modifier = Modifier.size(22.dp))
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
              Text(step.stepName, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
              Text(step.detail, style = MaterialTheme.typography.bodyMedium, color = Color(0xFF94A3B8))
            }
            Surface(
              color = stepColor.copy(alpha = 0.2f),
              shape = RoundedCornerShape(6.dp),
              border = androidx.compose.foundation.BorderStroke(1.dp, stepColor)
            ) {
              Text(
                text = step.status,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                color = stepColor,
                modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
              )
            }
          }
        }
      }
    }

    // Architecture & Redis Cache Stats
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder)
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Text("🗄️ Redis Cache & Heuristics Engine Status", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = NeonCyan)
          Spacer(modifier = Modifier.height(10.dp))
          Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text("Cached Price Records:", color = Color(0xFF94A3B8), style = MaterialTheme.typography.bodyMedium)
            Text("Not available", color = Color(0xFF64748B), style = MaterialTheme.typography.bodyMedium)
          }
          Spacer(modifier = Modifier.height(6.dp))
          Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text("Average Scrape Latency:", color = Color(0xFF94A3B8), style = MaterialTheme.typography.bodyMedium)
            Text("Not available", color = Color(0xFF64748B), style = MaterialTheme.typography.bodyMedium)
          }
          Spacer(modifier = Modifier.height(6.dp))
          Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text("Discount Risk Detection Accuracy:", color = Color(0xFF94A3B8), style = MaterialTheme.typography.bodyMedium)
            Text("Not available", color = Color(0xFF64748B), style = MaterialTheme.typography.bodyMedium)
          }
        }
      }
    }
  }
}
