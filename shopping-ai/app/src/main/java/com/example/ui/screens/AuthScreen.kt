package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.CloudDone
import androidx.compose.material.icons.filled.CloudOff
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.VerifiedUser
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Divider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.LocalizedStrings
import com.example.model.UserProfile
import com.example.ui.theme.AlertOrange
import com.example.ui.theme.CyberBorder
import com.example.ui.theme.CyberSurface
import com.example.ui.theme.NeonCyan
import com.example.ui.theme.NeonEmerald
import com.example.ui.theme.ScamRed

@Composable
fun AuthScreen(
  strings: LocalizedStrings,
  currentUser: UserProfile?,
  isAuthLoading: Boolean,
  errorMessage: String?,
  successMessage: String?,
  isFirebaseInitialized: Boolean,
  onSignIn: (String, String) -> Unit,
  onSignUp: (String, String) -> Unit,
  onAnonymousSignIn: () -> Unit,
  onForgotPassword: (String) -> Unit,
  onSignOut: () -> Unit,
  onClearMessages: () -> Unit,
  modifier: Modifier = Modifier
) {
  var isSignUpMode by remember { mutableStateOf(false) }
  var emailInput by remember { mutableStateOf("") }
  var passwordInput by remember { mutableStateOf("") }

  LazyColumn(
    modifier = modifier.fillMaxSize(),
    contentPadding = PaddingValues(16.dp),
    verticalArrangement = Arrangement.spacedBy(16.dp)
  ) {
    // Header & Firebase Connection Status Banner
    item {
      Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = CyberSurface),
        border = androidx.compose.foundation.BorderStroke(1.dp, NeonCyan)
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
              imageVector = if (isFirebaseInitialized) Icons.Default.CloudDone else Icons.Default.CloudOff,
              contentDescription = null,
              tint = if (isFirebaseInitialized) NeonEmerald else AlertOrange,
              modifier = Modifier.size(26.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
              text = strings.authTitle,
              style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
              color = Color.White
            )
          }
          Spacer(modifier = Modifier.height(6.dp))
          Text(
            text = strings.authSubtitle,
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFF94A3B8)
          )
          Spacer(modifier = Modifier.height(12.dp))
          Surface(
            color = if (isFirebaseInitialized) NeonEmerald.copy(alpha = 0.15f) else AlertOrange.copy(alpha = 0.15f),
            shape = RoundedCornerShape(8.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, if (isFirebaseInitialized) NeonEmerald else AlertOrange)
          ) {
            Text(
              text = if (isFirebaseInitialized)
                "🟢 Live Firebase SDK: Connected to Firebase Cloud Project"
              else
                "⚠️ Firebase auth is not configured. Add google-services.json to enable real live authentication.",
              style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
              color = if (isFirebaseInitialized) NeonEmerald else Color(0xFFFFCC80),
              modifier = Modifier.padding(10.dp).fillMaxWidth()
            )
          }
        }
      }
    }

    // Success / Error Feedback Banners
    if (errorMessage != null || successMessage != null) {
      item {
        Card(
          modifier = Modifier.fillMaxWidth(),
          shape = RoundedCornerShape(12.dp),
          colors = CardDefaults.cardColors(containerColor = if (errorMessage != null) ScamRed.copy(alpha = 0.2f) else NeonEmerald.copy(alpha = 0.2f)),
          border = androidx.compose.foundation.BorderStroke(1.dp, if (errorMessage != null) ScamRed else NeonEmerald)
        ) {
          Row(
            modifier = Modifier
              .fillMaxWidth()
              .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
          ) {
            Text(
              text = errorMessage ?: successMessage ?: "",
              style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.SemiBold),
              color = if (errorMessage != null) Color(0xFFFF8A80) else Color(0xFFB9F6CA),
              modifier = Modifier.weight(1f)
            )
            IconButton(onClick = onClearMessages, modifier = Modifier.size(24.dp)) {
              Icon(Icons.Default.Close, contentDescription = "Close", tint = Color.White)
            }
          }
        }
      }
    }

    // Main Profile or Authentication Box
    if (currentUser != null) {
      // LOGGED IN USER VIEW
      item {
        Surface(
          modifier = Modifier.fillMaxWidth(),
          color = Color(0xFF131A2A),
          shape = RoundedCornerShape(16.dp),
          border = androidx.compose.foundation.BorderStroke(1.5.dp, NeonEmerald)
        ) {
          Column(
            modifier = Modifier.padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
          ) {
            Box(
              modifier = Modifier
                .size(84.dp)
                .background(Color(0xFF1E283F), CircleShape)
                .border(2.dp, NeonEmerald, CircleShape),
              contentAlignment = Alignment.Center
            ) {
              Icon(
                imageVector = Icons.Default.VerifiedUser,
                contentDescription = null,
                tint = NeonEmerald,
                modifier = Modifier.size(48.dp)
              )
            }
            Spacer(modifier = Modifier.height(14.dp))
            Text(
              text = currentUser.displayName ?: "Verified Shopper",
              style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold),
              color = Color.White
            )
            if (!currentUser.email.isNullOrBlank()) {
              Text(
                text = currentUser.email,
                style = MaterialTheme.typography.bodyMedium,
                color = Color(0xFF94A3B8)
              )
            }
            Spacer(modifier = Modifier.height(14.dp))

            // User Info Badges
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
              Surface(
                color = NeonCyan.copy(alpha = 0.15f),
                shape = RoundedCornerShape(6.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, NeonCyan)
              ) {
                Text(
                  text = "Provider: ${currentUser.provider}",
                  style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                  color = NeonCyan,
                  modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                )
              }
              Surface(
                color = if (currentUser.isEmailVerified || currentUser.isAnonymous) NeonEmerald.copy(alpha = 0.15f) else AlertOrange.copy(alpha = 0.15f),
                shape = RoundedCornerShape(6.dp)
              ) {
                Text(
                  text = if (currentUser.isAnonymous) "Guest Session" else if (currentUser.isEmailVerified) "Verified Email ✅" else "Unverified Email ⚠️",
                  style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                  color = if (currentUser.isEmailVerified || currentUser.isAnonymous) NeonEmerald else AlertOrange,
                  modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                )
              }
            }

            Spacer(modifier = Modifier.height(16.dp))
            Divider(color = CyberBorder)
            Spacer(modifier = Modifier.height(16.dp))

            Row(verticalAlignment = Alignment.CenterVertically) {
              Icon(Icons.Default.CloudDone, contentDescription = null, tint = NeonEmerald, modifier = Modifier.size(18.dp))
              Spacer(modifier = Modifier.width(6.dp))
              Text(
                text = "Cloud Sync Active: All price trackers & affiliate tags are encrypted and synced.",
                style = MaterialTheme.typography.labelSmall,
                color = Color(0xFFCBD5E1),
                textAlign = TextAlign.Center
              )
            }

            Spacer(modifier = Modifier.height(20.dp))
            Button(
              onClick = onSignOut,
              colors = ButtonDefaults.buttonColors(containerColor = ScamRed, contentColor = Color.White),
              shape = RoundedCornerShape(10.dp),
              modifier = Modifier.fillMaxWidth().height(50.dp)
            ) {
              Icon(Icons.Default.Logout, contentDescription = null)
              Spacer(modifier = Modifier.width(8.dp))
              Text(strings.signOutBtn, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold))
            }
          }
        }
      }
    } else {
      // LOGGED OUT / LOGIN FORM VIEW
      item {
        Surface(
          modifier = Modifier.fillMaxWidth(),
          color = Color(0xFF131A2A),
          shape = RoundedCornerShape(16.dp),
          border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder)
        ) {
          Column(modifier = Modifier.padding(20.dp)) {
            // Mode Switcher (Sign In vs Sign Up)
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
              Button(
                onClick = { isSignUpMode = false; onClearMessages() },
                colors = ButtonDefaults.buttonColors(
                  containerColor = if (!isSignUpMode) NeonCyan else Color(0xFF1E283F),
                  contentColor = if (!isSignUpMode) Color.Black else Color.White
                ),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier.weight(1f).height(46.dp)
              ) {
                Text(strings.signInBtn, style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
              }
              Button(
                onClick = { isSignUpMode = true; onClearMessages() },
                colors = ButtonDefaults.buttonColors(
                  containerColor = if (isSignUpMode) NeonCyan else Color(0xFF1E283F),
                  contentColor = if (isSignUpMode) Color.Black else Color.White
                ),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier.weight(1f).height(46.dp)
              ) {
                Text(strings.signUpBtn, style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
              }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Email Field
            Text(strings.emailLabel, style = MaterialTheme.typography.labelSmall, color = Color(0xFF94A3B8))
            Spacer(modifier = Modifier.height(6.dp))
            OutlinedTextField(
              value = emailInput,
              onValueChange = { emailInput = it },
              placeholder = { Text("user@example.com", color = Color(0xFF64748B)) },
              leadingIcon = { Icon(Icons.Default.Email, contentDescription = null, tint = NeonCyan) },
              modifier = Modifier.fillMaxWidth(),
              singleLine = true,
              keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
              colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = NeonCyan,
                unfocusedBorderColor = CyberBorder,
                focusedTextColor = Color.White,
                unfocusedTextColor = Color.White
              ),
              shape = RoundedCornerShape(10.dp)
            )

            Spacer(modifier = Modifier.height(14.dp))

            // Password Field
            Text(strings.passwordLabel, style = MaterialTheme.typography.labelSmall, color = Color(0xFF94A3B8))
            Spacer(modifier = Modifier.height(6.dp))
            OutlinedTextField(
              value = passwordInput,
              onValueChange = { passwordInput = it },
              placeholder = { Text("••••••••", color = Color(0xFF64748B)) },
              leadingIcon = { Icon(Icons.Default.Lock, contentDescription = null, tint = NeonCyan) },
              visualTransformation = PasswordVisualTransformation(),
              modifier = Modifier.fillMaxWidth(),
              singleLine = true,
              keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
              colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = NeonCyan,
                unfocusedBorderColor = CyberBorder,
                focusedTextColor = Color.White,
                unfocusedTextColor = Color.White
              ),
              shape = RoundedCornerShape(10.dp)
            )

            // Forgot Password Button (only in SignIn Mode)
            if (!isSignUpMode) {
              Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.CenterEnd) {
                TextButton(onClick = { if (emailInput.isNotBlank()) onForgotPassword(emailInput) else onForgotPassword("") }) {
                  Text(strings.forgotPasswordBtn, style = MaterialTheme.typography.labelSmall, color = Color(0xFFB388FF))
                }
              }
            } else {
              Spacer(modifier = Modifier.height(16.dp))
            }

            // Primary Auth Button
            Button(
              onClick = {
                if (isSignUpMode) {
                  onSignUp(emailInput, passwordInput)
                } else {
                  onSignIn(emailInput, passwordInput)
                }
              },
              enabled = !isAuthLoading && emailInput.isNotBlank() && passwordInput.isNotBlank(),
              colors = ButtonDefaults.buttonColors(containerColor = NeonEmerald, contentColor = Color.Black),
              shape = RoundedCornerShape(10.dp),
              modifier = Modifier.fillMaxWidth().height(52.dp)
            ) {
              if (isAuthLoading) {
                CircularProgressIndicator(modifier = Modifier.size(22.dp), color = Color.Black, strokeWidth = 2.5.dp)
              } else {
                Icon(if (isSignUpMode) Icons.Default.AccountCircle else Icons.Default.Security, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                  text = if (isSignUpMode) "Register Firebase Account" else "Sign In to Firebase Cloud",
                  style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold)
                )
              }
            }

            Spacer(modifier = Modifier.height(20.dp))
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
              Divider(modifier = Modifier.weight(1f), color = CyberBorder)
              Text(" OR CONTINUE WITH ", style = MaterialTheme.typography.labelSmall, color = Color(0xFF64748B), modifier = Modifier.padding(horizontal = 8.dp))
              Divider(modifier = Modifier.weight(1f), color = CyberBorder)
            }
            Spacer(modifier = Modifier.height(16.dp))

            // Guest Anonymous Button
            OutlinedButton(
              onClick = onAnonymousSignIn,
              enabled = !isAuthLoading,
              shape = RoundedCornerShape(10.dp),
              border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder),
              modifier = Modifier.fillMaxWidth().height(48.dp)
            ) {
              Icon(Icons.Default.Person, contentDescription = null, tint = Color(0xFF94A3B8))
              Spacer(modifier = Modifier.width(8.dp))
              Text(strings.guestSignInBtn, style = MaterialTheme.typography.labelMedium, color = Color(0xFFCBD5E1))
            }
          }
        }
      }
    }
  }
}
