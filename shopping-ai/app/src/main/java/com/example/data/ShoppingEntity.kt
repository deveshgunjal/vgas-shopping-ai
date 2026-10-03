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
  val fakeReason: String,
  val storeName: String, // e.g., "Amazon India", "Flipkart", "Myntra"
  val affiliateUrl: String,
  val category: String, // "Electronics", "Fashion", "Home", "Kitchen", "Hardware", "Gadgets"
  val priceHistoryJson: String, // Comma separated prices e.g. "22990,22990,34990,24990"
  val addedTimestamp: Long = System.currentTimeMillis(),
  val reviewScore: Float = 4.5f,
  val reviewCount: Int = 1250,
  val qualityScore: Int = 92,
  val functionalityScore: Int = 90,
  val isRefurbished: Boolean = false,
  val isWholesale: Boolean = false,
  val isLootDeal: Boolean = false,
  val discountPercent: Int = ((originalPrice - currentPrice) * 100 / (if (originalPrice > 0) originalPrice else 1)).coerceIn(0, 95),
  val sellerName: String = "Verified Retailer",
  val couponCode: String = "LOOT500",
  val cashbackCoins: Int = (currentPrice / 100).coerceAtLeast(50)
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
