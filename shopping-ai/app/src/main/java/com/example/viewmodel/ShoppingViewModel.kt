package com.example.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.PriceAlert
import com.example.data.ShoppingDatabase
import com.example.data.ShoppingRepository
import com.example.data.TrackedProduct
import com.example.model.AiChatMessage
import com.example.model.AppLanguage
import com.example.model.ScraperLogStep
import com.example.model.UserProfile
import com.example.model.WhatsAppLog
import com.example.network.BackendClient
import com.google.firebase.FirebaseApp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseUser
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.random.Random

data class ShoppingUiState(
  val products: List<TrackedProduct> = emptyList(),
  val alerts: List<PriceAlert> = emptyList(),
  val selectedLanguage: AppLanguage = AppLanguage.ENGLISH,
  val selectedCategory: String = "All",
  val searchQuery: String = "",
  val selectedProductForChart: TrackedProduct? = null,
  val selectedProductForDetail: TrackedProduct? = null,
  // Starts offline. The app cannot claim the WhatsApp bot is online until it has
  // actually connected — defaulting to `true` shows a green "online" badge for a
  // bot that is not connected.
  val isBotOnline: Boolean = false,
  val autoBroadcastEnabled: Boolean = true,
  val autoConvertAffiliate: Boolean = true,
  val isScraping: Boolean = false,
  val scraperUrlInput: String = "",
  val scraperSteps: List<ScraperLogStep> = emptyList(),
  val whatsappLogs: List<WhatsAppLog> = emptyList(),
  // Money counters are 0 until a real backend figure is loaded. They must not
  // ship pre-filled (4850 / 1420 / 3.4% were invented) — a dashboard that shows
  // earnings nobody earned is the worst kind of fake.
  val totalCommissionEarned: Int = 0,
  val affiliateClicksCount: Int = 0,
  val conversionRatePercent: Float = 0f,

  val currentUser: UserProfile? = null,
  val isAuthLoading: Boolean = false,
  val authErrorMessage: String? = null,
  val authSuccessMessage: String? = null,
  val isFirebaseInitialized: Boolean = false,
  val sortBy: String = "LATEST",
  val compareProductIds: Set<Int> = emptySet(),
  val chatMessages: List<AiChatMessage> = emptyList(),
  val isPaymentModalOpen: Boolean = false,
  val selectedProductForPayment: TrackedProduct? = null,
  val paymentSuccessMessage: String? = null,
  // "unknown" rather than a marketing version string. Real version comes from
  // BuildConfig at runtime.
  val appVersion: String = "unknown"
)

class ShoppingViewModel(application: Application) : AndroidViewModel(application) {
  private val repository: ShoppingRepository
  private val _uiState = MutableStateFlow(ShoppingUiState())
  private var currentAiSessionId: String? = null

  val uiState: StateFlow<ShoppingUiState>

