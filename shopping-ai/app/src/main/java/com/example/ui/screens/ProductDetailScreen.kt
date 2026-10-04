package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.TrackedProduct

/**
 * ProductDetailScreen — renders ONLY the fields the backend actually returned
 * for a tracked product.
 *
 * There are no hardcoded prices, star ratings, review counts, store price rows
 * or AI predictions here. Anything the store did not report is rendered as
 * "not reported" rather than filled in with a plausible-looking value.
 */
@Composable
fun ProductDetailScreen(
    product: TrackedProduct?,
    modifier: Modifier = Modifier
) {
    if (product == null) {
        EmptyDetailState(modifier)
        return
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(VgasBackground)
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        // Product image — only shown if the scraper actually returned one.
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(Color(0xFF1E293B)),
            contentAlignment = Alignment.Center
        ) {
            Text("no image returned", color = VgasTextMuted, fontSize = 13.sp)
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(product.title, color = VgasText, fontSize = 22.sp, fontWeight = FontWeight.Bold)

        Spacer(modifier = Modifier.height(8.dp))

        // Rating — 0 means the store did not report one, so nothing is claimed.
        Row(verticalAlignment = Alignment.CenterVertically) {
            if (product.reviewScore > 0f) {
                Text(
                    "★".repeat(product.reviewScore.toInt().coerceIn(1, 5)),
                    color = VgasGold,
                    fontSize = 16.sp
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    buildString {
                        append(String.format("%.1f", product.reviewScore))
                        if (product.reviewCount > 0) append(" (${product.reviewCount} reviews)")
                    },
                    color = VgasTextMuted,
                    fontSize = 14.sp
                )
            } else {
                Text("★ rating not reported by the store", color = VgasTextMuted, fontSize = 14.sp)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Price — current and original both come from the scrape.
        Row(verticalAlignment = Alignment.CenterVertically) {
            if (product.currentPrice > 0) {
                Text(
                    "₹${formatIndian(product.currentPrice)}",
                    color = VgasTertiary,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.ExtraBold
                )
            } else {
                Text("price unavailable", color = VgasTextMuted, fontSize = 22.sp)
            }

            if (product.originalPrice > 0 && product.originalPrice != product.currentPrice) {
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    "₹${formatIndian(product.originalPrice)}",
                    color = VgasTextMuted,
                    fontSize = 16.sp,
                    textDecoration = androidx.compose.ui.text.style.TextDecoration.LineThrough
                )
                Spacer(modifier = Modifier.width(12.dp))
                Box(
                    modifier = Modifier
                        .background(VgasRed.copy(alpha = 0.15f), RoundedCornerShape(8.dp))
                        .border(1.dp, VgasRed.copy(alpha = 0.35f), RoundedCornerShape(8.dp))
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text("-${product.discountPercent}%", color = VgasRed, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                }
            }
        }

        if (product.isFakeDiscount) {
            Spacer(modifier = Modifier.height(12.dp))
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(VgasRed.copy(alpha = 0.12f))
                    .border(1.dp, VgasRed.copy(alpha = 0.4f), RoundedCornerShape(12.dp))
                    .padding(12.dp)
            ) {
                Text(
                    "⚠️ Fake discount flagged${if (product.fakeReason.isNotBlank()) ": ${product.fakeReason}" else ""}",
                    color = VgasRed,
                    fontSize = 13.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Details — every row is omitted unless the backend supplied a value.
        Text("Details", color = VgasText, fontSize = 18.sp, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(10.dp))
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            DetailRow("Store", product.storeName)
            DetailRow("Category", product.category)
            DetailRow("Seller", product.sellerName)
            DetailRow("Coupon code", product.couponCode)
            DetailRow("Cashback", if (product.cashbackCoins > 0) "${product.cashbackCoins} coins" else "")
            DetailRow(
                "Lowest recorded",
                if (product.lowestRecordedPrice > 0) "₹${formatIndian(product.lowestRecordedPrice)}" else ""
            )
            DetailRow(
                "Quality score",
                if (product.qualityScore > 0) "${product.qualityScore}/100" else ""
            )
            DetailRow(
                "Functionality score",
                if (product.functionalityScore > 0) "${product.functionalityScore}/100" else ""
            )
            DetailRow("Source URL", product.url)
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Price history — only when the backend actually stored history points.
        val history = product.priceHistoryJson
            .split(",")
            .mapNotNull { it.trim().toIntOrNull() }
            .filter { it > 0 }
        if (history.isNotEmpty()) {
            Text("Recorded price history", color = VgasText, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                history.joinToString(" → ") { "₹${formatIndian(it)}" },
                color = VgasTextSecondary,
                fontSize = 13.sp
            )
        } else {
            Text("No price history recorded yet for this product.", color = VgasTextMuted, fontSize = 13.sp)
        }

        Spacer(modifier = Modifier.height(80.dp))
    }
}

@Composable
private fun EmptyDetailState(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .background(VgasBackground)
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("📦", fontSize = 48.sp)
        Spacer(modifier = Modifier.height(12.dp))
        Text("No product selected", color = VgasText, fontSize = 18.sp, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            "Scrape a product URL to see its real details here.",
            color = VgasTextMuted,
            fontSize = 14.sp
        )
    }
}

@Composable
private fun DetailRow(label: String, value: String) {
    // An absent value renders as an explicit "not reported" line rather than
    // being hidden, so the user can tell the difference between "missing" and
    // "not shown".
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(VgasCard)
            .border(1.dp, VgasBorder, RoundedCornerShape(10.dp))
            .padding(horizontal = 12.dp, vertical = 10.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(label, color = VgasTextSecondary, fontSize = 13.sp)
            Text(
                if (value.isBlank()) "not reported" else value,
                color = if (value.isBlank()) VgasTextMuted else VgasText,
                fontSize = 13.sp,
                fontWeight = if (value.isBlank()) FontWeight.Normal else FontWeight.Medium
            )
        }
    }
}

/** 134990 -> "1,34,990" (Indian digit grouping). */
private fun formatIndian(value: Int): String {
    val s = value.toString()
    if (s.length <= 3) return s
    val head = s.dropLast(3)
    val tail = s.takeLast(3)
    val buf = StringBuilder()
    var count = 0
    for (ch in head.reversed()) {
        buf.append(ch)
        count++
        if (count % 2 == 0 && count < head.length) buf.append(',')
    }
    return "${buf.reverse()},$tail"
}