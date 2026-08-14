package com.investment.investment_system.repository;

import com.investment.investment_system.entity.Stock;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface StockRepository extends JpaRepository<Stock, Long> { //Create a repository for the Stock entity, extending JpaRepository to provide CRUD operations and additional query methods.

    Optional<Stock> findBySymbol(String symbol);
}