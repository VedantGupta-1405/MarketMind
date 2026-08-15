package com.investment.investment_system.service;

import com.investment.investment_system.dto.PredictionDTO;
import com.investment.investment_system.dto.PredictionResponseDTO;
import com.investment.investment_system.entity.News;
import com.investment.investment_system.entity.Prediction;
import com.investment.investment_system.entity.Sentiment;
import com.investment.investment_system.entity.Stock;
import com.investment.investment_system.repository.NewsRepository;
import com.investment.investment_system.repository.PredictionRepository;
import com.investment.investment_system.repository.SentimentRepository;
import com.investment.investment_system.repository.StockRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Optional;

@Service
public class PredictionService {

    private final MlService mlService;
    private final PredictionRepository predictionRepository;
    private final StockRepository stockRepository;
    private final DecisionService decisionService;
    private final SentimentRepository sentimentRepository;
    private final NewsRepository newsRepository;

    public PredictionService(MlService mlService,
                             PredictionRepository predictionRepository,
                             StockRepository stockRepository,
                             DecisionService decisionService,
                             SentimentRepository sentimentRepository,
                             NewsRepository newsRepository) {
        this.mlService = mlService;
        this.predictionRepository = predictionRepository;
        this.stockRepository = stockRepository;
        this.decisionService = decisionService;
        this.sentimentRepository = sentimentRepository;
        this.newsRepository = newsRepository;
    }

    public PredictionDTO createPrediction(Long stockId) {

        Stock stock = stockRepository.findById(stockId)
                .orElseThrow(() -> new RuntimeException("Stock not found"));

        Optional<News> latestNews =
                newsRepository.findTopByStockIdOrderByIdDesc(stockId);

        String newsTitle = "";
        String newsContent = "";

        if (latestNews.isPresent()) {
            newsTitle = latestNews.get().getTitle();
            newsContent = latestNews.get().getContent();
        }

        PredictionResponseDTO mlResponse =
                mlService.getPrediction(
                        stockId,
                        newsTitle,
                        newsContent
                );

        double sentimentScore = mlService.getSentiment(stockId);

        Prediction prediction = new Prediction();
        prediction.setPrediction(mlResponse.getPrediction());
        prediction.setProbability(mlResponse.getProbability());
        prediction.setCreatedAt(LocalDateTime.now());
        prediction.setStock(stock);

        Prediction savedPrediction = predictionRepository.save(prediction);

        if (latestNews.isPresent()) {
            Sentiment sentiment = new Sentiment();
            sentiment.setScore(sentimentScore);
            sentiment.setNews(latestNews.get());

            sentimentRepository.save(sentiment);
        }

        decisionService.generateDecision(savedPrediction);

        PredictionDTO dto = new PredictionDTO();
        dto.setId(savedPrediction.getId());
        dto.setPrediction(savedPrediction.getPrediction());
        dto.setProbability(savedPrediction.getProbability());
        dto.setCreatedAt(savedPrediction.getCreatedAt());
        dto.setStockId(stock.getId());
        dto.setStockSymbol(stock.getSymbol());

        return dto;
    }
}