package com.investment.investment_system.controller;

import com.investment.investment_system.dto.PredictionDTO;
import com.investment.investment_system.service.PredictionService;
import org.springframework.web.bind.annotation.*;

@CrossOrigin("*")// allows all origins (dev only, insecure for prod)
@RestController // marks class as REST API and then methods return JSON by default
@RequestMapping("/predictions")// base path: /predictions
public class PredictionController {

    private final PredictionService predictionService; // service layer for business logic

    public PredictionController(PredictionService predictionService) {
        this.predictionService = predictionService;
    }

    @PostMapping("/{stockId}") // POST /predictions/{stockId} to create a new prediction for a stock
    public PredictionDTO predict(@PathVariable Long stockId) {
        return predictionService.createPrediction(stockId); // calls service to create prediction and returns it as JSON
    }
}