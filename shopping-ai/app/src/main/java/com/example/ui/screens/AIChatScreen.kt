package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun AIChatScreen() {
    var inputText by remember { mutableStateOf("") }
    val messages = remember {
        mutableStateListOf(
            ChatMessage("Hi! I'm VGAS AI Shopping Assistant. Ask me anything about products, prices, or deals!", false),
            ChatMessage("Find me the best iPhone 15 deal", true),
            ChatMessage("Best deal: iPhone 15 Pro Max on Amazon at ₹1,34,990 (save ₹24,910). Price expected to drop further in 5 days.", false)
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(VgasBackground)
    ) {
        // Header
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(VgasCard)
                .border(1.dp, VgasBorder)
                .padding(16.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("🤖", fontSize = 24.sp)
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text("VGAS AI Assistant", color = VgasText, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Text("Powered by OmniRoute", color = VgasTextMuted, fontSize = 12.sp)
                }
            }
        }

        // Messages
        LazyColumn(
            modifier = Modifier.weight(1f).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(messages) { msg ->
                ChatBubble(msg)
            }
        }

        // Quick Suggestions
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            listOf("iPhone 15 deals", "Best laptop under 50K", "Nike shoes").forEach { suggestion ->
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(20.dp))
                        .background(Color(0xFF262A34).copy(alpha = 0.7f))
                        .border(1.dp, VgasBorder, RoundedCornerShape(20.dp))
                        .padding(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Text(suggestion, color = VgasText, fontSize = 12.sp)
                }
            }
        }

        // Input
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(VgasCard)
                .border(1.dp, VgasBorder)
                .padding(16.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                TextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    placeholder = { Text("Ask about any product, price, or deal...", color = VgasTextMuted, fontSize = 14.sp) },
                    colors = TextFieldDefaults.colors(
                        focusedContainerColor = Color.Transparent,
                        unfocusedContainerColor = Color.Transparent,
                        focusedIndicatorColor = Color.Transparent,
                        unfocusedIndicatorColor = Color.Transparent,
                        focusedTextColor = VgasText,
                        unfocusedTextColor = VgasText,
                        cursorColor = VgasSecondary
                    ),
                    modifier = Modifier.weight(1f),
                    singleLine = true
                )
                Spacer(modifier = Modifier.width(8.dp))
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(VgasPrimary),
                    contentAlignment = Alignment.Center
                ) {
                    Text("➤", color = Color.White, fontSize = 16.sp)
                }
            }
        }
    }
}

@Composable
fun ChatBubble(message: ChatMessage) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (message.isUser) Arrangement.End else Arrangement.Start
    ) {
        Box(
            modifier = Modifier
                .widthIn(max = 280.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(
                    if (message.isUser) VgasPrimary
                    else Color(0xFF1E293B)
                )
                .border(
                    1.dp,
                    if (message.isUser) Color.Transparent else VgasBorder,
                    RoundedCornerShape(16.dp)
                )
                .padding(12.dp)
        ) {
            Text(message.text, color = VgasText, fontSize = 14.sp, lineHeight = 20.sp)
        }
    }
}

data class ChatMessage(val text: String, val isUser: Boolean)
