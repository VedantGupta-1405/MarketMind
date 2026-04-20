package com.investment.investment_system.dto;

public class TransactionRequestDTO {

    private Long stockId;
    private int quantity;
    private double price;

    public TransactionRequestDTO() {}

    public Long getStockId() { return stockId; }
    public void setStockId(Long stockId) { this.stockId = stockId; }

    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }
}