package com.investment.investment_system.dto;

public class PredictionRequestDTO {

    private Long stockId;

    public PredictionRequestDTO() {}

    public Long getStockId() {
        return stockId;
    }

    public void setStockId(Long stockId) {
        this.stockId = stockId;
    }
}