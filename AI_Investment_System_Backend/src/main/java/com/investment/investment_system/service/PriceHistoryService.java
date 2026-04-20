package com.investment.investment_system.service;

import com.investment.investment_system.entity.PriceHistory;
import com.investment.investment_system.entity.Stock;
import com.investment.investment_system.exception.ResourceNotFoundException;
import com.investment.investment_system.repository.PriceHistoryRepository;
import com.investment.investment_system.repository.StockRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PriceHistoryService {

    private final PriceHistoryRepository priceHistoryRepository;
    private final StockRepository stockRepository;

    public PriceHistoryService(PriceHistoryRepository priceHistoryRepository,
                               StockRepository stockRepository) {
        this.priceHistoryRepository = priceHistoryRepository;
        this.stockRepository = stockRepository;
    }

    public PriceHistory addPriceHistory(Long stockId, PriceHistory priceHistory) {

        Stock stock = stockRepository.findById(stockId)
                .orElseThrow(() -> new ResourceNotFoundException("Stock not found"));

        priceHistory.setStock(stock);

        return priceHistoryRepository.save(priceHistory);
    }

    public List<PriceHistory> getPriceHistory(Long stockId) {

        Stock stock = stockRepository.findById(stockId)
                .orElseThrow(() -> new ResourceNotFoundException("Stock not found"));

        return priceHistoryRepository.findByStock(stock);
    }
}