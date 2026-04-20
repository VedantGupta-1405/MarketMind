package com.investment.investment_system.service;

import com.investment.investment_system.dto.PortfolioDTO;
import com.investment.investment_system.entity.Portfolio;
import com.investment.investment_system.repository.PortfolioRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PortfolioService {

    private final PortfolioRepository portfolioRepository;

    public PortfolioService(PortfolioRepository portfolioRepository) {
        this.portfolioRepository = portfolioRepository;
    }

    // 🔥 Get all portfolios (API use-case)
    public List<PortfolioDTO> getAllPortfolios() {
        List<Portfolio> portfolios = portfolioRepository.findAll();

        return portfolios.stream()
                .map(this::convertToDTO)
                .toList();
    }

    // 🔥 Mapping (VERY IMPORTANT SKILL)
    private PortfolioDTO convertToDTO(Portfolio portfolio) {

        double currentPrice = portfolio.getStock().getPrice();
        double totalValue = portfolio.getQuantity() * currentPrice;

        return new PortfolioDTO(
                portfolio.getStock().getId(),
                portfolio.getStock().getName(),
                portfolio.getStock().getSymbol(),
                portfolio.getQuantity(),
                portfolio.getAveragePrice(),
                currentPrice,
                totalValue
        );
    }
}