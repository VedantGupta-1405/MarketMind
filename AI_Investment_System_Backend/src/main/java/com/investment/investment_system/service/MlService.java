package com.investment.investment_system.service;

import com.investment.investment_system.dto.PredictionRequestDTO;
import com.investment.investment_system.dto.PredictionResponseDTO;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class MlService {

    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${ml.service.url:http://localhost:8000}")
    private String mlServiceBaseUrl;

    private String getPredictUrl() {
        return mlServiceBaseUrl + "/predict";
    }

    private String getSentimentUrl() {
        return mlServiceBaseUrl + "/sentiment";
    }

    public PredictionResponseDTO getPrediction(
            Long stockId,
            String newsTitle,
            String newsContent
    ) {

        try {
            PredictionRequestDTO request = new PredictionRequestDTO();

            request.setStockId(stockId);
            request.setNewsTitle(newsTitle);
            request.setNewsContent(newsContent);

            return restTemplate.postForObject(
                    getPredictUrl(),
                    request,
                    PredictionResponseDTO.class
            );

        } catch (Exception e) {
            PredictionResponseDTO fallback = new PredictionResponseDTO();
            fallback.setPrediction("UNKNOWN");
            fallback.setProbability(0.0);

            return fallback;
        }
    }

    public double getSentiment(
            Long stockId,
            String newsTitle,
            String newsContent
    ) {

        try {
            PredictionRequestDTO request = new PredictionRequestDTO();

            request.setStockId(stockId);
            request.setNewsTitle(newsTitle);
            request.setNewsContent(newsContent);

            Map<String, Object> response = restTemplate.postForObject(
                    getSentimentUrl(),
                    request,
                    Map.class
            );

            if (response != null && response.containsKey("sentiment")) {
                return Double.parseDouble(
                        response.get("sentiment").toString()
                );
            }

            return 0.0;

        } catch (Exception e) {
            return 0.0;
        }
    }
}