package com.investment.investment_system.service;

import com.investment.investment_system.dto.TransactionDTO;
import com.investment.investment_system.entity.*;
import com.investment.investment_system.exception.BadRequestException;
import com.investment.investment_system.exception.ResourceNotFoundException;
import com.investment.investment_system.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class TransactionService {

    private final StockRepository stockRepository;
    private final TransactionRepository transactionRepository;
    private final PortfolioRepository portfolioRepository;

    public TransactionService(StockRepository stockRepository,
                              TransactionRepository transactionRepository,
                              PortfolioRepository portfolioRepository) {
        this.stockRepository = stockRepository;
        this.transactionRepository = transactionRepository;
        this.portfolioRepository = portfolioRepository;
    }

    @Transactional
    public void buyStock(Long stockId, int quantity, double price) {

        if (quantity <= 0 || price <= 0) {
            throw new BadRequestException("Invalid quantity or price");
        }

        Stock stock = stockRepository.findById(stockId)
                .orElseThrow(() -> new ResourceNotFoundException("Stock not found"));

        Portfolio portfolio = portfolioRepository.findByStock(stock)
                .orElse(null);

        if (portfolio == null) {
            portfolio = new Portfolio(stock, quantity, price);
        } else {
            int oldQty = portfolio.getQuantity();
            double oldAvg = portfolio.getAveragePrice();

            int newQty = oldQty + quantity;

            double newAvgPrice = ((oldQty * oldAvg) + (quantity * price)) / newQty;

            portfolio.setQuantity(newQty);
            portfolio.setAveragePrice(newAvgPrice);
        }

        portfolioRepository.save(portfolio);

        Transaction transaction = new Transaction(
                stock,
                TransactionType.BUY,
                quantity,
                price
        );

        transactionRepository.save(transaction);
    }

    @Transactional
    public void sellStock(Long stockId, int quantity, double price) {

        if (quantity <= 0 || price <= 0) {
            throw new BadRequestException("Invalid quantity or price");
        }

        Stock stock = stockRepository.findById(stockId)
                .orElseThrow(() -> new ResourceNotFoundException("Stock not found"));

        Portfolio portfolio = portfolioRepository.findByStock(stock)
                .orElseThrow(() -> new BadRequestException("No stock in portfolio"));

        if (portfolio.getQuantity() < quantity) {
            throw new BadRequestException("Not enough stock to sell");
        }

        int remainingQty = portfolio.getQuantity() - quantity;

        if (remainingQty == 0) {
            portfolioRepository.delete(portfolio);
        } else {
            portfolio.setQuantity(remainingQty);
            portfolioRepository.save(portfolio);
        }

        Transaction transaction = new Transaction(
                stock,
                TransactionType.SELL,
                quantity,
                price
        );

        transactionRepository.save(transaction);
    }

    public List<TransactionDTO> getAllTransactions() {
        return transactionRepository.findAllByOrderByTimestampDesc()
                .stream()
                .map(t -> new TransactionDTO(
                        t.getId(),
                        t.getStock().getSymbol(),
                        t.getType().name(),
                        t.getQuantity(),
                        t.getPrice(),
                        t.getTimestamp()
                ))
                .toList();
    }
}