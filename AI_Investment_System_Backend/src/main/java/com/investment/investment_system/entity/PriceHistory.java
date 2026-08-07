package com.investment.investment_system.entity;

//This entity stores the historical market data of a stock.

import jakarta.persistence.*;
import java.time.LocalDate;

@Entity
@Table(name = "price_history") //maps this entity to the price_history table in the database
public class PriceHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY) //geenerates ID automatically for each new record
    private Long id;

    private LocalDate date; //we care only about the date, not the time, for historical stock prices

    private double openPrice;
    private double closePrice;
    private double high;
    private double low;

    //standard stock market data fields

    private Long volume;

    @ManyToOne //multiple price history records can be associated with a single stock
    @JoinColumn(name = "stock_id", nullable = false) //specifies the foreign key column in the price_history table that references the primary key of the stocks table.
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

    //getters for all the fields in the PriceHistory entity.

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

    //setters for all the fields in the PriceHistory entity.

}