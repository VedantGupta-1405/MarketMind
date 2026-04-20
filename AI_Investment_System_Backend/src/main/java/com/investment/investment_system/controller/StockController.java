package com.investment.investment_system.controller;

import com.investment.investment_system.entity.Stock;
import com.investment.investment_system.repository.StockRepository;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/stocks")
public class StockController {

    private final StockRepository stockRepository;

    public StockController(StockRepository stockRepository) {
        this.stockRepository = stockRepository;
    }

    // ✅ Debug endpoint (INSIDE class)
    @GetMapping("/debug")
    public String debug() {
        return "Connected";
    }

    @PostMapping
    public ResponseEntity<?> createStock(@RequestBody Stock stock) {

        try {
            Stock savedStock = stockRepository.save(stock);
            return ResponseEntity.ok(savedStock);
        } catch (DataIntegrityViolationException e) {
            return ResponseEntity
                    .badRequest()
                    .body("Stock with this symbol already exists");
        }
    }

    @GetMapping
    public List<Stock> getAllStocks() {
        return stockRepository.findAll();
    }
}