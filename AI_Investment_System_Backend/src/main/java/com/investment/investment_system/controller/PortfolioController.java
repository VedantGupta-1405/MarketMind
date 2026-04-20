package com.investment.investment_system.controller;

import com.investment.investment_system.entity.Portfolio;
import com.investment.investment_system.repository.PortfolioRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/portfolio")
public class PortfolioController {

    private final PortfolioRepository portfolioRepository;

    public PortfolioController(PortfolioRepository portfolioRepository) {
        this.portfolioRepository = portfolioRepository;
    }

    @GetMapping
    public List<Portfolio> getPortfolio() {
        return portfolioRepository.findAll();
    }
}