package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.TrackedProduct
import com.example.model.AppLanguage
import com.example.model.LocalizedStrings
import com.example.viewmodel.ShoppingUiState

// VGAS.AI Design Tokens (shared across the screens package)
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

/**
 * HomeScreen — renders live state from [ShoppingViewModel].
 *
 * Everything shown here comes from data the backend actually returned for URLs
 * the user scraped. There is no built-in product list, no "10 Crore+ products"
 * marketing counter, and no trending chips with invented names. When the product
 * list is empty the screen says so instead of filling the gap.
 */
@Composable
fun HomeScreen(
    uiState: ShoppingUiState,
    strings: LocalizedStrings,
    onLanguageSelected: (AppLanguage) -> Unit,
    onCategorySelected: (String) -> Unit,
    onSearchQueryChanged: (String) -> Unit,
    onUrlInputChanged: (String) -> Unit,
    onAnalyzeClick: (String) -> Unit,
    onViewChartClick: (TrackedProduct) -> Unit,
    onOpenDetail: (TrackedProduct) -> Unit,
    onShareWhatsAppClick: (TrackedProduct) -> Unit,
    onDeleteClick: (Int) -> Unit,
    onBotClick: () -> Unit,
    onNavigateToScraper: () -> Unit,
    onNavigateToAuth: () -> Unit,
    onSortSelected: (String) -> Unit,
    onToggleCompare: (Int) -> Unit,
    onBuyClick: (TrackedProduct) -> Unit,
    onNavigateToCompare: () -> Unit,
    onNavigateToChat: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(VgasBackground)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            // ---- Top bar -------------------------------------------------
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
                            .background(Brush.linearGradient(listOf(VgasPrimary, Color(0xFF4F46E5)))),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("V", color = Color.White, fontWeight = FontWeight.ExtraBold, fontSize = 18.sp)
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(strings.appTitle, color = VgasText, fontWeight = FontWeight.ExtraBold, fontSize = 20.sp)
                }

                // Language switcher — driven by real state, not a fake flag.
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
                            .background(if (uiState.isBotOnline) VgasTertiary else VgasTextMuted)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    AppLanguage.entries.forEach { lang ->
                        Text(
                            lang.code,
                            color = if (lang == uiState.selectedLanguage) VgasSecondary else VgasTextMuted,
                            fontSize = 10.sp,
                            fontWeight = if (lang == uiState.selectedLanguage) FontWeight.Bold else FontWeight.Normal,
                            modifier = Modifier
                                .clickable { onLanguageSelected(lang) }
                                .padding(horizontal = 4.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // ---- Hero ----------------------------------------------------
            Text(
                strings.appTitle,
                color = VgasText,
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                "Paste a product URL and the backend scrapes the live price.",
                color = VgasTextSecondary,
                fontSize = 13.sp
            )

            Spacer(modifier = Modifier.height(16.dp))

            // URL input -> real scrape
            OutlinedTextField(
                value = uiState.scraperUrlInput,
                onValueChange = onUrlInputChanged,
                label = { Text(strings.pasteUrlHint, fontSize = 12.sp) },
                singleLine = true,
                isError = uiState.isScraping,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = VgasSecondary,
                    unfocusedBorderColor = VgasBorder,
                    focusedLabelColor = VgasSecondary,
                    unfocusedLabelColor = VgasTextMuted,
                    focusedTextColor = VgasText,
                    unfocusedTextColor = VgasText,
                    cursorColor = VgasSecondary
                ),
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(10.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(
                    onClick = { onAnalyzeClick(uiState.scraperUrlInput) },
                    enabled = !uiState.isScraping && uiState.scraperUrlInput.isNotBlank(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = VgasPrimary,
                        contentColor = Color.White,
                        disabledContainerColor = Color(0xFF262A34),
                        disabledContentColor = VgasTextMuted
                    ),
                    modifier = Modifier.weight(1f)
                ) {
                    Text(if (uiState.isScraping) "Scraping…" else strings.analyzeBtn, fontSize = 13.sp)
                }
                OutlinedButton(
                    onClick = onBotClick,
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = VgasSecondary),
                    modifier = Modifier.weight(1f)
                ) {
                    Text("WhatsApp Bot", fontSize = 13.sp)
                }
            }

            if (uiState.isScraping && uiState.scraperSteps.isNotEmpty()) {
                Spacer(modifier = Modifier.height(12.dp))
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(VgasCard)
                        .border(1.dp, VgasBorder, RoundedCornerShape(12.dp))
                        .padding(12.dp)
                ) {
                    uiState.scraperSteps.forEach { step ->
                        Text(
                            "${step.stepName} — ${step.status}",
                            color = when (step.status) {
                                "COMPLETED" -> VgasTertiary
                                "FAILED" -> VgasRed
                                else -> VgasTextSecondary
                            },
                            fontSize = 12.sp
                        )
                        if (step.detail.isNotBlank()) {
                            Text(step.detail, color = VgasTextMuted, fontSize = 11.sp)
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // ---- Real counters (from Room, i.e. from real scrapes) --------
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF0A0E17).copy(alpha = 0.8f))
                    .padding(vertical = 10.dp),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem(uiState.products.size.toString(), "Tracked", VgasSecondary)
                StatItem(uiState.alerts.size.toString(), "Alerts", VgasGold)
                StatItem(uiState.compareProductIds.size.toString(), "Compare", VgasPrimary)
                StatItem(strings.verifiedDeal, "Analysis", VgasTertiary)
            }

            Spacer(modifier = Modifier.height(20.dp))

            // ---- Filters + search (real state) ----------------------------
            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf(
                    "All" to "All",
                    "Real Only" to strings.filterRealOnly,
                    "Flagged Only" to strings.filterFakeOnly,
                    "Electronics" to strings.filterElectronics,
                    "Fashion" to strings.filterFashion,
                    "Home" to strings.filterHome
                ).forEach { (key, label) ->
                    val active = uiState.selectedCategory == key
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(20.dp))
                            .background(if (active) VgasPrimary.copy(alpha = 0.2f) else Color(0xFF262A34).copy(alpha = 0.7f))
                            .border(1.dp, if (active) VgasPrimary else VgasBorder, RoundedCornerShape(20.dp))
                            .clickable { onCategorySelected(key) }
                            .padding(horizontal = 14.dp, vertical = 7.dp)
                    ) {
                        Text(label, color = if (active) VgasPrimary else VgasText, fontSize = 12.sp)
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            OutlinedTextField(
                value = uiState.searchQuery,
                onValueChange = onSearchQueryChanged,
                placeholder = { Text("Filter tracked products", fontSize = 12.sp) },
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = VgasSecondary,
                    unfocusedBorderColor = VgasBorder,
                    focusedTextColor = VgasText,
                    unfocusedTextColor = VgasText,
                    cursorColor = VgasSecondary
                ),
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(10.dp))

            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf(
                    "LATEST" to "Latest",
                    "PRICE_LOW_HIGH" to "Price ↑",
                    "PRICE_HIGH_LOW" to "Price ↓",
                    "DISCOUNT_PERCENT" to "Discount",
                    "REVIEW_SCORE" to "Rating"
                ).forEach { (key, label) ->
                    val active = uiState.sortBy == key
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(8.dp))
                            .background(if (active) VgasSecondary.copy(alpha = 0.18f) else Color.Transparent)
                            .border(1.dp, if (active) VgasSecondary else VgasBorder, RoundedCornerShape(8.dp))
                            .clickable { onSortSelected(key) }
                            .padding(horizontal = 10.dp, vertical = 5.dp)
                    ) {
                        Text(label, color = if (active) VgasSecondary else VgasTextMuted, fontSize = 11.sp)
                    }
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // ---- Products ------------------------------------------------
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Tracked Products", color = VgasText, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                Text(
                    "${uiState.products.size} live",
                    color = VgasTextMuted,
                    fontSize = 12.sp
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            if (uiState.products.isEmpty()) {
                EmptyProductsState(
                    onNavigateToScraper = onNavigateToScraper,
                    onNavigateToAuth = onNavigateToAuth,
                    onNavigateToChat = onNavigateToChat
                )
            } else {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    uiState.products.forEach { product ->
                        LiveProductCard(
                            product = product,
                            isSelectedForCompare = uiState.compareProductIds.contains(product.id),
                            onViewChart = { onViewChartClick(product) },
                            onOpenDetail = { onOpenDetail(product) },
                            onShareWhatsApp = { onShareWhatsAppClick(product) },
                            onDelete = { onDeleteClick(product.id) },
                            onToggleCompare = { onToggleCompare(product.id) },
                            onBuy = { onBuyClick(product) }
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(80.dp))
        }
    }
}

