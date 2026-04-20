package com.investment.investment_system.dto;

public class PredictionResponseDTO {

    private String prediction;
    private double probability;

    public PredictionResponseDTO() {}

    public String getPrediction() {
        return prediction;
    }

    public double getProbability() {
        return probability;
    }

    public void setPrediction(String prediction) {
        this.prediction = prediction;
    }

    public void setProbability(double probability) {
        this.probability = probability;
    }
}