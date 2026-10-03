package com.example.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.TrendingDown
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.TrackedProduct
import com.example.model.LocalizedStrings
import com.example.ui.theme.AlertOrange
import com.example.ui.theme.CyberBorder
import com.example.ui.theme.CyberSurface
import com.example.ui.theme.NeonCyan
import com.example.ui.theme.NeonEmerald
import com.example.ui.theme.ScamRed
import com.example.ui.theme.WhatsAppGreen

@Composable
fun InteractivePriceChartModal(
  product: TrackedProduct,
  strings: LocalizedStrings,
  onClose: () -> Unit,
  onSendWhatsApp: () -> Unit,
  onCopyAffiliate: () -> Unit,
  modifier: Modifier = Modifier
) {
  val prices = product.priceHistoryJson
    .split(",")
    .mapNotNull { it.trim().toIntOrNull() }
    .ifEmpty { listOf(product.currentPrice, product.currentPrice) }

  val maxPrice = (prices.maxOrNull() ?: product.originalPrice).toFloat()
  val minPrice = (prices.minOrNull() ?: product.lowestRecordedPrice).toFloat()
  val priceRange = if (maxPrice - minPrice > 0) maxPrice - minPrice else 1000f

  Card(
    modifier = modifier.fillMaxWidth().padding(16.dp),
    shape = RoundedCornerShape(24.dp),
    colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
    border = androidx.compose.foundation.BorderStroke(1.5.dp, NeonCyan),
    elevation = CardDefaults.cardElevation(defaultElevation = 16.dp)
  ) {
    Column(
      modifier = Modifier
        .fillMaxWidth()
        .padding(20.dp)
    ) {
      // Header Row
      Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
      ) {
        Column(modifier = Modifier.weight(1f)) {
          Text(
            text = strings.priceHistoryTitle,
            style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
            color = Color.White
          )
          Text(
            text = product.title,
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFF94A3B8),
            maxLines = 1
          )
        }
        IconButton(onClick = onClose) {
          Icon(Icons.Default.Close, contentDescription = "Close", tint = Color.White)
        }
      }

      Spacer(modifier = Modifier.height(16.dp))

      // Price chart metadata row
      Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
      ) {
        Column {
          Text("Stated MRP", style = MaterialTheme.typography.labelSmall, color = Color(0xFF64748B))
          Text("₹${product.originalPrice}", style = MaterialTheme.typography.titleMedium, color = Color(0xFF94A3B8))
        }
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
          Text("Current Tracked", style = MaterialTheme.typography.labelSmall, color = Color(0xFF64748B))
          Text("₹${product.currentPrice}", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold), color = if (product.isFakeDiscount) AlertOrange else NeonEmerald)
        }
        Column(horizontalAlignment = Alignment.End) {
          Text("All-Time Low", style = MaterialTheme.typography.labelSmall, color = Color(0xFF64748B))
          Text("₹${product.lowestRecordedPrice}", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = NeonCyan)
        }
      }

      Spacer(modifier = Modifier.height(20.dp))

      // Custom Canvas Price Graph
      Box(
        modifier = Modifier
          .fillMaxWidth()
          .height(180.dp)
          .background(Color(0xFF0B0F19), RoundedCornerShape(12.dp))
          .border(1.dp, CyberBorder, RoundedCornerShape(12.dp))
          .padding(16.dp)
      ) {
        Canvas(modifier = Modifier.fillMaxWidth().height(148.dp)) {
          val canvasWidth = size.width
          val canvasHeight = size.height
          val stepX = if (prices.size > 1) canvasWidth / (prices.size - 1) else canvasWidth

          // Draw horizontal grid lines
          val gridColor = Color(0xFF1E283F)
          for (i in 0..3) {
            val y = canvasHeight * (i / 3f)
            drawLine(
              color = gridColor,
              start = Offset(0f, y),
              end = Offset(canvasWidth, y),
              strokeWidth = 1f
            )
          }

          val points = prices.mapIndexed { index, price ->
            val x = index * stepX
            val normalizedY = (price - minPrice) / priceRange
            val y = canvasHeight - (normalizedY * (canvasHeight * 0.8f) + (canvasHeight * 0.1f))
            Offset(x, y)
          }

          // Draw gradient fill under the line
          if (points.size > 1) {
            val fillPath = Path().apply {
              moveTo(points.first().x, canvasHeight)
              points.forEach { lineTo(it.x, it.y) }
              lineTo(points.last().x, canvasHeight)
              close()
            }
            drawPath(
              path = fillPath,
              brush = Brush.verticalGradient(
                colors = listOf(
                  if (product.isFakeDiscount) ScamRed.copy(alpha = 0.4f) else NeonCyan.copy(alpha = 0.4f),
                  Color.Transparent
                )
              )
            )

            // Draw line stroke
            val linePath = Path().apply {
              moveTo(points.first().x, points.first().y)
              for (i in 1 until points.size) {
                lineTo(points[i].x, points[i].y)
              }
            }
            drawPath(
              path = linePath,
              color = if (product.isFakeDiscount) AlertOrange else NeonCyan,
              style = Stroke(width = 3.5f, cap = StrokeCap.Round)
            )

            // Draw circle markers on each point
            points.forEachIndexed { idx, pt ->
              val isPeak = prices[idx] == prices.maxOrNull()
              drawCircle(
                color = if (isPeak && product.isFakeDiscount) ScamRed else if (idx == points.lastIndex) NeonEmerald else Color.White,
                radius = if (idx == points.lastIndex || (isPeak && product.isFakeDiscount)) 6f else 4f,
                center = pt
              )
            }
          }
        }

        // Floating label for inflation peak or savings
        if (product.isFakeDiscount) {
          Surface(
            modifier = Modifier.align(Alignment.TopEnd).padding(4.dp),
            color = ScamRed,
            shape = RoundedCornerShape(6.dp)
          ) {
            Text(
              text = "⚠️ Peak Inflation: ₹$maxPrice",
              style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
              color = Color.White,
              modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
            )
          }
        } else {
          Surface(
            modifier = Modifier.align(Alignment.BottomStart).padding(4.dp),
            color = NeonEmerald.copy(alpha = 0.2f),
            shape = RoundedCornerShape(6.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, NeonEmerald)
          ) {
            Text(
              text = "⚡ Real Drop Verified",
              style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
              color = NeonEmerald,
              modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
            )
          }
        }
      }

      Spacer(modifier = Modifier.height(16.dp))

      // Affiliate Converter Box
      Surface(
        modifier = Modifier.fillMaxWidth(),
        color = Color(0xFF1E283F),
        shape = RoundedCornerShape(12.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFB388FF))
      ) {
        Column(modifier = Modifier.padding(12.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
              text = "✨ Affiliate Link Converter (Commission Ready)",
              style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold),
              color = Color(0xFFB388FF)
            )
          }
          Spacer(modifier = Modifier.height(4.dp))
          Text(
            text = product.affiliateUrl,
            style = MaterialTheme.typography.labelSmall,
            color = Color(0xFFCBD5E1),
            maxLines = 1
          )
          Spacer(modifier = Modifier.height(8.dp))
          Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
          ) {
            Text(
              text = "Estimated Earnings: ~₹${(product.currentPrice * 0.045).toInt()} per sale",
              style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
              color = NeonEmerald
            )
            Button(
              onClick = onCopyAffiliate,
              colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFB388FF), contentColor = Color.Black),
              modifier = Modifier.height(32.dp),
              contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 12.dp, vertical = 4.dp)
            ) {
              Icon(Icons.Default.ContentCopy, contentDescription = null, modifier = Modifier.size(12.dp))
              Spacer(modifier = Modifier.width(4.dp))
              Text("Copy Tagged Link", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold))
            }
          }
        }
      }

      Spacer(modifier = Modifier.height(16.dp))

      // Send WhatsApp Broadcast Button
      Button(
        onClick = onSendWhatsApp,
        colors = ButtonDefaults.buttonColors(containerColor = WhatsAppGreen, contentColor = Color.White),
        modifier = Modifier.fillMaxWidth().height(48.dp),
        shape = RoundedCornerShape(12.dp)
      ) {
        Text("🟢 Broadcast Price Drop Alert to Subscribers", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold))
      }
    }
  }
}
