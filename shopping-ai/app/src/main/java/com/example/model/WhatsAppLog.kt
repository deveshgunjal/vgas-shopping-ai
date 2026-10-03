package com.example.model

data class WhatsAppLog(
  val id: String,
  val timestamp: String,
  val productTitle: String,
  val priceDropText: String,
  val recipientCount: Int,
  val isFakeWarning: Boolean,
  val status: String = "DELIVERED"
)

data class ScraperLogStep(
  val stepName: String,
  val status: String, // "PENDING", "ACTIVE", "COMPLETED", "CACHED"
  val detail: String
)
