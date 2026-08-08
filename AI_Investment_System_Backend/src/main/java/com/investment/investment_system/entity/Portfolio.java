package com.investment.investment_system.entity;

//A portfolio represents how many shares of a stock are currently owned.

import jakarta.persistence.*;

@Entity
@Table(name = "portfolio")
public class Portfolio {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY) // Fetch the associated Stock entity lazily and it also delays the portfolio entry if the associated stock is deleted.
    @JoinColumn(name = "stock_id", nullable = false)

    // The stock associated with this portfolio entry. It represents the stock that is currently owned in the portfolio.

    private Stock stock;

    @Column(nullable = false)
    private int quantity; // The number of shares of the associated stock that are currently owned in the portfolio.

    @Column(nullable = false)
    private double averagePrice; // The average price at which the shares of the associated stock were purchased. 
                                 // It represents the cost basis for the shares owned in the portfolio.

    public Portfolio() {}

    public Portfolio(Stock stock, int quantity, double averagePrice) {
        this.stock = stock;
        this.quantity = quantity;
        this.averagePrice = averagePrice;
    }

    public Long getId() { return id; }

    public Stock getStock() { return stock; }
    public void setStock(Stock stock) { this.stock = stock; }

    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }

    public double getAveragePrice() { return averagePrice; }
    public void setAveragePrice(double averagePrice) { this.averagePrice = averagePrice; }
}   