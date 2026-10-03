package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun ProductDetailScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(VgasBackground)
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        // Product Image
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(250.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(Color(0xFF1E293B)),
            contentAlignment = Alignment.Center
        ) {
            Text("📱", fontSize = 80.sp)
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Title
        Text("iPhone 15 Pro Max 256GB", color = VgasText, fontSize = 24.sp, fontWeight = FontWeight.Bold)

        Spacer(modifier = Modifier.height(8.dp))

        // Rating
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text("★★★★★", color = VgasGold, fontSize = 16.sp)
            Spacer(modifier = Modifier.width(8.dp))
            Text("4.5 (2,341 reviews)", color = VgasTextMuted, fontSize = 14.sp)
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Price
        Row(verticalAlignment = Alignment.Baseline) {
            Text("₹1,34,990", color = VgasTertiary, fontSize = 32.sp, fontWeight = FontWeight.ExtraBold)
            Spacer(modifier = Modifier.width(12.dp))
            Text("₹1,59,900", color = VgasTextMuted, fontSize = 18.sp)
            Spacer(modifier = Modifier.width(12.dp))
            Box(
                modifier = Modifier
                    .background(VgasRed.copy(alpha = 0.15f), RoundedCornerShape(8.dp))
                    .border(1.dp, VgasRed.copy(alpha = 0.35f), RoundedCornerShape(8.dp))
                    .padding(horizontal = 8.dp, vertical = 4.dp)
            ) {
                Text("-16%", color = VgasRed, fontSize = 12.sp, fontWeight = FontWeight.Bold)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // AI Prediction
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(VgasSecondary.copy(alpha = 0.1f))
                .border(1.dp, VgasSecondary.copy(alpha = 0.3f), RoundedCornerShape(12.dp))
                .padding(16.dp)
        ) {
            Column {
                Text("🤖 AI Price Prediction", color = VgasSecondary, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))
                Text("Expected price drop to ₹1,29,990 in 5 days", color = VgasText, fontSize = 14.sp)
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Store Prices
        Text("Store Prices", color = VgasText, fontSize = 18.sp, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(12.dp))

        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            StorePriceRow("Amazon", "₹1,34,990", true)
            StorePriceRow("Flipkart", "₹1,36,990", false)
            StorePriceRow("Myntra", "₹1,39,990", false)
            StorePriceRow("Meesho", "₹1,42,000", false)
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Delivery
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text("🚚", fontSize = 20.sp)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Free Delivery", color = VgasTertiary, fontSize = 14.sp)
            Spacer(modifier = Modifier.width(16.dp))
            Text("📦", fontSize = 20.sp)
            Spacer(modifier = Modifier.width(8.dp))
            Text("7 Day Returns", color = VgasTextSecondary, fontSize = 14.sp)
        }

        Spacer(modifier = Modifier.height(80.dp))
    }
}

@Composable
fun StorePriceRow(store: String, price: String, isBest: Boolean) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(if (isBest) VgasTertiary.copy(alpha = 0.1f) else VgasCard)
            .border(
                1.dp,
                if (isBest) VgasTertiary else VgasBorder,
                RoundedCornerShape(12.dp)
            )
            .padding(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(store, color = VgasText, fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
                if (isBest) {
                    Text("BEST PRICE", color = VgasTertiary, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }
            Text(price, color = if (isBest) VgasTertiary else VgasText, fontWeight = FontWeight.ExtraBold, fontSize = 16.sp)
        }
    }
}
