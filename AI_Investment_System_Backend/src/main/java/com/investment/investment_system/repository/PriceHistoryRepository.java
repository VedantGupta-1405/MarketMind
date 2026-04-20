package com.investment.investment_system.repository;

import com.investment.investment_system.entity.PriceHistory;
import com.investment.investment_system.entity.Stock;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface PriceHistoryRepository extends JpaRepository<PriceHistory, Long> {

    List<PriceHistory> findByStock(Stock stock);
}