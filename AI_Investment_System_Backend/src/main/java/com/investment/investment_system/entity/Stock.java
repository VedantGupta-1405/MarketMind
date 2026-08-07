package com.investment.investment_system.entity;

import com.fasterxml.jackson.annotation.JsonIgnore; //Used during JSON serialization
import jakarta.persistence.*; //Everything related to JPA (Java Persistence API) is imported from the jakarta.persistence package, 
                              //which is used for mapping Java objects to database tables and managing persistence.
import java.time.LocalDateTime;
import java.util.List;

@Entity //This tells JPA that this class is an entity and should be mapped to a database table

@Table(name = "stocks", uniqueConstraints = {
        @UniqueConstraint(columnNames = "symbol") //No two stocks can have the same symbol
})

//The @Table annotation specifies the name of the database table to which this entity will be mapped.

public class Stock {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // The @Id annotation indicates that this field is the primary key of the entity and Every table needs a primary key

    private String name;

    @Column(nullable = false, unique = true) //The @Column annotation is used to specify the properties of the column in the database table. 
                                             //In this case, it indicates that the symbol column cannot be null and must be unique across all records in the stocks table.
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