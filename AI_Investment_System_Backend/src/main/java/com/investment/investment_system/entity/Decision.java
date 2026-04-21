package com.investment.investment_system.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity // maps to DB table
@Table(name = "decisions")
public class Decision {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id; // primary key

    private String decision; // BUY / SELL / HOLD

    private double confidence; 
    // taken from prediction probability

    private String reason; 
    // explanation string (useful for frontend/debug)

    private LocalDateTime createdAt; 
    // timestamp

    @ManyToOne
    @JoinColumn(name = "stock_id", nullable = false)
    private Stock stock; 
    // FK → which stock this decision is for

    public Decision() {}

    // ===== GETTERS =====

    public Long getId() { return id; }

    public String getDecision() { return decision; }

    public double getConfidence() { return confidence; }

    public String getReason() { return reason; }

    public LocalDateTime getCreatedAt() { return createdAt; }

    public Stock getStock() { return stock; }

    // ===== SETTERS =====

    public void setDecision(String decision) {
        this.decision = decision;
    }

    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public void setStock(Stock stock) {
        this.stock = stock;
    }
}