@Composable
private fun EmptyProductsState(
    onNavigateToScraper: () -> Unit,
    onNavigateToAuth: () -> Unit,
    onNavigateToChat: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(VgasCard)
            .border(1.dp, VgasBorder, RoundedCornerShape(16.dp))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("📭", fontSize = 40.sp)
        Spacer(modifier = Modifier.height(10.dp))
        Text("No products tracked yet", color = VgasText, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            "This list only fills up when the backend successfully scrapes a real " +
                "product URL. No sample products are shown.",
            color = VgasTextMuted,
            fontSize = 13.sp,
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )
        Spacer(modifier = Modifier.height(16.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(
                onClick = onNavigateToScraper,
                colors = ButtonDefaults.outlinedButtonColors(contentColor = VgasSecondary)
            ) { Text("Scrape a URL", fontSize = 12.sp) }
            OutlinedButton(
                onClick = onNavigateToChat,
                colors = ButtonDefaults.outlinedButtonColors(contentColor = VgasPrimary)
            ) { Text("Ask AI", fontSize = 12.sp) }
            OutlinedButton(
                onClick = onNavigateToAuth,
                colors = ButtonDefaults.outlinedButtonColors(contentColor = VgasGold)
            ) { Text("Sign in", fontSize = 12.sp) }
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

/**
 * A card for one real scraped product. Missing backend fields render as an
 * explicit dash rather than an invented default.
 */
@Composable
fun LiveProductCard(
    product: TrackedProduct,
    isSelectedForCompare: Boolean,
    onViewChart: () -> Unit,
    onOpenDetail: () -> Unit,
    onShareWhatsApp: () -> Unit,
    onDelete: () -> Unit,
    onToggleCompare: () -> Unit,
    onBuy: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(VgasCard)
            .border(
                1.dp,
                if (isSelectedForCompare) VgasSecondary else VgasBorder,
                RoundedCornerShape(16.dp)
            )
            .padding(16.dp)
    ) {
        Text(
            product.title,
            color = VgasText,
            fontWeight = FontWeight.SemiBold,
            fontSize = 14.sp,
            modifier = Modifier.clickable { onOpenDetail() }
        )

        Spacer(modifier = Modifier.height(6.dp))

        Row(verticalAlignment = Alignment.CenterVertically) {
            if (product.currentPrice > 0) {
                Text(
                    "₹${product.currentPrice}",
                    color = VgasTertiary,
                    fontWeight = FontWeight.ExtraBold,
                    fontSize = 18.sp
                )
            } else {
                Text("price unavailable", color = VgasTextMuted, fontSize = 14.sp)
            }
            if (product.originalPrice > 0 && product.originalPrice != product.currentPrice) {
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    "₹${product.originalPrice}",
                    color = VgasTextMuted,
                    fontSize = 12.sp,
                    textDecoration = TextDecoration.LineThrough
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    "-${product.discountPercent}%",
                    color = if (product.discountPercent >= 70) VgasRed else VgasGold,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }

        Spacer(modifier = Modifier.height(6.dp))

        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(product.storeName, color = VgasTextSecondary, fontSize = 12.sp)
            if (product.reviewScore > 0f) {
                Spacer(modifier = Modifier.width(10.dp))
                Text("★ ${product.reviewScore}", color = VgasGold, fontSize = 11.sp)
            } else {
                Spacer(modifier = Modifier.width(10.dp))
                Text("no rating", color = VgasTextMuted, fontSize = 11.sp)
            }
        }

        if (product.isFakeDiscount) {
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                "⚠ ${strings_fakeReason(product)}",
                color = VgasRed,
                fontSize = 11.sp
            )
        }

        Spacer(modifier = Modifier.height(12.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            SmallAction("Chart", VgasSecondary, onViewChart, Modifier.weight(1f))
            SmallAction("WhatsApp", VgasTertiary, onShareWhatsApp, Modifier.weight(1f))
            SmallAction(
                if (isSelectedForCompare) "Added" else "Compare",
                if (isSelectedForCompare) VgasSecondary else VgasPrimary,
                onToggleCompare,
                Modifier.weight(1f)
            )
            SmallAction("Buy", VgasGold, onBuy, Modifier.weight(1f))
            SmallAction("Delete", VgasRed, onDelete, Modifier.weight(1f))
        }
    }
}

private fun strings_fakeReason(product: TrackedProduct): String =
    if (product.fakeReason.isBlank()) "fake discount flagged by backend" else product.fakeReason

@Composable
private fun SmallAction(label: String, color: Color, onClick: () -> Unit, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(color.copy(alpha = 0.15f))
            .border(1.dp, color.copy(alpha = 0.35f), RoundedCornerShape(8.dp))
            .clickable { onClick() }
            .padding(vertical = 7.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(label, color = color, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
    }
}