  init {
    val dao = ShoppingDatabase.getDatabase(application).shoppingDao()
    repository = ShoppingRepository(dao)

    uiState = combine(
      _uiState,
      repository.allProducts,
      repository.allAlerts
    ) { state, products, alerts ->
      val filteredProducts = products.filter { p ->
        val matchesCategory = when (state.selectedCategory) {
          "All" -> true
          "Real Only" -> !p.isFakeDiscount
          "Flagged Only" -> p.isFakeDiscount
          "🔥 80-90% Loot" -> p.isLootDeal || p.discountPercent >= 80
          "♻️ Refurbished" -> p.isRefurbished || p.title.contains("Refurbished", ignoreCase = true)
          "📦 Wholesale" -> p.isWholesale || p.title.contains("Wholesale", ignoreCase = true)
          else -> p.category.equals(state.selectedCategory, ignoreCase = true) || p.category.contains(state.selectedCategory, ignoreCase = true)
        }
        val matchesSearch = state.searchQuery.isBlank() ||
          p.title.contains(state.searchQuery, ignoreCase = true) ||
          p.storeName.contains(state.searchQuery, ignoreCase = true) ||
          p.category.contains(state.searchQuery, ignoreCase = true)
        matchesCategory && matchesSearch
      }
      val sortedProducts = when (state.sortBy) {
        "PRICE_LOW_HIGH" -> filteredProducts.sortedBy { it.currentPrice }
        "PRICE_HIGH_LOW" -> filteredProducts.sortedByDescending { it.currentPrice }
        "REVIEW_SCORE" -> filteredProducts.sortedByDescending { it.reviewScore }
        "QUALITY_SCORE" -> filteredProducts.sortedByDescending { it.qualityScore }
        "FUNCTIONALITY_SCORE" -> filteredProducts.sortedByDescending { it.functionalityScore }
        "DISCOUNT_PERCENT" -> filteredProducts.sortedByDescending { it.discountPercent }
        else -> filteredProducts.sortedByDescending { it.addedTimestamp }
      }
      state.copy(products = sortedProducts, alerts = alerts)
    }.stateIn(
      scope = viewModelScope,
      started = SharingStarted.WhileSubscribed(5000),
      initialValue = ShoppingUiState()
    )

    try {
      if (FirebaseApp.getApps(application).isNotEmpty()) {
        val auth = FirebaseAuth.getInstance()
        val current = auth.currentUser
        _uiState.update { it.copy(isFirebaseInitialized = true, currentUser = current?.let { u -> mapFirebaseUser(u) }) }
        auth.addAuthStateListener { firebaseAuth ->
          val usr = firebaseAuth.currentUser
          _uiState.update { it.copy(currentUser = usr?.let { u -> mapFirebaseUser(u) }) }
        }
      } else {
        _uiState.update { it.copy(isFirebaseInitialized = false) }
      }
    } catch (e: Exception) {
      _uiState.update { it.copy(isFirebaseInitialized = false) }
    }
  }

  fun setLanguage(lang: AppLanguage) {
    _uiState.update { it.copy(selectedLanguage = lang) }
  }

  private fun mapFirebaseUser(user: FirebaseUser): UserProfile {
    val provider = user.providerData.firstOrNull()?.providerId ?: "Firebase Auth"
    val providerName = when {
      provider.contains("google") -> "Google OAuth"
      user.isAnonymous -> "Anonymous Guest"
      else -> "Email / Password"
    }
    return UserProfile(
      uid = user.uid,
      email = user.email,
      displayName = user.displayName ?: user.email?.substringBefore("@")?.replaceFirstChar { it.uppercase() } ?: "Shopping AI User",
      isAnonymous = user.isAnonymous,
      isEmailVerified = user.isEmailVerified,
      provider = providerName
    )
  }

  fun signInWithEmail(email: String, pass: String) {
    if (email.isBlank() || pass.isBlank()) {
      _uiState.update { it.copy(authErrorMessage = "Please enter both email and password.") }
      return
    }
    _uiState.update { it.copy(isAuthLoading = true, authErrorMessage = null, authSuccessMessage = null) }
    if (_uiState.value.isFirebaseInitialized) {
      try {
        FirebaseAuth.getInstance().signInWithEmailAndPassword(email.trim(), pass)
          .addOnSuccessListener {
            _uiState.update { state -> state.copy(isAuthLoading = false, authSuccessMessage = "Successfully signed in to Firebase Cloud!") }
          }
          .addOnFailureListener { e ->
            _uiState.update { state -> state.copy(isAuthLoading = false, authErrorMessage = e.localizedMessage ?: "Authentication failed.") }
          }
      } catch (e: Exception) {
        _uiState.update { it.copy(isAuthLoading = false, authErrorMessage = e.localizedMessage ?: "Login error.") }
      }
    } else {
      _uiState.update { it.copy(isAuthLoading = false, authErrorMessage = "Firebase auth is not configured. Add google-services.json to enable live sign-in.") }
    }
  }

