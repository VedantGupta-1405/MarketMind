package com.investment.investment_system.repository;

import com.investment.investment_system.entity.Decision;
import com.investment.investment_system.entity.Stock;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DecisionRepository extends JpaRepository<Decision, Long> {

    List<Decision> findByStock(Stock stock);
}