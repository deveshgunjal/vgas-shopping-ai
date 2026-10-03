package com.example.ui.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.CreditCard
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Payments
import androidx.compose.material.icons.filled.Security
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.TrackedProduct
import com.example.ui.theme.CyberBorder
import com.example.ui.theme.CyberSurface
import com.example.ui.theme.NeonCyan
import com.example.ui.theme.NeonEmerald

@Composable
fun PaymentModal(
  product: TrackedProduct,
  successMessage: String?,
  onProcessPayment: (String, String) -> Unit,
  onClearSuccess: () -> Unit,
  onClose: () -> Unit
) {
  var selectedMethod by remember { mutableStateOf("UPI (GPay / PhonePe / Paytm)") }
  var upiOrCardInput by remember { mutableStateOf("user@okaxis") }
  var isProcessing by remember { mutableStateOf(false) }

  Surface(
    modifier = Modifier
      .fillMaxWidth()
      .height(580.dp),
    color = Color(0xFF0F172A),
    shape = RoundedCornerShape(20.dp),
    border = androidx.compose.foundation.BorderStroke(2.dp, NeonEmerald)
  ) {
    Column(modifier = Modifier.fillMaxSize()) {
      // Header
      Surface(modifier = Modifier.fillMaxWidth(), color = Color(0xFF064E3B)) {
        Row(
          modifier = Modifier.padding(16.dp),
          verticalAlignment = Alignment.CenterVertically,
          horizontalArrangement = Arrangement.SpaceBetween
        ) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Security, contentDescription = null, tint = NeonEmerald)
            Spacer(modifier = Modifier.width(10.dp))
            Column {
              Text("VGAS Safe Checkout & Payment", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = Color.White)
              Text("Vikas Gunjal Advance System • 256-Bit SSL Encrypted", style = MaterialTheme.typography.bodySmall, color = Color(0xFFA7F3D0))
            }
          }
          IconButton(onClick = onClose) {
            Icon(Icons.Default.Close, contentDescription = "Close", tint = Color.White)
          }
        }
      }

      if (successMessage != null) {
        Column(
          modifier = Modifier
            .weight(1f)
            .padding(24.dp),
          horizontalAlignment = Alignment.CenterHorizontally,
          verticalArrangement = Arrangement.Center
        ) {
          Icon(Icons.Default.CheckCircle, contentDescription = null, tint = NeonEmerald, modifier = Modifier.size(64.dp))
          Spacer(modifier = Modifier.height(16.dp))
          Text("पेमेंट यशस्वी! (Order Confirmed)", style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold), color = NeonEmerald)
          Spacer(modifier = Modifier.height(12.dp))
          Text(successMessage, style = MaterialTheme.typography.bodyMedium.copy(lineHeight = 22.sp), color = Color.White, modifier = Modifier.padding(horizontal = 16.dp))
          Spacer(modifier = Modifier.height(24.dp))
          Button(
            onClick = {
              onClearSuccess()
              onClose()
            },
            colors = ButtonDefaults.buttonColors(containerColor = NeonEmerald, contentColor = Color.Black),
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier.fillMaxWidth(0.7f).height(50.dp)
          ) {
            Text("Done / आर्डर पहा", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
          }
        }
      } else {
        Column(
          modifier = Modifier
            .weight(1f)
            .padding(20.dp),
          verticalArrangement = Arrangement.SpaceBetween
        ) {
          Column {
            Text("Order Summary:", style = MaterialTheme.typography.labelMedium, color = Color(0xFF94A3B8))
            Spacer(modifier = Modifier.height(6.dp))
            Surface(color = CyberSurface, shape = RoundedCornerShape(12.dp), border = androidx.compose.foundation.BorderStroke(1.dp, CyberBorder), modifier = Modifier.fillMaxWidth()) {
              Row(modifier = Modifier.padding(14.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Column(modifier = Modifier.weight(1f)) {
                  Text(product.title, style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold), color = Color.White)
                  Text("Seller: ${product.sellerName}", style = MaterialTheme.typography.bodySmall, color = Color(0xFF94A3B8))
                }
                Spacer(modifier = Modifier.width(12.dp))
                Text("₹${product.currentPrice}", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold), color = NeonEmerald)
              }
            }

            Spacer(modifier = Modifier.height(16.dp))
            Text("Select Payment Gateway System:", style = MaterialTheme.typography.labelMedium, color = Color(0xFF94A3B8))
            Spacer(modifier = Modifier.height(8.dp))

            val methods = listOf(
              "UPI (GPay / PhonePe / Paytm)" to Icons.Default.Payments,
              "Credit / Debit Card (Razorpay / Stripe)" to Icons.Default.CreditCard,
              "Cash on Delivery (COD)" to Icons.Default.Lock
            )

            methods.forEach { (methodName, icon) ->
              val isSelected = selectedMethod == methodName
              Surface(
                modifier = Modifier
                  .fillMaxWidth()
                  .padding(vertical = 4.dp)
                  .clickable { selectedMethod = methodName },
                color = if (isSelected) NeonEmerald.copy(alpha = 0.15f) else Color(0xFF1E293B),
                shape = RoundedCornerShape(12.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, if (isSelected) NeonEmerald else CyberBorder)
              ) {
                Row(modifier = Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                  Icon(icon, contentDescription = null, tint = if (isSelected) NeonEmerald else Color(0xFF94A3B8))
                  Spacer(modifier = Modifier.width(12.dp))
                  Text(methodName, style = MaterialTheme.typography.bodyMedium.copy(fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal), color = if (isSelected) Color.White else Color(0xFFE2E8F0))
                }
              }
            }

            Spacer(modifier = Modifier.height(14.dp))
            if (selectedMethod.contains("UPI")) {
              OutlinedTextField(
                value = upiOrCardInput,
                onValueChange = { upiOrCardInput = it },
                label = { Text("Enter UPI ID (VPA)", color = Color(0xFF94A3B8)) },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = NeonEmerald, unfocusedBorderColor = CyberBorder, focusedTextColor = Color.White, unfocusedTextColor = Color.White)
              )
            }
          }

          Button(
            onClick = {
              isProcessing = true
              onProcessPayment(selectedMethod, upiOrCardInput)
            },
            colors = ButtonDefaults.buttonColors(containerColor = NeonEmerald, contentColor = Color.Black),
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier.fillMaxWidth().height(54.dp),
            enabled = !isProcessing
          ) {
            Icon(Icons.Default.Security, contentDescription = null, modifier = Modifier.size(18.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text(if (isProcessing) "Processing Payment..." else "Pay ₹${product.currentPrice} Securely", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.ExtraBold))
          }
        }
      }
    }
  }
}
