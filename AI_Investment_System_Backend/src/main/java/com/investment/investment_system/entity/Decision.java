package com.investment.investment_system.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity 
@Table(name = "decisions")
public class Decision {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY) // Standard database-generated primary key
    private Long id;

    private String decision; // Represents the decision made (e.g., "buy", "sell", "hold")

    private double confidence; // Represents the confidence level of the decision, typically a value between 0 and 1
    private String reason; // Provides a textual explanation or rationale for the decision mades

    private LocalDateTime createdAt; 

    @ManyToOne
    @JoinColumn(name = "stock_id", nullable = false) // Many decisions can be associated with one stock.
    private Stock stock; 

    public Decision() {}

    public Long getId() { return id; }

    public String getDecision() { return decision; }

    public double getConfidence() { return confidence; }

    public String getReason() { return reason; }

    public LocalDateTime getCreatedAt() { return createdAt; }

    public Stock getStock() { return stock; }

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