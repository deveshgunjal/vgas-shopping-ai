package com.example.ui.components

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.SmartToy
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
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
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.R
import com.example.model.AiChatMessage
import com.example.ui.theme.CyberBorder
import com.example.ui.theme.CyberSurface
import com.example.ui.theme.NeonCyan
import com.example.ui.theme.NeonEmerald

@Composable
fun AiChatModal(
  messages: List<AiChatMessage>,
  onSendMessage: (String) -> Unit,
  onClose: () -> Unit
) {
  var input by remember { mutableStateOf("") }

  Surface(
    modifier = Modifier
      .fillMaxWidth()
      .height(600.dp),
    color = Color(0xFF0F172A),
    shape = RoundedCornerShape(20.dp),
    border = androidx.compose.foundation.BorderStroke(2.dp, NeonCyan)
  ) {
    Column(modifier = Modifier.fillMaxSize()) {
      // Header Bar
      Surface(
        modifier = Modifier.fillMaxWidth(),
        color = Color(0xFF1E293B)
      ) {
        Row(
          modifier = Modifier.padding(16.dp),
          verticalAlignment = Alignment.CenterVertically,
          horizontalArrangement = Arrangement.SpaceBetween
        ) {
          Row(verticalAlignment = Alignment.CenterVertically) {
            Surface(
              modifier = Modifier.size(40.dp),
              shape = RoundedCornerShape(8.dp),
              color = Color(0xFF0F172A),
              border = androidx.compose.foundation.BorderStroke(1.dp, NeonCyan)
            ) {
              Image(
                painter = painterResource(id = R.drawable.vgas_app_logo_1785237044971),
                contentDescription = null,
                modifier = Modifier.fillMaxSize()
              )
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column {
              Text("VGAS AI Shopping Assistant", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = NeonCyan)
              Text("VGAS • मराठी • हिंदी • தமிழ் • తెలుగు • বাংলা • English (All India Languages)", style = MaterialTheme.typography.bodySmall, color = Color(0xFFD8B4FE))
              Text("AI-Powered Shopping Assistant", style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp), color = NeonEmerald)
            }
          }
          IconButton(onClick = onClose) {
            Icon(Icons.Default.Close, contentDescription = "Close", tint = Color.White)
          }
        }
      }

      // Feature Highlights Banner
      Surface(
        modifier = Modifier.fillMaxWidth(),
        color = NeonEmerald.copy(alpha = 0.15f)
      ) {
        Text(
          text = "✨ विचारा: रिव्ह्यू (Reviews), 80-90% लूट डील्स, होलसेल दर (Wholesale), किंवा रिफर्बिश्ड गॅजेट्सबद्दल!",
          style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
          color = NeonEmerald,
          modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
        )
      }

      // Messages List
      LazyColumn(
        modifier = Modifier
          .weight(1f)
          .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
      ) {
        items(messages, key = { it.id }) { msg ->
          val isUser = msg.sender == "USER"
          Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
          ) {
            if (!isUser) {
              Surface(
                shape = CircleShape,
                color = NeonCyan.copy(alpha = 0.2f),
                modifier = Modifier.size(32.dp)
              ) {
                Box(contentAlignment = Alignment.Center) {
                  Icon(Icons.Default.SmartToy, contentDescription = null, tint = NeonCyan, modifier = Modifier.size(18.dp))
                }
              }
              Spacer(modifier = Modifier.width(8.dp))
            }

            Card(
              colors = CardDefaults.cardColors(
                containerColor = if (isUser) Color(0xFF3B82F6) else Color(0xFF1E293B)
              ),
              shape = RoundedCornerShape(
                topStart = 16.dp,
                topEnd = 16.dp,
                bottomStart = if (isUser) 16.dp else 4.dp,
                bottomEnd = if (isUser) 4.dp else 16.dp
              ),
              modifier = Modifier.fillMaxWidth(0.85f)
            ) {
              Column(modifier = Modifier.padding(12.dp)) {
                Text(
                  text = msg.message,
                  style = MaterialTheme.typography.bodyMedium.copy(lineHeight = 20.sp),
                  color = Color.White
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                  text = msg.timestamp,
                  style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp),
                  color = if (isUser) Color(0xFFDBEAFE) else Color(0xFF64748B),
                  modifier = Modifier.align(Alignment.End)
                )
              }
            }
          }
        }
      }

      // Input Bottom Bar
      Surface(
        modifier = Modifier.fillMaxWidth(),
        color = Color(0xFF1E293B)
      ) {
        Row(
          modifier = Modifier.padding(12.dp),
          verticalAlignment = Alignment.CenterVertically
        ) {
          OutlinedTextField(
            value = input,
            onValueChange = { input = it },
            placeholder = { Text("मराठीत किंवा इंग्रजीत प्रश्न विचारा...", color = Color(0xFF64748B)) },
            modifier = Modifier.weight(1f),
            singleLine = true,
            colors = OutlinedTextFieldDefaults.colors(
              focusedBorderColor = NeonCyan,
              unfocusedBorderColor = CyberBorder,
              focusedTextColor = Color.White,
              unfocusedTextColor = Color.White
            ),
            shape = RoundedCornerShape(12.dp)
          )
          Spacer(modifier = Modifier.width(8.dp))
          Button(
            onClick = {
              if (input.isNotBlank()) {
                onSendMessage(input)
                input = ""
              }
            },
            colors = ButtonDefaults.buttonColors(containerColor = NeonCyan, contentColor = Color.Black),
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier.height(54.dp)
          ) {
            Icon(Icons.Default.Send, contentDescription = "Send")
          }
        }
      }
    }
  }
}
