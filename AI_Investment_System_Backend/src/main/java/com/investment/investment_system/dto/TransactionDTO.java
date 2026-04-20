package com.investment.investment_system.dto;

import java.time.LocalDateTime;

public class TransactionDTO {

    private Long id;
    private String stockSymbol;
    private String type;
    private int quantity;
    private double price;
    private LocalDateTime timestamp;

    public TransactionDTO(Long id, String stockSymbol, String type,
                          int quantity, double price, LocalDateTime timestamp) {
        this.id = id;
        this.stockSymbol = stockSymbol;
        this.type = type;
        this.quantity = quantity;
        this.price = price;
        this.timestamp = timestamp;
    }

    public Long getId() { return id; }
    public String getStockSymbol() { return stockSymbol; }
    public String getType() { return type; }
    public int getQuantity() { return quantity; }
    public double getPrice() { return price; }
    public LocalDateTime getTimestamp() { return timestamp; }
}