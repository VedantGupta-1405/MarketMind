package com.investment.investment_system.entity;

import com.fasterxml.jackson.annotation.JsonIgnore; //Used during JSON serialization
import jakarta.persistence.*; //Everything related to JPA (Java Persistence API) is imported from the jakarta.persistence package, 
                              //which is used for mapping Java objects to database tables and managing persistence.
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "stocks", uniqueConstraints = {
        @UniqueConstraint(columnNames = "symbol")
})
public class Stock {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @Column(nullable = false, unique = true)
    private String symbol;

    private Double price;

    private LocalDateTime createdAt = LocalDateTime.now();


    @JsonIgnore
    @OneToMany(mappedBy = "stock", cascade = CascadeType.ALL)
    private List<PriceHistory> priceHistoryList;

    @JsonIgnore
    @OneToMany(mappedBy = "stock", cascade = CascadeType.ALL)
    private List<News> newsList;

    @JsonIgnore
    @OneToMany(mappedBy = "stock", cascade = CascadeType.ALL)
    private List<Prediction> predictions;

    @JsonIgnore
    @OneToMany(mappedBy = "stock", cascade = CascadeType.ALL)
    private List<Decision> decisions;

    public Stock() {}

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getSymbol() {
        return symbol;
    }

    public Double getPrice() {
        return price;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public List<PriceHistory> getPriceHistoryList() {
        return priceHistoryList;
    }

    public List<News> getNewsList() {
        return newsList;
    }

    public List<Prediction> getPredictions() {
        return predictions;
    }

    public List<Decision> getDecisions() {
        return decisions;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }

    public void setPrice(Double price) {
        this.price = price;
    }

    public void setPriceHistoryList(List<PriceHistory> priceHistoryList) {
        this.priceHistoryList = priceHistoryList;
    }

    public void setNewsList(List<News> newsList) {
        this.newsList = newsList;
    }

    public void setPredictions(List<Prediction> predictions) {
        this.predictions = predictions;
    }

    public void setDecisions(List<Decision> decisions) {
        this.decisions = decisions;
    }
}