  fun signUpWithEmail(email: String, pass: String) {
    if (email.isBlank() || pass.length < 6) {
      _uiState.update { it.copy(authErrorMessage = "Email required and password must be at least 6 characters.") }
      return
    }
    _uiState.update { it.copy(isAuthLoading = true, authErrorMessage = null, authSuccessMessage = null) }
    if (_uiState.value.isFirebaseInitialized) {
      try {
        FirebaseAuth.getInstance().createUserWithEmailAndPassword(email.trim(), pass)
          .addOnSuccessListener {
            _uiState.update { state -> state.copy(isAuthLoading = false, authSuccessMessage = "Account created in Firebase Cloud!") }
          }
          .addOnFailureListener { e ->
            _uiState.update { state -> state.copy(isAuthLoading = false, authErrorMessage = e.localizedMessage ?: "Registration failed.") }
          }
      } catch (e: Exception) {
        _uiState.update { it.copy(isAuthLoading = false, authErrorMessage = e.localizedMessage ?: "Registration error.") }
      }
    } else {
      _uiState.update { it.copy(isAuthLoading = false, authErrorMessage = "Firebase auth registration is not configured. Add google-services.json to enable live auth.") }
    }
  }

  fun signInAnonymously() {
    _uiState.update { it.copy(isAuthLoading = true, authErrorMessage = null, authSuccessMessage = null) }
    if (_uiState.value.isFirebaseInitialized) {
      try {
        FirebaseAuth.getInstance().signInAnonymously()
          .addOnSuccessListener {
            _uiState.update { state -> state.copy(isAuthLoading = false, authSuccessMessage = "Signed in anonymously to Firebase Cloud!") }
          }
          .addOnFailureListener { e ->
            _uiState.update { state -> state.copy(isAuthLoading = false, authErrorMessage = e.localizedMessage ?: "Anonymous login failed.") }
          }
      } catch (e: Exception) {
        _uiState.update { it.copy(isAuthLoading = false, authErrorMessage = e.localizedMessage ?: "Login error.") }
      }
    } else {
      _uiState.update { it.copy(isAuthLoading = false, authErrorMessage = "Firebase authentication is not configured. Add google-services.json to enable real auth.") }
    }
  }

  fun sendPasswordReset(email: String) {
    if (email.isBlank()) {
      _uiState.update { it.copy(authErrorMessage = "Please enter your email address to reset password.") }
      return
    }
    if (_uiState.value.isFirebaseInitialized) {
      try {
        FirebaseAuth.getInstance().sendPasswordResetEmail(email.trim())
          .addOnSuccessListener {
            _uiState.update { state -> state.copy(authSuccessMessage = "Password reset email sent to $email!") }
          }
          .addOnFailureListener { e ->
            _uiState.update { state -> state.copy(authErrorMessage = e.localizedMessage ?: "Failed to send reset email.") }
          }
      } catch (e: Exception) {
        _uiState.update { it.copy(authErrorMessage = e.localizedMessage ?: "Reset error.") }
      }
    } else {
      _uiState.update { it.copy(authErrorMessage = "Firebase password reset is not configured. Add google-services.json to enable real email reset.") }
    }
  }

  fun signOut() {
    if (_uiState.value.isFirebaseInitialized) {
      try {
        FirebaseAuth.getInstance().signOut()
      } catch (e: Exception) {
        // ignore
      }
    }
    _uiState.update { it.copy(currentUser = null, authSuccessMessage = "Signed out successfully.", authErrorMessage = null) }
  }

  fun clearAuthMessages() {
    _uiState.update { it.copy(authErrorMessage = null, authSuccessMessage = null) }
  }

  fun setCategoryFilter(category: String) {
    _uiState.update { it.copy(selectedCategory = category) }
  }

  fun setSearchQuery(query: String) {
    _uiState.update { it.copy(searchQuery = query) }
  }

  fun selectProductForChart(product: TrackedProduct?) {
    _uiState.update { it.copy(selectedProductForChart = product) }
  }

  fun openProductDetail(product: TrackedProduct) {
    _uiState.update { it.copy(selectedProductForDetail = product) }
  }

  fun closeProductDetail() {
    _uiState.update { it.copy(selectedProductForDetail = null) }
  }

