package com.investment.investment_system.controller;

import com.investment.investment_system.dto.MarketCandleDTO;
import com.investment.investment_system.service.MarketDataService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@CrossOrigin("*")
@RestController
@RequestMapping("/market-data")
public class MarketDataController {

    private final MarketDataService marketDataService;

    public MarketDataController(MarketDataService marketDataService) {
        this.marketDataService = marketDataService;
    }

    @GetMapping("/candles/{symbol}")
    public ResponseEntity<?> getCandles(
            @PathVariable String symbol,
            @RequestParam(required = false, defaultValue = "D") String resolution,
            @RequestParam(required = false) Long from,
            @RequestParam(required = false) Long to
    ) {
        try {
            List<MarketCandleDTO> candles = marketDataService.getCandles(symbol, resolution, from, to);
            return ResponseEntity.ok(candles);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body("Failed to retrieve market candle data");
        }
    }
}
