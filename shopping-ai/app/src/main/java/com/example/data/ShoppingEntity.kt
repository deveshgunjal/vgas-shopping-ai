package com.example.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "tracked_products")
data class TrackedProduct(
  @PrimaryKey(autoGenerate = true) val id: Int = 0,
  val title: String,
  val url: String,
  val currentPrice: Int,
  val originalPrice: Int,
  val lowestRecordedPrice: Int,
  val isFakeDiscount: Boolean,
  // Empty string means "the backend did not report a reason". Never pre-filled
  // with "Verified genuine discount" — that would be a claim we cannot back.
  val fakeReason: String,
  val storeName: String, // e.g. "Amazon India", "Flipkart", "Myntra" — "" if unknown
  val affiliateUrl: String,
  val category: String, // "" if the scraper could not determine it
  val priceHistoryJson: String, // comma separated prices; "" when no history exists
  val addedTimestamp: Long = System.currentTimeMillis(),
  // Scores/counts default to 0 = "no data reported". They must never be seeded
  // with invented numbers (4.5 stars, 1250 reviews, 92 quality) because the UI
  // would then present fabricated facts as if the store had reported them.
  val reviewScore: Float = 0f,
  val reviewCount: Int = 0,
  val qualityScore: Int = 0,
  val functionalityScore: Int = 0,
  val isRefurbished: Boolean = false,
  val isWholesale: Boolean = false,
  val isLootDeal: Boolean = false,
  // Derived from the two real prices above, so this is arithmetic, not invention.
  val discountPercent: Int = ((originalPrice - currentPrice) * 100 / (if (originalPrice > 0) originalPrice else 1)).coerceIn(0, 95),
  // "" = the store did not name a seller. "Verified Retailer" would be a
  // trust claim this app has no way to substantiate.
  val sellerName: String = "",
  // "" = no coupon returned by the store. A made-up code like "LOOT500" would
  // send the user to a checkout that fails.
  val couponCode: String = "",
  // 0 = no cashback reported. Never computed locally: the app is not a bank
  // and has no payout ledger, so a locally invented figure is a lie.
  val cashbackCoins: Int = 0
)

@Entity(tableName = "price_alerts")
data class PriceAlert(
  @PrimaryKey(autoGenerate = true) val id: Int = 0,
  val productId: Int,
  val productTitle: String,
  val alertType: String, // "PRICE_DROP" or "FAKE_DISCOUNT_WARNING"
  val message: String,
  val timestamp: String,
  val isRead: Boolean = false
)
