package com.investment.investment_system.service;

import com.investment.investment_system.entity.Decision;
import com.investment.investment_system.entity.Prediction;
import com.investment.investment_system.entity.Sentiment;
import com.investment.investment_system.repository.DecisionRepository;
import com.investment.investment_system.repository.SentimentRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service // business logic for final decision
public class DecisionService {

    private final DecisionRepository decisionRepository; // DB: decisions
    private final SentimentRepository sentimentRepository; // DB: sentiment

    public DecisionService(DecisionRepository decisionRepository,
                           SentimentRepository sentimentRepository) {
        this.decisionRepository = decisionRepository;
        this.sentimentRepository = sentimentRepository;
    }

    public Decision generateDecision(Prediction prediction) {

        String predictionValue = prediction.getPrediction(); 
        // ML output: "UP" / "DOWN"

        double probability = prediction.getProbability(); 
        // ML confidence

        // 1. fetch latest sentiment for stock
        List<Sentiment> sentiments = sentimentRepository.findLatestByStockId(
                prediction.getStock().getId()
        );

        double sentimentScore = 0.0;

        if (!sentiments.isEmpty()) {
            sentimentScore = sentiments.get(0).getScore(); 
            // takes latest sentiment
        }

        // 2. decision logic (rule-based engine)
        String decisionValue;
        String reason;

        if ("UP".equalsIgnoreCase(predictionValue)) {

            if (sentimentScore > 0.5) {
                decisionValue = "BUY"; // strong positive signal
                reason = "Prediction is UP with strong positive sentiment (" + sentimentScore + ")";
            } else if (sentimentScore > 0) {
                decisionValue = "HOLD"; // weak positive
                reason = "Prediction is UP but sentiment is weak (" + sentimentScore + ")";
            } else {
                decisionValue = "HOLD"; // negative sentiment overrides
                reason = "Prediction is UP but sentiment is negative (" + sentimentScore + ")";
            }

        } else if ("DOWN".equalsIgnoreCase(predictionValue)) {

            if (sentimentScore < -0.5) {
                decisionValue = "SELL"; // strong negative signal
                reason = "Prediction is DOWN with strong negative sentiment (" + sentimentScore + ")";
            } else if (sentimentScore < 0) {
                decisionValue = "HOLD"; // weak negative
                reason = "Prediction is DOWN but sentiment is weak (" + sentimentScore + ")";
            } else {
                decisionValue = "HOLD"; // positive sentiment cancels sell
                reason = "Prediction is DOWN but sentiment is positive (" + sentimentScore + ")";
            }

        } else {
            decisionValue = "HOLD"; // fallback for UNKNOWN
            reason = "Prediction is uncertain";
        }

        // 3. map → Decision entity
        Decision decision = new Decision();
        decision.setDecision(decisionValue);
        decision.setConfidence(probability); // uses ML probability
        decision.setReason(reason); // explanation string (good for UI/debug)
        decision.setCreatedAt(LocalDateTime.now());
        decision.setStock(prediction.getStock()); // FK relation

        return decisionRepository.save(decision); 
        // persist decision in DB
    }
}