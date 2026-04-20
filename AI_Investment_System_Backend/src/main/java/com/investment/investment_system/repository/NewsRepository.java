package com.investment.investment_system.repository;

import com.investment.investment_system.entity.News;
import com.investment.investment_system.entity.Stock;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface NewsRepository extends JpaRepository<News, Long> {

    // 🔥 Get latest news for a stock
    Optional<News> findTopByStockIdOrderByIdDesc(Long stockId);

    // 🔥 Get all news for a stock
    List<News> findByStock(Stock stock);
}