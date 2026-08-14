package com.investment.investment_system.service;

import com.investment.investment_system.entity.News;
import com.investment.investment_system.entity.Stock;
import com.investment.investment_system.exception.ResourceNotFoundException;
import com.investment.investment_system.repository.NewsRepository;
import com.investment.investment_system.repository.StockRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class NewsService {

    private final NewsRepository newsRepository;
    private final StockRepository stockRepository;

    public NewsService(NewsRepository newsRepository,
                       StockRepository stockRepository) {
        this.newsRepository = newsRepository;
        this.stockRepository = stockRepository;
    }

    public News addNews(Long stockId, News news) {

        Stock stock = stockRepository.findById(stockId)
                .orElseThrow(() -> new ResourceNotFoundException("Stock not found"));

        news.setStock(stock);

        return newsRepository.save(news);
    }

    public News saveScrapedNews(News news) {

        if (newsRepository.existsByUrl(news.getUrl())) {
            return null;
        }

        return newsRepository.save(news);
    }

    public List<News> getNews(Long stockId) {

        Stock stock = stockRepository.findById(stockId)
                .orElseThrow(() -> new ResourceNotFoundException("Stock not found"));

        return newsRepository.findByStock(stock);
    }
}