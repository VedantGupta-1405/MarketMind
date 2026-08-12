package com.investment.investment_system.entity;

//A sentiment entity that represents the sentiment score associated with a news article. 
// It has a one-to-one relationship with the News entity.

import jakarta.persistence.*;

@Entity
@Table(name = "sentiment") //maps to the "sentiment" table in the database
public class Sentiment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private double score;

    @OneToOne
    @JoinColumn(name = "news_id", nullable = false)
    private News news;

    public Sentiment() {}

    // ===== GETTERS =====

    public Long getId() {
        return id;
    }

    public double getScore() {
        return score;
    }

    public News getNews() {
        return news;
    }

    // ===== SETTERS =====

    public void setScore(double score) {
        this.score = score;
    }

    public void setNews(News news) {
        this.news = news;
    }
}