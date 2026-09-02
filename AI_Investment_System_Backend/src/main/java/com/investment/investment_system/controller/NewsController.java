package com.investment.investment_system.controller;

import com.investment.investment_system.entity.News;
import com.investment.investment_system.service.NewsService;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@CrossOrigin("*")
@RestController
@RequestMapping("/news")
public class NewsController {

    private final NewsService newsService;

    public NewsController(NewsService newsService) {
        this.newsService = newsService;
    }

    @PostMapping("/{stockId}")
    public ResponseEntity<News> addNews(
            @PathVariable Long stockId,
            @RequestBody News news
    ) {
        return ResponseEntity.ok(
                newsService.addNews(stockId, news)
        );
    }

    @GetMapping("/{stockId}")
    public ResponseEntity<List<News>> getNews(
            @PathVariable Long stockId
    ) {
        return ResponseEntity.ok(
                newsService.getNews(stockId)
        );
    }
}