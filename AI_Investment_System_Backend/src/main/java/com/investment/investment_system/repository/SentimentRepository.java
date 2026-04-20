package com.investment.investment_system.repository;

import com.investment.investment_system.entity.Sentiment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface SentimentRepository extends JpaRepository<Sentiment, Long> {

    @Query("""
        SELECT s FROM Sentiment s
        WHERE s.news.stock.id = :stockId
        ORDER BY s.id DESC
    """)
    List<Sentiment> findLatestByStockId(@Param("stockId") Long stockId);
}