  fun setScraperUrlInput(url: String) {
    _uiState.update { it.copy(scraperUrlInput = url) }
  }

  fun toggleBotStatus() {
    _uiState.update { current ->
      current.copy(isBotOnline = !current.isBotOnline)
    }
  }

  fun toggleAutoBroadcast(enabled: Boolean) {
    _uiState.update { it.copy(autoBroadcastEnabled = enabled) }
  }

  fun toggleAutoConvert(enabled: Boolean) {
    _uiState.update { it.copy(autoConvertAffiliate = enabled) }
  }

  fun deleteProduct(id: Int) {
    viewModelScope.launch {
      repository.deleteProductById(id)
    }
  }

  fun analyzeAndScrapeUrl(urlInput: String) {
    if (urlInput.isBlank() || _uiState.value.isScraping) return

    viewModelScope.launch {
      _uiState.update {
        it.copy(
          isScraping = true,
          scraperSteps = listOf(
            ScraperLogStep("1. FastAPI Headless Browser", "ACTIVE", "Initializing Playwright & fetching DOM tree..."),
            ScraperLogStep("2. Redis Cache Lookup", "PENDING", "Waiting for DOM extraction..."),
            ScraperLogStep("3. AI Discount Verification", "PENDING", "Waiting for price history records..."),
            ScraperLogStep("4. Affiliate Converter", "PENDING", "Waiting for AI verification...")
          )
        )
      }

      val response = withContext(Dispatchers.IO) {
        BackendClient.fetchProductByUrl(urlInput)
      }

      if (response != null) {
        // Every field below is read straight from the backend response. Where a
        // field is missing it becomes an empty/zero value so the UI can say
        // "not reported" — a substituted default (4.5 stars, "Verified
        // Retailer", "LOOT500", a computed cashback) would be fabricated data
        // wearing the store's name.
        val productName = response.optString("name", "").ifBlank { "Unnamed product (scraper returned no title)" }
        val currentPrice = response.optInt("current_price", 0)
        val originalPrice = response.optInt("original_price", currentPrice)
        val lowestPrice = response.optInt("lowest_price", currentPrice).coerceAtMost(currentPrice)
        val isFake = response.optBoolean("is_fake_discount", false)
        val fakeReason = response.optString("fake_discount_reason", "")
        val affiliateUrl = response.optString("affiliate_url", "").ifBlank { urlInput }
        val storeName = response.optString("store", response.optString("store_domain", "")).ifBlank { "Unknown store" }
        val category = response.optString("category", "")
        // No history -> empty string. Fabricating "original,current" would draw
        // a price trend that never happened.
        val priceHistoryJson = response.optJSONArray("price_history")?.let { array ->
          List(array.length()) { idx -> array.optDouble(idx, 0.0).toInt().toString() }.joinToString(",")
        } ?: ""

        _uiState.update { state ->
          val newSteps = state.scraperSteps.mapIndexed { idx, step ->
            when (idx) {
              0 -> step.copy(status = "COMPLETED", detail = "DOM extracted. Product: $productName")
              1 -> step.copy(status = "COMPLETED", detail = "Backend responded with live product data.")
              2 -> step.copy(
                status = "COMPLETED",
                detail = when {
                  isFake -> "Suspicious discount flagged by backend analysis: ${fakeReason.ifBlank { "no reason supplied" }}"
                  else -> "Backend reported no fake-discount flag for this item."
                }
              )
              3 -> step.copy(
                status = if (affiliateUrl.isBlank()) "FAILED" else "COMPLETED",
                detail = if (affiliateUrl.isBlank()) "Backend returned no affiliate URL." else "Affiliate URL returned by backend."
              )
              else -> step
            }
          }
          state.copy(scraperSteps = newSteps)
        }

        repository.insertProduct(
          TrackedProduct(
            title = productName,
            url = urlInput,
            currentPrice = currentPrice,
            originalPrice = originalPrice,
            lowestRecordedPrice = lowestPrice,
            isFakeDiscount = isFake,
            fakeReason = fakeReason,
            storeName = storeName,
            affiliateUrl = affiliateUrl,
            category = category,
            priceHistoryJson = priceHistoryJson,
            reviewScore = if (response.has("rating")) response.optDouble("rating", 0.0).toFloat() else 0f,
            reviewCount = response.optInt("rating_count", 0),
            qualityScore = response.optInt("quality_score", 0),
            functionalityScore = response.optInt("functionality_score", 0),
            isLootDeal = response.optDouble("discount_percentage", 0.0) >= 70,
            sellerName = response.optString("seller_name", ""),
            couponCode = response.optString("coupon_code", ""),
            cashbackCoins = response.optInt("cashback_coins", 0)
          )
        )

        _uiState.update { state ->
          state.copy(isScraping = false, scraperUrlInput = "")
        }

        } else {
        _uiState.update { state ->
          val failedSteps = state.scraperSteps.mapIndexed { idx, step ->
            when (idx) {
              0 -> step.copy(status = "FAILED", detail = "Backend request failed. Real product scraping requires the backend service.")
              1 -> step.copy(status = "FAILED", detail = "Unable to fetch cached product data from backend.")
              2 -> step.copy(status = "FAILED", detail = "AI discount verification unavailable without backend response.")
              3 -> step.copy(status = "FAILED", detail = "Affiliate conversion unavailable without a valid product response.")
              else -> step
            }
          }
          state.copy(scraperSteps = failedSteps, isScraping = false)
        }
      }
    }
  }

