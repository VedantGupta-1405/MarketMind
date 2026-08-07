package com.investment.investment_system.entity;

//This entity stores the historical market data of a stock.

import jakarta.persistence.*;
import java.time.LocalDate;

@Entity
@Table(name = "price_history")
public class PriceHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private LocalDate date;

    private double openPrice;
    private double closePrice;
    private double high;
    private double low;

    private Long volume;

    @ManyToOne
    @JoinColumn(name = "stock_id", nullable = false)
    private Stock stock;

    public PriceHistory() {}

    public Long getId() {
        return id;
    }

    public LocalDate getDate() {
        return date;
    }

    public double getOpenPrice() {
        return openPrice;
    }

    public double getClosePrice() {
        return closePrice;
    }

    public double getHigh() {
        return high;
    }

    public double getLow() {
        return low;
    }

    public Long getVolume() {
        return volume;
    }

    public Stock getStock() {
        return stock;
    }

    public void setDate(LocalDate date) {
        this.date = date;
    }

    public void setOpenPrice(double openPrice) {
        this.openPrice = openPrice;
    }

    public void setClosePrice(double closePrice) {
        this.closePrice = closePrice;
    }

    public void setHigh(double high) {
        this.high = high;
    }

    public void setLow(double low) {
        this.low = low;
    }

    public void setVolume(Long volume) {
        this.volume = volume;
    }

    public void setStock(Stock stock) {
        this.stock = stock;
    }
}