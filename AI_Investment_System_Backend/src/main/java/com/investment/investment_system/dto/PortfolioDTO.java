package com.investment.investment_system.dto;

public class PortfolioDTO {

    private Long stockId;
    private String stockName;
    private String symbol;

    private int quantity;
    private double averagePrice;

    private double currentPrice;
    private double totalValue;

    public PortfolioDTO() {}

    public PortfolioDTO(Long stockId, String stockName, String symbol,
                        int quantity, double averagePrice,
                        double currentPrice, double totalValue) {
        this.stockId = stockId;
        this.stockName = stockName;
        this.symbol = symbol;
        this.quantity = quantity;
        this.averagePrice = averagePrice;
        this.currentPrice = currentPrice;
        this.totalValue = totalValue;
    }

    // getters + setters
}