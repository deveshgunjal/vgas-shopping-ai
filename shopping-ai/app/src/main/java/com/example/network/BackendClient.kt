package com.example.network

import com.example.BuildConfig
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.net.URLEncoder

object BackendClient {
  private val client = OkHttpClient()
  private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

  fun buildBaseUrl(): String {
    val configuredUrl = BuildConfig.BACKEND_BASE_URL.trim()
    if (configuredUrl.isNotEmpty()) {
      return configuredUrl
    }
    return "http://10.0.2.2:8000/api/v1"
  }

  fun fetchProductByUrl(productUrl: String): JSONObject? {
    val encodedUrl = URLEncoder.encode(productUrl, "UTF-8")
    val url = "${buildBaseUrl()}/products/by-url?url=$encodedUrl&use_cache=true"
    val request = Request.Builder()
      .url(url)
      .get()
      .build()

    client.newCall(request).execute().use { response ->
      if (!response.isSuccessful) {
        return null
      }
      val bodyString = response.body?.string() ?: return null
      return JSONObject(bodyString)
    }
  }

  fun sendAiChatMessage(message: String, sessionId: String?, language: String): JSONObject? {
    val urlBuilder = StringBuilder("${buildBaseUrl()}/ai/chat/send?language=$language")
    if (!sessionId.isNullOrBlank()) {
      urlBuilder.append("&session_id=").append(URLEncoder.encode(sessionId, "UTF-8"))
    }
    val url = urlBuilder.toString()
    val payload = JSONObject().put("message", message).put("context", JSONObject())
    val body = payload.toString().toRequestBody(jsonMediaType)

    val request = Request.Builder()
      .url(url)
      .post(body)
      .build()

    client.newCall(request).execute().use { response ->
      if (!response.isSuccessful) {
        return null
      }
      val bodyString = response.body?.string() ?: return null
      return JSONObject(bodyString)
    }
  }
}
