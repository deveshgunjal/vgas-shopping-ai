package com.example.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(entities = [TrackedProduct::class, PriceAlert::class], version = 2, exportSchema = false)
abstract class ShoppingDatabase : RoomDatabase() {
  abstract fun shoppingDao(): ShoppingDao

  companion object {
    @Volatile
    private var INSTANCE: ShoppingDatabase? = null

    fun getDatabase(context: Context): ShoppingDatabase {
      return INSTANCE ?: synchronized(this) {
        val instance = Room.databaseBuilder(
          context.applicationContext,
          ShoppingDatabase::class.java,
          "shopping_ai_database"
        )
        .fallbackToDestructiveMigration()
        .build()
        INSTANCE = instance
        instance
      }
    }
  }
}
