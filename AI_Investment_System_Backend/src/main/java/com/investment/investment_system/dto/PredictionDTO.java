package com.investment.investment_system.dto;

import java.time.LocalDateTime;

public class PredictionDTO {

    private Long id;
    private String prediction;
    private double probability;
    private LocalDateTime createdAt;
    private Long stockId;
    private String stockSymbol;

    public PredictionDTO() {}

    public Long getId() { return id; }
    public String getPrediction() { return prediction; }
    public double getProbability() { return probability; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public Long getStockId() { return stockId; }
    public String getStockSymbol() { return stockSymbol; }

    public void setId(Long id) { this.id = id; }
    public void setPrediction(String prediction) { this.prediction = prediction; }
    public void setProbability(double probability) { this.probability = probability; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    public void setStockId(Long stockId) { this.stockId = stockId; }
    public void setStockSymbol(String stockSymbol) { this.stockSymbol = stockSymbol; }
}