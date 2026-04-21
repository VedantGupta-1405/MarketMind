package com.investment.investment_system.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "predictions")
public class Prediction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String prediction; // e.g., "UP", "DOWN", "STABLE"

    private double probability; // Confidence level of the prediction (0.0 to 1.0)

    private LocalDateTime createdAt; // Timestamp of when the prediction was made

    @ManyToOne
    @JoinColumn(name = "stock_id", nullable = false)
    private Stock stock;

    public Prediction() {}

    // ===== GETTERS =====

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

    public Stock getStock() {
        return stock;
    }

    // ===== SETTERS =====

    public void setPrediction(String prediction) {
        this.prediction = prediction;
    }

    public void setProbability(double probability) {
        this.probability = probability;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public void setStock(Stock stock) {
        this.stock = stock;
    }
}