  fun setSortBy(sortBy: String) {
    _uiState.update { it.copy(sortBy = sortBy) }
  }

  fun toggleCompareProduct(productId: Int) {
    _uiState.update { state ->
      val current = state.compareProductIds.toMutableSet()
      if (current.contains(productId)) {
        current.remove(productId)
      } else {
        if (current.size < 3) {
          current.add(productId)
        }
      }
      state.copy(compareProductIds = current)
    }
  }

  fun clearComparison() {
    _uiState.update { it.copy(compareProductIds = emptySet()) }
  }

  fun sendAiChatMessage(userMessage: String) {
    if (userMessage.isBlank()) return
    val timeStr = SimpleDateFormat("hh:mm a", Locale.getDefault()).format(Date())
    val userMsg = AiChatMessage(
      id = "CHAT-${Random.nextInt(10000, 99999)}",
      sender = "USER",
      message = userMessage,
      timestamp = timeStr
    )
    _uiState.update { it.copy(chatMessages = it.chatMessages + userMsg) }

    viewModelScope.launch {
      val response = withContext(Dispatchers.IO) {
        BackendClient.sendAiChatMessage(userMessage, currentAiSessionId, _uiState.value.selectedLanguage.code)
      }

      val aiReplyText = response?.optString("response") ?: "माफ करा, सध्या AI सेवा उपलब्ध नाही. कृपया नंतर प्रयत्न करा."
      currentAiSessionId = response?.optString("session_id") ?: currentAiSessionId
      val replyTimeStr = SimpleDateFormat("hh:mm a", Locale.getDefault()).format(Date())
      val aiReply = AiChatMessage(
        id = "CHAT-${Random.nextInt(10000, 99999)}",
        sender = "AI_ASSISTANT",
        message = aiReplyText,
        timestamp = replyTimeStr
      )
      _uiState.update { it.copy(chatMessages = it.chatMessages + aiReply) }
    }
  }

  fun openPaymentModal(product: TrackedProduct) {
    _uiState.update { it.copy(isPaymentModalOpen = true, selectedProductForPayment = product, paymentSuccessMessage = null) }
  }

  fun closePaymentModal() {
    _uiState.update { it.copy(isPaymentModalOpen = false, selectedProductForPayment = null) }
  }

  fun processPayment(method: String, details: String) {
    val msg = "No payment gateway is connected. Use Stripe checkout for real payments."
    _uiState.update { it.copy(paymentSuccessMessage = msg) }
  }

  fun clearPaymentMessage() {
    _uiState.update { it.copy(paymentSuccessMessage = null) }
  }
}
