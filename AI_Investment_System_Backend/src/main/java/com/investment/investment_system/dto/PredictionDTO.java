package com.investment.investment_system.dto;

import java.time.LocalDateTime;

public class PredictionDTO {

    private Long id;
    private String prediction;
    private double probability;
    private LocalDateTime createdAt;
    private Long stockId;
    private String stockSymbol;
    private String decision;
    private double sentiment;
    private double decisionConfidence;
    private String reason;

    public PredictionDTO() {}

    public Long getId() {
        return id;
    }

    public String getPrediction() {
        return prediction;
    }

    public double getProbability() {
        return probability;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public Long getStockId() {
        return stockId;
    }

    public String getStockSymbol() {
        return stockSymbol;
    }

    public String getDecision() {
        return decision;
    }

    public double getSentiment() {
        return sentiment;
    }

    public double getDecisionConfidence() {
        return decisionConfidence;
    }

    public String getReason() {
        return reason;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setPrediction(String prediction) {
        this.prediction = prediction;
    }

    public void setProbability(double probability) {
        this.probability = probability;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public void setStockId(Long stockId) {
        this.stockId = stockId;
    }

    public void setStockSymbol(String stockSymbol) {
        this.stockSymbol = stockSymbol;
    }

    public void setDecision(String decision) {
        this.decision = decision;
    }

    public void setSentiment(double sentiment) {
        this.sentiment = sentiment;
    }

    public void setDecisionConfidence(double decisionConfidence) {
        this.decisionConfidence = decisionConfidence;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }
}