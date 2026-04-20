package com.investment.investment_system.controller;

import com.investment.investment_system.entity.PriceHistory;
import com.investment.investment_system.service.PriceHistoryService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@CrossOrigin("*")
@RestController
@RequestMapping("/price-history")
public class PriceHistoryController {

    private final PriceHistoryService priceHistoryService;

    public PriceHistoryController(PriceHistoryService priceHistoryService) {
        this.priceHistoryService = priceHistoryService;
    }

    // 🔥 ADD
    @PostMapping("/{stockId}")
    public ResponseEntity<PriceHistory> addPrice(
            @PathVariable Long stockId,
            @RequestBody PriceHistory priceHistory
    ) {
        return ResponseEntity.ok(priceHistoryService.addPriceHistory(stockId, priceHistory));
    }

    // 🔥 GET
    @GetMapping("/{stockId}")
    public ResponseEntity<List<PriceHistory>> getPrices(@PathVariable Long stockId) {
        return ResponseEntity.ok(priceHistoryService.getPriceHistory(stockId));
    }
}