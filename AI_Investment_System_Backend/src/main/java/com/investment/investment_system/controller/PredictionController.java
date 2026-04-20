package com.investment.investment_system.controller;

import com.investment.investment_system.dto.PredictionDTO;
import com.investment.investment_system.service.PredictionService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/predictions")
public class PredictionController {

    private final PredictionService predictionService;

    public PredictionController(PredictionService predictionService) {
        this.predictionService = predictionService;
    }

    @PostMapping("/{stockId}")
    public PredictionDTO predict(@PathVariable Long stockId) {
        return predictionService.createPrediction(stockId);
    }
}