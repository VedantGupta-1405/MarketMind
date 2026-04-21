package com.investment.investment_system.service;

import com.investment.investment_system.dto.PredictionRequestDTO;
import com.investment.investment_system.dto.PredictionResponseDTO;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service // Service to interact with the ML model (FastAPI)
public class MlService {

    private final RestTemplate restTemplate = new RestTemplate();

    private final String PREDICT_URL = "http://localhost:8000/predict";
    private final String SENTIMENT_URL = "http://localhost:8000/sentiment";

    public PredictionResponseDTO getPrediction(Long stockId) {

        try {
            PredictionRequestDTO request = new PredictionRequestDTO();
            request.setStockId(stockId);

            return restTemplate.postForObject(
                    PREDICT_URL, // URL of the FastAPI prediction endpoint
                    request, // Request body containing the stock ID 
                    PredictionResponseDTO.class  //Expected response type from FastAPI (prediction and probability
            );

        } catch (Exception e) {
            PredictionResponseDTO fallback = new PredictionResponseDTO();
            fallback.setPrediction("UNKNOWN");
            fallback.setProbability(0.0);
            return fallback;
        }
    }

    // ========================
    // GET SENTIMENT
    // ========================
    public double getSentiment(Long stockId) {

        try {
            PredictionRequestDTO request = new PredictionRequestDTO();
            request.setStockId(stockId);

            // Using Map because FastAPI may return dynamic JSON
            Map<String, Object> response = restTemplate.postForObject(
                    SENTIMENT_URL,
                    request,
                    Map.class
            );

            if (response != null && response.containsKey("sentiment")) {
                return Double.parseDouble(response.get("sentiment").toString());
            } // If response is null or doesn't contain sentiment, return neutral sentiment

            return 0.0;

        } catch (Exception e) { // In case of any error, return neutral sentiment
            return 0.0;
        }
    }
}