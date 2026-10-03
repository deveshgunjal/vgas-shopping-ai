package com.example.ui.components

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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Analytics
import androidx.compose.material.icons.filled.CompareArrows
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Storefront
import androidx.compose.material.icons.filled.TrendingDown
import androidx.compose.material.icons.filled.Verified
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.style.TextOverflow
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
fun ProductCard(
  product: TrackedProduct,
  strings: LocalizedStrings,
  onViewChartClick: () -> Unit,
  onShareWhatsAppClick: () -> Unit,
  onDeleteClick: () -> Unit,
  isCompared: Boolean = false,
  onToggleCompare: (() -> Unit)? = null,
  onBuyClick: (() -> Unit)? = null,
  modifier: Modifier = Modifier
) {
  Card(
    modifier = modifier.fillMaxWidth(),
    shape = RoundedCornerShape(16.dp),
    colors = CardDefaults.cardColors(containerColor = CyberSurface),
    border = androidx.compose.foundation.BorderStroke(1.dp, if (product.isFakeDiscount) ScamRed.copy(alpha = 0.6f) else CyberBorder),
    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
  ) {
    Column(
      modifier = Modifier
        .fillMaxWidth()
        .padding(16.dp)
    ) {
      // Store Badge & Category Row
      Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
      ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
          Surface(
            color = getStoreColor(product.storeName).copy(alpha = 0.2f),
            shape = RoundedCornerShape(6.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, getStoreColor(product.storeName))
          ) {
            Row(
              modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
              verticalAlignment = Alignment.CenterVertically
            ) {
              Icon(
                imageVector = Icons.Default.Storefront,
                contentDescription = null,
                tint = getStoreColor(product.storeName),
                modifier = Modifier.size(12.dp)
              )
              Spacer(modifier = Modifier.width(4.dp))
              Text(
                text = product.storeName,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                color = getStoreColor(product.storeName)
              )
            }
          }

          Spacer(modifier = Modifier.width(8.dp))

          Surface(
            color = Color(0xFF1E283F),
            shape = RoundedCornerShape(6.dp)
          ) {
            Text(
              text = product.category,
              style = MaterialTheme.typography.labelSmall,
              color = Color(0xFF94A3B8),
              modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
            )
          }

          if (product.isLootDeal) {
            Spacer(modifier = Modifier.width(6.dp))
            Surface(color = Color(0xFFFF6D00).copy(alpha = 0.2f), shape = RoundedCornerShape(6.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFFF6D00))) {
              Text("🔥 LOOT ${product.discountPercent}% OFF", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.ExtraBold, fontSize = 9.sp), color = Color(0xFFFF6D00), modifier = Modifier.padding(horizontal = 5.dp, vertical = 2.dp))
            }
          } else if (product.isRefurbished) {
            Spacer(modifier = Modifier.width(6.dp))
            Surface(color = Color(0xFF00E676).copy(alpha = 0.2f), shape = RoundedCornerShape(6.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF00E676))) {
              Text("♻️ REFURBISHED", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.ExtraBold, fontSize = 9.sp), color = Color(0xFF00E676), modifier = Modifier.padding(horizontal = 5.dp, vertical = 2.dp))
            }
          } else if (product.isWholesale) {
            Spacer(modifier = Modifier.width(6.dp))
            Surface(color = Color(0xFFD500F9).copy(alpha = 0.2f), shape = RoundedCornerShape(6.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFD500F9))) {
              Text("📦 WHOLESALE B2B", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.ExtraBold, fontSize = 9.sp), color = Color(0xFFD500F9), modifier = Modifier.padding(horizontal = 5.dp, vertical = 2.dp))
            }
          }
        }

        IconButton(
          onClick = onDeleteClick,
          modifier = Modifier.size(28.dp)
        ) {
          Icon(
            imageVector = Icons.Default.Delete,
            contentDescription = "Delete",
            tint = Color(0xFF64748B),
            modifier = Modifier.size(18.dp)
          )
        }
      }

      Spacer(modifier = Modifier.height(10.dp))

      // Product Title
      Text(
        text = product.title,
        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
        color = Color.White,
        maxLines = 2,
        overflow = TextOverflow.Ellipsis
      )

      Spacer(modifier = Modifier.height(12.dp))

      // Price Breakdown Row
      Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.Bottom
      ) {
        Column {
          Text(
            text = strings.currentPriceLabel,
            style = MaterialTheme.typography.labelSmall,
            color = Color(0xFF94A3B8)
          )
          Row(verticalAlignment = Alignment.Bottom) {
            Text(
              text = "₹${formatPrice(product.currentPrice)}",
              style = MaterialTheme.typography.headlineMedium.copy(fontWeight = FontWeight.ExtraBold),
              color = if (product.isFakeDiscount) AlertOrange else NeonEmerald
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
              text = "₹${formatPrice(product.originalPrice)}",
              style = MaterialTheme.typography.bodyMedium.copy(
                textDecoration = TextDecoration.LineThrough
              ),
              color = Color(0xFF64748B),
              modifier = Modifier.padding(bottom = 2.dp)
            )
          }
        }

        Column(horizontalAlignment = Alignment.End) {
          Text(
            text = strings.lowestPriceLabel,
            style = MaterialTheme.typography.labelSmall,
            color = Color(0xFF94A3B8)
          )
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
              imageVector = Icons.Default.TrendingDown,
              contentDescription = null,
              tint = NeonCyan,
              modifier = Modifier.size(14.dp)
            )
            Spacer(modifier = Modifier.width(2.dp))
            Text(
              text = "₹${formatPrice(product.lowestRecordedPrice)}",
              style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Bold),
              color = NeonCyan
            )
          }
        }
      }

      Spacer(modifier = Modifier.height(12.dp))

      // Review, Quality & Functionality Score Bar
      Surface(
        modifier = Modifier.fillMaxWidth(),
        color = Color(0xFF0F172A),
        shape = RoundedCornerShape(10.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF334155))
      ) {
        Row(
          modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 12.dp, vertical = 8.dp),
          horizontalArrangement = Arrangement.SpaceBetween,
          verticalAlignment = Alignment.CenterVertically
        ) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Star, contentDescription = null, tint = Color(0xFFFFD700), modifier = Modifier.size(14.dp))
            Spacer(modifier = Modifier.width(4.dp))
            Text(
              text = "${product.reviewScore} (${product.reviewCount})",
              style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
              color = Color.White
            )
          }
          Text("•", color = Color(0xFF64748B))
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Verified, contentDescription = null, tint = NeonCyan, modifier = Modifier.size(14.dp))
            Spacer(modifier = Modifier.width(4.dp))
            Text(
              text = "Quality: ${product.qualityScore}%",
              style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
              color = NeonCyan
            )
          }
          Text("•", color = Color(0xFF64748B))
          Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
              text = "⚙️ Func: ${product.functionalityScore}%",
              style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
              color = NeonEmerald
            )
          }
        }
      }

      Spacer(modifier = Modifier.height(12.dp))

      // Discount Verification Badge
      Surface(
        modifier = Modifier.fillMaxWidth(),
        color = if (product.isFakeDiscount) ScamRed.copy(alpha = 0.15f) else NeonEmerald.copy(alpha = 0.15f),
        shape = RoundedCornerShape(10.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, if (product.isFakeDiscount) ScamRed else NeonEmerald)
      ) {
        Row(
          modifier = Modifier.padding(10.dp),
          verticalAlignment = Alignment.Top
        ) {
          Icon(
            imageVector = if (product.isFakeDiscount) Icons.Default.Warning else Icons.Default.Analytics,
            contentDescription = null,
            tint = if (product.isFakeDiscount) ScamRed else NeonEmerald,
            modifier = Modifier
              .size(18.dp)
              .padding(top = 2.dp)
          )
          Spacer(modifier = Modifier.width(8.dp))
          Column {
            Text(
              text = if (product.isFakeDiscount) strings.fakeDiscountAlert else strings.verifiedDeal,
              style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold),
              color = if (product.isFakeDiscount) ScamRed else NeonEmerald
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
              text = "${strings.fakeReasonPrefix} ${product.fakeReason}",
              style = MaterialTheme.typography.bodyMedium,
              color = Color(0xFFE2E8F0)
            )
          }
        }
      }

      Spacer(modifier = Modifier.height(14.dp))

      // Action Buttons (Top Row: Chart & WhatsApp)
      Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
      ) {
        Button(
          onClick = onViewChartClick,
          colors = ButtonDefaults.buttonColors(
            containerColor = Color(0xFF1E283F),
            contentColor = NeonCyan
          ),
          shape = RoundedCornerShape(10.dp),
          modifier = Modifier.weight(1f)
        ) {
          Icon(Icons.Default.Analytics, contentDescription = null, modifier = Modifier.size(16.dp))
          Spacer(modifier = Modifier.width(6.dp))
          Text(strings.viewChartBtn, style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
        }

        Spacer(modifier = Modifier.width(8.dp))

        Button(
          onClick = onShareWhatsAppClick,
          colors = ButtonDefaults.buttonColors(
            containerColor = WhatsAppGreen.copy(alpha = 0.2f),
            contentColor = WhatsAppGreen
          ),
          border = androidx.compose.foundation.BorderStroke(1.dp, WhatsAppGreen),
          shape = RoundedCornerShape(10.dp),
          modifier = Modifier.weight(1f)
        ) {
          Icon(Icons.Default.Share, contentDescription = null, modifier = Modifier.size(16.dp))
          Spacer(modifier = Modifier.width(6.dp))
          Text(strings.shareWhatsAppBtn, style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
        }
      }

      Spacer(modifier = Modifier.height(8.dp))

      // Action Buttons (Bottom Row: Compare & Buy Now)
      Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
      ) {
        if (onToggleCompare != null) {
          Button(
            onClick = onToggleCompare,
            colors = ButtonDefaults.buttonColors(
              containerColor = if (isCompared) Color(0xFF9333EA).copy(alpha = 0.3f) else Color(0xFF1E283F),
              contentColor = if (isCompared) Color(0xFFD8B4FE) else Color(0xFFE2E8F0)
            ),
            border = androidx.compose.foundation.BorderStroke(1.dp, if (isCompared) Color(0xFF9333EA) else CyberBorder),
            shape = RoundedCornerShape(10.dp),
            modifier = Modifier.weight(1f)
          ) {
            Icon(Icons.Default.CompareArrows, contentDescription = null, modifier = Modifier.size(16.dp))
            Spacer(modifier = Modifier.width(6.dp))
            Text(if (isCompared) "⚖️ Compared" else "+ Compare", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
          }
          Spacer(modifier = Modifier.width(8.dp))
        }

        if (onBuyClick != null) {
          Button(
            onClick = onBuyClick,
            colors = ButtonDefaults.buttonColors(
              containerColor = NeonEmerald,
              contentColor = Color.Black
            ),
            shape = RoundedCornerShape(10.dp),
            modifier = Modifier.weight(1f)
          ) {
            Icon(Icons.Default.ShoppingCart, contentDescription = null, modifier = Modifier.size(16.dp))
            Spacer(modifier = Modifier.width(6.dp))
            Text("🛒 Buy / Pay", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.ExtraBold))
          }
        }
      }
    }
  }
}

private fun getStoreColor(storeName: String): Color {
  return when {
    storeName.contains("Amazon", ignoreCase = true) -> Color(0xFFFF9900)
    storeName.contains("Flipkart", ignoreCase = true) -> Color(0xFF2874F0)
    storeName.contains("Myntra", ignoreCase = true) -> Color(0xFFFF3F6C)
    else -> Color(0xFF00E5FF)
  }
}

private fun formatPrice(price: Int): String {
  val str = price.toString()
  if (str.length <= 3) return str
  val last3 = str.takeLast(3)
  val rest = str.dropLast(3)
  return rest.chunked(2).joinToString(",") + "," + last3
}
