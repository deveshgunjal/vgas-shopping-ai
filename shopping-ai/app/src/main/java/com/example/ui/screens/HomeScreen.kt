package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// VGAS.AI Design Tokens
val VgasBackground = Color(0xFF0F131C)
val VgasCard = Color(0x991E293B)
val VgasBorder = Color(0x14FFFFFF)
val VgasPrimary = Color(0xFF6366F1)
val VgasSecondary = Color(0xFF22D3EE)
val VgasTertiary = Color(0xFF10B981)
val VgasGold = Color(0xFFF59E0B)
val VgasRed = Color(0xFFEF4444)
val VgasText = Color(0xFFF8FAFC)
val VgasTextSecondary = Color(0xFFCBD5E1)
val VgasTextMuted = Color(0xFF64748B)

@Composable
fun HomeScreen() {
    var searchText by remember { mutableStateOf("") }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        VgasBackground,
                        VgasBackground
                    )
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            // Top Bar
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(RoundedCornerShape(10.dp))
                            .background(
                                Brush.linearGradient(
                                    colors = listOf(VgasPrimary, Color(0xFF4F46E5))
                                )
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("V", color = Color.White, fontWeight = FontWeight.ExtraBold, fontSize = 18.sp)
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("VGAS", color = VgasText, fontWeight = FontWeight.ExtraBold, fontSize = 20.sp)
                    Text(".AI", color = VgasPrimary, fontWeight = FontWeight.ExtraBold, fontSize = 20.sp)
                }

                // Radar indicator
                Row(
                    modifier = Modifier
                        .border(1.dp, VgasBorder, RoundedCornerShape(20.dp))
                        .padding(horizontal = 8.dp, vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(RoundedCornerShape(4.dp))
                            .background(VgasSecondary)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("52 Stores", color = VgasSecondary, fontSize = 10.sp)
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Hero
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(VgasCard)
                    .border(1.dp, VgasBorder, RoundedCornerShape(16.dp))
                    .padding(16.dp)
            ) {
                Column {
                    // AI Badge
                    Row(
                        modifier = Modifier
                            .background(
                                VgasSecondary.copy(alpha = 0.1f),
                                RoundedCornerShape(6.dp)
                            )
                            .border(1.dp, VgasSecondary.copy(alpha = 0.3f), RoundedCornerShape(6.dp))
                            .padding(horizontal = 8.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("🤖", fontSize = 12.sp)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("NEURAL ARBITRAGE V4.2", color = VgasSecondary, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Text(
                        "Find Lowest Prices Across 10 Crore+ Products",
                        color = VgasText,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        lineHeight = 32.sp
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    // Search Bar
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(Color(0xFF0A0E17))
                            .border(1.dp, VgasBorder, RoundedCornerShape(12.dp))
                            .padding(horizontal = 12.dp, vertical = 12.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("🔍", fontSize = 16.sp)
                            Spacer(modifier = Modifier.width(8.dp))
                            TextField(
                                value = searchText,
                                onValueChange = { searchText = it },
                                placeholder = { Text("Search products...", color = VgasTextMuted, fontSize = 14.sp) },
                                colors = TextFieldDefaults.colors(
                                    focusedContainerColor = Color.Transparent,
                                    unfocusedContainerColor = Color.Transparent,
                                    focusedIndicatorColor = Color.Transparent,
                                    unfocusedIndicatorColor = Color.Transparent,
                                    focusedTextColor = VgasText,
                                    unfocusedTextColor = VgasText,
                                    cursorColor = VgasSecondary
                                ),
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Trending chips
                    Row(
                        modifier = Modifier.horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        listOf("🔥 iPhone 15", "👟 Nike Air", "💻 MacBook M3").forEach { chip ->
                            Box(
                                modifier = Modifier
                                    .background(
                                        Color(0xFF262A34).copy(alpha = 0.7f),
                                        RoundedCornerShape(20.dp)
                                    )
                                    .border(1.dp, VgasBorder, RoundedCornerShape(20.dp))
                                    .padding(horizontal = 12.dp, vertical = 6.dp)
                            ) {
                                Text(chip, color = VgasText, fontSize = 12.sp)
                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Stats Ticker
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF0A0E17).copy(alpha = 0.8f))
                    .padding(vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem("10Cr+", "Products", VgasSecondary)
                StatItem("50+", "Stores", VgasTertiary)
                StatItem("80%", "Savings", VgasGold)
                StatItem("500K+", "Users", VgasPrimary)
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Categories
            Text("Categories", color = VgasText, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(12.dp))

            LazyVerticalGrid(
                columns = GridCells.Fixed(4),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.height(200.dp)
            ) {
                items(listOf(
                    "📱" to "Electronics",
                    "👕" to "Fashion",
                    "🏠" to "Home",
                    "💄" to "Beauty",
                    "⚽" to "Sports",
                    "📚" to "Books",
                    "🛒" to "Grocery",
                    "🎮" to "Toys"
                )) { (icon, name) ->
                    Column(
                        modifier = Modifier
                            .clip(RoundedCornerShape(12.dp))
                            .background(VgasCard)
                            .border(1.dp, VgasBorder, RoundedCornerShape(12.dp))
                            .padding(12.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(icon, fontSize = 24.sp)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(name, color = VgasText, fontSize = 10.sp, fontWeight = FontWeight.Medium)
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Loot Deals
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("🔥 Loot Deals", color = VgasText, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                Box(
                    modifier = Modifier
                        .background(VgasRed.copy(alpha = 0.2f), RoundedCornerShape(8.dp))
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text("LIVE", color = VgasRed, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Product Cards
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                ProductCard("iPhone 15 Pro Max", "₹1,34,990", "₹1,59,900", "Amazon", VgasRed)
                ProductCard("Samsung S24 Ultra", "₹1,29,999", "₹1,44,999", "Flipkart", VgasRed)
                ProductCard("Nike Air Jordan 1", "₹8,999", "₹14,995", "Myntra", VgasRed)
            }

            Spacer(modifier = Modifier.height(80.dp))
        }

        // Bottom Nav
        Box(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .background(VgasCard)
                .border(1.dp, VgasBorder)
                .padding(vertical = 12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                BottomNavItem("🏠", "Home", true)
                BottomNavItem("🔍", "Search", false)
                BottomNavItem("🔥", "Deals", false)
                BottomNavItem("🤖", "AI Chat", false)
                BottomNavItem("👤", "Profile", false)
            }
        }
    }
}

@Composable
fun StatItem(value: String, label: String, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, color = color, fontWeight = FontWeight.Bold, fontSize = 14.sp)
        Text(label, color = VgasTextMuted, fontSize = 10.sp)
    }
}

@Composable
fun ProductCard(title: String, price: String, originalPrice: String, store: String, discountColor: Color) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(VgasCard)
            .border(1.dp, VgasBorder, RoundedCornerShape(16.dp))
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(Color(0xFF1E293B)),
                contentAlignment = Alignment.Center
            ) {
                Text("📦", fontSize = 32.sp)
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(title, color = VgasText, fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
                Spacer(modifier = Modifier.height(4.dp))
                Row(verticalAlignment = Alignment.Baseline) {
                    Text(price, color = VgasTertiary, fontWeight = FontWeight.ExtraBold, fontSize = 18.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(originalPrice, color = VgasTextMuted, fontSize = 12.sp, fontWeight = FontWeight.Light)
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(store, color = VgasTextSecondary, fontSize = 12.sp)
            }
            Box(
                modifier = Modifier
                    .background(discountColor.copy(alpha = 0.15f), RoundedCornerShape(8.dp))
                    .border(1.dp, discountColor.copy(alpha = 0.35f), RoundedCornerShape(8.dp))
                    .padding(horizontal = 8.dp, vertical = 4.dp)
            ) {
                Text("-16%", color = discountColor, fontSize = 11.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun BottomNavItem(icon: String, label: String, active: Boolean) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.padding(horizontal = 8.dp)
    ) {
        Text(icon, fontSize = 20.sp)
        Spacer(modifier = Modifier.height(2.dp))
        Text(
            label,
            color = if (active) VgasSecondary else VgasTextMuted,
            fontSize = 10.sp,
            fontWeight = if (active) FontWeight.Bold else FontWeight.Normal
        )
    }
}
