package com.investment.investment_system.service;

import com.investment.investment_system.entity.Decision;
import com.investment.investment_system.entity.Prediction;
import com.investment.investment_system.entity.Sentiment;
import com.investment.investment_system.repository.DecisionRepository;
import com.investment.investment_system.repository.SentimentRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class DecisionService {

    private final DecisionRepository decisionRepository;
    private final SentimentRepository sentimentRepository;

    public DecisionService(DecisionRepository decisionRepository,
                           SentimentRepository sentimentRepository) {
        this.decisionRepository = decisionRepository;
        this.sentimentRepository = sentimentRepository;
    }

    public Decision generateDecision(Prediction prediction) {

        String predictionValue = prediction.getPrediction();
        double probability = prediction.getProbability();

        // 1. Get latest sentiment
        List<Sentiment> sentiments = sentimentRepository.findLatestByStockId(
                prediction.getStock().getId()
        );

        double sentimentScore = 0.0;

        if (!sentiments.isEmpty()) {
            sentimentScore = sentiments.get(0).getScore();
        }

        // 2. Decision logic
        String decisionValue;
        String reason;

        if ("UP".equalsIgnoreCase(predictionValue)) {

            if (sentimentScore > 0.5) {
                decisionValue = "BUY";
                reason = "Prediction is UP with strong positive sentiment (" + sentimentScore + ")";
            } else if (sentimentScore > 0) {
                decisionValue = "HOLD";
                reason = "Prediction is UP but sentiment is weak (" + sentimentScore + ")";
            } else {
                decisionValue = "HOLD";
                reason = "Prediction is UP but sentiment is negative (" + sentimentScore + ")";
            }

        } else if ("DOWN".equalsIgnoreCase(predictionValue)) {

            if (sentimentScore < -0.5) {
                decisionValue = "SELL";
                reason = "Prediction is DOWN with strong negative sentiment (" + sentimentScore + ")";
            } else if (sentimentScore < 0) {
                decisionValue = "HOLD";
                reason = "Prediction is DOWN but sentiment is weak (" + sentimentScore + ")";
            } else {
                decisionValue = "HOLD";
                reason = "Prediction is DOWN but sentiment is positive (" + sentimentScore + ")";
            }

        } else {
            decisionValue = "HOLD";
            reason = "Prediction is uncertain";
        }

        // 3. Save decision
        Decision decision = new Decision();
        decision.setDecision(decisionValue);
        decision.setConfidence(probability);
        decision.setReason(reason); // 🔥 NEW
        decision.setCreatedAt(LocalDateTime.now());
        decision.setStock(prediction.getStock());

        return decisionRepository.save(decision);
    }
}