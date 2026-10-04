package com.example.ui

import android.widget.Toast
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.MonetizationOn
import androidx.compose.material.icons.filled.Public
import androidx.compose.material.icons.filled.Storefront
import androidx.compose.material.icons.filled.VerifiedUser
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.model.Translations
import com.example.ui.components.AiChatModal
import com.example.ui.components.ComparisonModal
import com.example.ui.components.InteractivePriceChartModal
import com.example.ui.components.PaymentModal
import com.example.ui.screens.AuthScreen
import com.example.ui.screens.HomeScreen
import com.example.ui.screens.MonetizationScreen
import com.example.ui.screens.ProductDetailScreen
import com.example.ui.screens.ScraperScreen
import com.example.ui.screens.WhatsAppBotScreen
import com.example.ui.theme.CyberSurface
import com.example.ui.theme.NeonCyan
import com.example.viewmodel.ShoppingViewModel

@Composable
fun MainScreen(viewModel: ShoppingViewModel) {
  val uiState by viewModel.uiState.collectAsStateWithLifecycle()
  val strings = Translations.get(uiState.selectedLanguage)
  val context = LocalContext.current
  var currentTabIndex by remember { mutableIntStateOf(0) }
  var isAiChatOpen by remember { mutableStateOf(false) }
  var isCompareOpen by remember { mutableStateOf(false) }

  Scaffold(
    modifier = Modifier.fillMaxSize(),
    bottomBar = {
      NavigationBar(
        containerColor = CyberSurface,
        contentColor = Color.White
      ) {
        NavigationBarItem(
          selected = currentTabIndex == 0,
          onClick = { currentTabIndex = 0 },
          icon = { Icon(Icons.Default.Storefront, contentDescription = null) },
          label = { Text(strings.dashboardTab, fontSize = 11.sp, fontWeight = if (currentTabIndex == 0) FontWeight.Bold else FontWeight.Normal) },
          colors = NavigationBarItemDefaults.colors(
            selectedIconColor = Color.Black,
            selectedTextColor = NeonCyan,
            indicatorColor = NeonCyan,
            unselectedIconColor = Color(0xFF94A3B8),
            unselectedTextColor = Color(0xFF94A3B8)
          )
        )
        NavigationBarItem(
          selected = currentTabIndex == 1,
          onClick = { currentTabIndex = 1 },
          icon = { Icon(Icons.Default.Public, contentDescription = null) },
          label = { Text(strings.scraperTab, fontSize = 11.sp, fontWeight = if (currentTabIndex == 1) FontWeight.Bold else FontWeight.Normal) },
          colors = NavigationBarItemDefaults.colors(
            selectedIconColor = Color.Black,
            selectedTextColor = NeonCyan,
            indicatorColor = NeonCyan,
            unselectedIconColor = Color(0xFF94A3B8),
            unselectedTextColor = Color(0xFF94A3B8)
          )
        )
        NavigationBarItem(
          selected = currentTabIndex == 2,
          onClick = { currentTabIndex = 2 },
          icon = { Icon(Icons.Default.Chat, contentDescription = null) },
          label = { Text(strings.whatsappTab, fontSize = 11.sp, fontWeight = if (currentTabIndex == 2) FontWeight.Bold else FontWeight.Normal) },
          colors = NavigationBarItemDefaults.colors(
            selectedIconColor = Color.Black,
            selectedTextColor = NeonCyan,
            indicatorColor = NeonCyan,
            unselectedIconColor = Color(0xFF94A3B8),
            unselectedTextColor = Color(0xFF94A3B8)
          )
        )
        NavigationBarItem(
          selected = currentTabIndex == 3,
          onClick = { currentTabIndex = 3 },
          icon = { Icon(Icons.Default.MonetizationOn, contentDescription = null) },
          label = { Text(strings.monetizationTab, fontSize = 11.sp, fontWeight = if (currentTabIndex == 3) FontWeight.Bold else FontWeight.Normal) },
          colors = NavigationBarItemDefaults.colors(
            selectedIconColor = Color.Black,
            selectedTextColor = NeonCyan,
            indicatorColor = NeonCyan,
            unselectedIconColor = Color(0xFF94A3B8),
            unselectedTextColor = Color(0xFF94A3B8)
          )
        )
        NavigationBarItem(
          selected = currentTabIndex == 4,
          onClick = { currentTabIndex = 4 },
          icon = { Icon(Icons.Default.VerifiedUser, contentDescription = null) },
          label = { Text(strings.authTab, fontSize = 11.sp, fontWeight = if (currentTabIndex == 4) FontWeight.Bold else FontWeight.Normal) },
          colors = NavigationBarItemDefaults.colors(
            selectedIconColor = Color.Black,
            selectedTextColor = NeonCyan,
            indicatorColor = NeonCyan,
            unselectedIconColor = Color(0xFF94A3B8),
            unselectedTextColor = Color(0xFF94A3B8)
          )
        )
      }
    }
  ) { innerPadding ->
    Box(
      modifier = Modifier
        .fillMaxSize()
        .padding(innerPadding)
    ) {
      when (currentTabIndex) {
        0 -> HomeScreen(
          uiState = uiState,
          strings = strings,
          onLanguageSelected = { viewModel.setLanguage(it) },
          onCategorySelected = { viewModel.setCategoryFilter(it) },
          onSearchQueryChanged = { viewModel.setSearchQuery(it) },
          onUrlInputChanged = { viewModel.setScraperUrlInput(it) },
          onAnalyzeClick = { viewModel.analyzeAndScrapeUrl(it) },
          onViewChartClick = { viewModel.selectProductForChart(it) },
          onOpenDetail = { viewModel.openProductDetail(it) },
          onShareWhatsAppClick = { product ->
            Toast.makeText(context, "🟢 WhatsApp Alert queued for ${product.title}!", Toast.LENGTH_SHORT).show()
            currentTabIndex = 2 // Switch to WhatsApp bot tab
          },
          onDeleteClick = { viewModel.deleteProduct(it) },
          onBotClick = { currentTabIndex = 2 },
          onNavigateToScraper = { currentTabIndex = 1 },
          onNavigateToAuth = { currentTabIndex = 4 },
          onSortSelected = { viewModel.setSortBy(it) },
          onToggleCompare = { viewModel.toggleCompareProduct(it) },
          onBuyClick = { viewModel.openPaymentModal(it) },
          onNavigateToCompare = { isCompareOpen = true },
          onNavigateToChat = { isAiChatOpen = true }
        )
        1 -> ScraperScreen(
          strings = strings,
          isScraping = uiState.isScraping,
          urlInput = uiState.scraperUrlInput,
          scraperSteps = uiState.scraperSteps,
          onUrlInputChanged = { viewModel.setScraperUrlInput(it) },
          onStartScrape = { viewModel.analyzeAndScrapeUrl(it) }
        )
        2 -> WhatsAppBotScreen(
          strings = strings,
          isBotOnline = uiState.isBotOnline,
          autoBroadcast = uiState.autoBroadcastEnabled,
          autoConvert = uiState.autoConvertAffiliate,
          logs = uiState.whatsappLogs,
          onToggleBot = { viewModel.toggleBotStatus() },
          onToggleBroadcast = { viewModel.toggleAutoBroadcast(it) },
          onToggleConvert = { viewModel.toggleAutoConvert(it) }
        )
        3 -> MonetizationScreen(
          strings = strings,
          selectedLang = uiState.selectedLanguage,
          totalCommission = uiState.totalCommissionEarned,
          clicksCount = uiState.affiliateClicksCount,
          conversionRate = uiState.conversionRatePercent,
          onLanguageSelected = { viewModel.setLanguage(it) }
        )
        4 -> AuthScreen(
          strings = strings,
          currentUser = uiState.currentUser,
          isAuthLoading = uiState.isAuthLoading,
          errorMessage = uiState.authErrorMessage,
          successMessage = uiState.authSuccessMessage,
          isFirebaseInitialized = uiState.isFirebaseInitialized,
          onSignIn = { email, pass -> viewModel.signInWithEmail(email, pass) },
          onSignUp = { email, pass -> viewModel.signUpWithEmail(email, pass) },
          onAnonymousSignIn = { viewModel.signInAnonymously() },
          onForgotPassword = { email -> viewModel.sendPasswordReset(email) },
          onSignOut = { viewModel.signOut() },
          onClearMessages = { viewModel.clearAuthMessages() }
        )
      }
    }

    // Modal Price Chart
    val chartProduct = uiState.selectedProductForChart
    if (chartProduct != null) {
      Dialog(
        onDismissRequest = { viewModel.selectProductForChart(null) },
        properties = DialogProperties(usePlatformDefaultWidth = false)
      ) {
        InteractivePriceChartModal(
          product = chartProduct,
          strings = strings,
          onClose = { viewModel.selectProductForChart(null) },
          onSendWhatsApp = {
            viewModel.selectProductForChart(null)
            Toast.makeText(context, "🟢 WhatsApp Alert queued for ${chartProduct.title}!", Toast.LENGTH_SHORT).show()
            currentTabIndex = 2
          },
          onCopyAffiliate = {
            Toast.makeText(context, "✨ Affiliate link copied to clipboard!", Toast.LENGTH_SHORT).show()
          }
        )
      }
    }

    // AI Chat & Review Modal
    if (isAiChatOpen) {
      Dialog(
        onDismissRequest = { isAiChatOpen = false },
        properties = DialogProperties(usePlatformDefaultWidth = false)
      ) {
        AiChatModal(
          messages = uiState.chatMessages,
          onSendMessage = { viewModel.sendAiChatMessage(it) },
          onClose = { isAiChatOpen = false }
        )
      }
    }

    // Product Comparison Modal
    if (isCompareOpen) {
      val compareList = uiState.products.filter { uiState.compareProductIds.contains(it.id) }
      Dialog(
        onDismissRequest = { isCompareOpen = false },
        properties = DialogProperties(usePlatformDefaultWidth = false)
      ) {
        ComparisonModal(
          products = compareList,
          onClose = { isCompareOpen = false },
          onBuyClick = {
            isCompareOpen = false
            viewModel.openPaymentModal(it)
          },
          onRemoveProduct = { viewModel.toggleCompareProduct(it) }
        )
      }
    }

    // Product Detail — shows only what the backend actually scraped
    val detailProduct = uiState.selectedProductForDetail
    if (detailProduct != null) {
      Dialog(
        onDismissRequest = { viewModel.closeProductDetail() },
        properties = DialogProperties(usePlatformDefaultWidth = false)
      ) {
        ProductDetailScreen(product = detailProduct)
      }
    }

    // Payment Modal
    val payProduct = uiState.selectedProductForPayment
    if (uiState.isPaymentModalOpen && payProduct != null) {
      Dialog(
        onDismissRequest = { viewModel.closePaymentModal() },
        properties = DialogProperties(usePlatformDefaultWidth = false)
      ) {
        PaymentModal(
          product = payProduct,
          successMessage = uiState.paymentSuccessMessage,
          onProcessPayment = { method, details -> viewModel.processPayment(method, details) },
          onClearSuccess = { viewModel.clearPaymentMessage() },
          onClose = { viewModel.closePaymentModal() }
        )
      }
    }
  }
}
