package com.example.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface ShoppingDao {
  @Query("SELECT * FROM tracked_products ORDER BY addedTimestamp DESC")
  fun getAllProducts(): Flow<List<TrackedProduct>>

  @Query("SELECT * FROM tracked_products WHERE id = :productId LIMIT 1")
  suspend fun getProductById(productId: Int): TrackedProduct?

  @Insert(onConflict = OnConflictStrategy.REPLACE)
  suspend fun insertProduct(product: TrackedProduct): Long

  @Query("DELETE FROM tracked_products WHERE id = :productId")
  suspend fun deleteProductById(productId: Int)

  @Query("SELECT * FROM price_alerts ORDER BY id DESC")
  fun getAllAlerts(): Flow<List<PriceAlert>>

  @Insert(onConflict = OnConflictStrategy.REPLACE)
  suspend fun insertAlert(alert: PriceAlert)

  @Query("DELETE FROM price_alerts")
  suspend fun clearAllAlerts()
}
