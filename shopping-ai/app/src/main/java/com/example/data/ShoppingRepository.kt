package com.example.data

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.firstOrNull

class ShoppingRepository(private val dao: ShoppingDao) {
  val allProducts: Flow<List<TrackedProduct>> = dao.getAllProducts()
  val allAlerts: Flow<List<PriceAlert>> = dao.getAllAlerts()

  suspend fun insertProduct(product: TrackedProduct): Long {
    return dao.insertProduct(product)
  }

  suspend fun deleteProductById(id: Int) {
    dao.deleteProductById(id)
  }

  suspend fun insertAlert(alert: PriceAlert) {
    dao.insertAlert(alert)
  }
}
