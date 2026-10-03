package com.example.model

data class AiChatMessage(
  val id: String,
  val sender: String, // "USER" or "AI_ASSISTANT"
  val message: String,
  val timestamp: String,
  val relatedProductTitle: String? = null
)
