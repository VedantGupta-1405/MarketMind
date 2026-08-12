package com.investment.investment_system.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "news") // Defines the database table for this entity
public class News {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    //Standard database-generated primary key

    private String title;

    @Column(columnDefinition = "TEXT") // Specifies that the content column should be of type TEXT in the database
    private String content;

    private LocalDateTime publishedAt; // Represents the date and time when the news was published

    @ManyToOne
    @JoinColumn(name = "stock_id", nullable = false)
    private Stock stock;

    //Many news articles can belong to one stock.

    public News() {}

    public Long getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getContent() {
        return content;
    }

    public LocalDateTime getPublishedAt() {
        return publishedAt;
    }

    public Stock getStock() {
        return stock;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public void setPublishedAt(LocalDateTime publishedAt) {
        this.publishedAt = publishedAt;
    }

    public void setStock(Stock stock) {
        this.stock = stock;
    }
}