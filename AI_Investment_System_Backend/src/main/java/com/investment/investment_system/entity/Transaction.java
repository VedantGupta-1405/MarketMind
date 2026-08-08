package com.investment.investment_system.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "transactions")
public class Transaction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY) // Auto-incrementing primary key
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY) //Lazy fetching to avoid loading the stock entity unless it's explicitly accessed
    @JoinColumn(name = "stock_id", nullable = false)
    @JsonIgnore
    private Stock stock;

    //Many transactions can belong to one stock, but each transaction is associated with only one stock. 

    @Enumerated(EnumType.STRING)
    @Column(nullable = false) // Store the enum as a string in the database
    private TransactionType type;

    @Column(nullable = false)
    private int quantity; // The number of shares involved in the transaction. It represents how many shares were bought or sold in this transaction.

    @Column(nullable = false)
    private double price; // The price at which the transaction occurred. It represents the price per share for the transaction.

    @Column(nullable = false)
    private LocalDateTime timestamp; // The timestamp when the transaction occurred. It is set to the current date and time when a new transaction is created.

    public Transaction() {}

    public Transaction(Stock stock, TransactionType type, int quantity, double price) {
        this.stock = stock;
        this.type = type;
        this.quantity = quantity;
        this.price = price;
        this.timestamp = LocalDateTime.now();
    }

    public Long getId() { return id; }

    public Stock getStock() { return stock; }
    public void setStock(Stock stock) { this.stock = stock; }

    public TransactionType getType() { return type; }
    public void setType(TransactionType type) { this.type = type; }

    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
}