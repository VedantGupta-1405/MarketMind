package com.investment.investment_system.repository;

import com.investment.investment_system.entity.Prediction;
import com.investment.investment_system.entity.Stock;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface PredictionRepository extends JpaRepository<Prediction, Long> {

    List<Prediction> findByStock(Stock stock);
}