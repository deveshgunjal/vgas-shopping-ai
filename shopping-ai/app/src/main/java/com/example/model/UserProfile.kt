package com.example.model

data class UserProfile(
  val uid: String,
  val email: String? = null,
  val displayName: String? = null,
  val isAnonymous: Boolean = false,
  val isEmailVerified: Boolean = false,
  val provider: String = "Email / Password"
)
