package com.example.ui.components

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material.icons.filled.Sort
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.TrackedProduct
import com.example.ui.theme.AlertOrange
import com.example.ui.theme.CyberBorder
import com.example.ui.theme.CyberSurface
import com.example.ui.theme.NeonCyan
import com.example.ui.theme.NeonEmerald
import com.example.ui.theme.ScamRed

@Composable
fun ComparisonModal(
  products: List<TrackedProduct>,
  onClose: () -> Unit,
  onBuyClick: (TrackedProduct) -> Unit,
  onRemoveProduct: (Int) -> Unit
) {
  Surface(
    modifier = Modifier
      .fillMaxWidth()
      .height(620.dp),
    color = Color(0xFF0F172A),
    shape = RoundedCornerShape(20.dp),
    border = androidx.compose.foundation.BorderStroke(2.dp, Color(0xFFC084FC))
  ) {
    Column(modifier = Modifier.fillMaxSize()) {
      // Header
      Surface(
        modifier = Modifier.fillMaxWidth(),
        color = Color(0xFF581C87)
      ) {
        Row(
          modifier = Modifier.padding(16.dp),
          verticalAlignment = Alignment.CenterVertically,
          horizontalArrangement = Arrangement.SpaceBetween
        ) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Sort, contentDescription = null, tint = Color.White)
            Spacer(modifier = Modifier.width(10.dp))
            Column {
              Text("Side-by-Side Product Comparison", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
              Text("Comparing Review ⭐, Quality 💎, Functionality ⚙️ & Price", style = MaterialTheme.typography.bodySmall, color = Color(0xFFE9D5FF))
            }
          }
          IconButton(onClick = onClose) {
            Icon(Icons.Default.Close, contentDescription = "Close", tint = Color.White)
          }
        }
      }

      if (products.isEmpty()) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
          Text("No products selected for comparison.", color = Color(0xFF94A3B8))
        }
      } else {
        Row(
          modifier = Modifier
            .weight(1f)
            .padding(16.dp)
            .horizontalScroll(rememberScrollState()),
          horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
          products.forEach { prod ->
            Card(
              modifier = Modifier
                .width(260.dp)
                .fillMaxSize(),
              colors = CardDefaults.cardColors(containerColor = CyberSurface),
              border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder),
              shape = RoundedCornerShape(16.dp)
            ) {
              Column(
                modifier = Modifier
                  .fillMaxSize()
                  .padding(14.dp)
                  .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.SpaceBetween
              ) {
                Column {
                  Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                  ) {
                    Surface(
                      color = NeonCyan.copy(alpha = 0.2f),
                      shape = RoundedCornerShape(6.dp)
                    ) {
                      Text(prod.storeName, style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = NeonCyan, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
                    }
                    IconButton(onClick = { onRemoveProduct(prod.id) }, modifier = Modifier.size(24.dp)) {
                      Icon(Icons.Default.Delete, contentDescription = null, tint = Color(0xFF64748B), modifier = Modifier.size(16.dp))
                    }
                  }

                  Spacer(modifier = Modifier.height(8.dp))
                  Text(prod.title, style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold), color = Color.White, maxLines = 2, overflow = TextOverflow.Ellipsis)

                  Spacer(modifier = Modifier.height(12.dp))
                  Text("Price Breakdown:", style = MaterialTheme.typography.labelSmall, color = Color(0xFF94A3B8))
                  Text("₹${prod.currentPrice}", style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.ExtraBold), color = NeonEmerald)
                  Text("Discount: ${prod.discountPercent}% OFF", style = MaterialTheme.typography.bodySmall, color = if (prod.isFakeDiscount) ScamRed else NeonCyan)

                  Spacer(modifier = Modifier.height(12.dp))
                  Surface(color = Color(0xFF1E293B), shape = RoundedCornerShape(8.dp), modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(10.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                      Text("⭐ Review Score: ${prod.reviewScore}/5", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold), color = Color(0xFFFFD700))
                      Text("💎 Quality Score: ${prod.qualityScore}/100", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold), color = NeonCyan)
                      Text("⚙️ Functionality: ${prod.functionalityScore}/100", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold), color = NeonEmerald)
                    }
                  }

                  Spacer(modifier = Modifier.height(12.dp))
                  Text("Seller & Authenticity:", style = MaterialTheme.typography.labelSmall, color = Color(0xFF94A3B8))
                  Text(prod.sellerName, style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
                  if (prod.isFakeDiscount) {
                    Text("⚠️ Fake Deal Alert", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = ScamRed)
                  }
                }

                Button(
                  onClick = { onBuyClick(prod) },
                  colors = ButtonDefaults.buttonColors(containerColor = NeonEmerald, contentColor = Color.Black),
                  shape = RoundedCornerShape(10.dp),
                  modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 16.dp)
                ) {
                  Icon(Icons.Default.ShoppingCart, contentDescription = null, modifier = Modifier.size(16.dp))
                  Spacer(modifier = Modifier.width(6.dp))
                  Text("Buy / Pay Now", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.ExtraBold))
                }
              }
            }
          }
        }
      }
    }
  }
}
