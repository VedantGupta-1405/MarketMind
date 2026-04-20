package com.investment.investment_system.repository;

import com.investment.investment_system.entity.Portfolio;
import com.investment.investment_system.entity.Stock;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface PortfolioRepository extends JpaRepository<Portfolio, Long> {

    Optional<Portfolio> findByStock(Stock stock);
}