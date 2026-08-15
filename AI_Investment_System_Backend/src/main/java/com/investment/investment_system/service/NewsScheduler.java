package com.investment.investment_system.service;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class NewsScheduler {

    private final NewsScraperService newsScraperService;

    public NewsScheduler(NewsScraperService newsScraperService) {
        this.newsScraperService = newsScraperService;
    }

    @Scheduled(fixedRate = 60000)
    public void scrapeNews() {
        newsScraperService.scrapeLatestNews();
    }
}