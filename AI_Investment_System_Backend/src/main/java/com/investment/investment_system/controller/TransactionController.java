package com.investment.investment_system.controller;

import com.investment.investment_system.dto.TransactionDTO;
import com.investment.investment_system.dto.TransactionRequestDTO;
import com.investment.investment_system.service.TransactionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/transactions")
public class TransactionController {

    private final TransactionService transactionService;

    public TransactionController(TransactionService transactionService) {
        this.transactionService = transactionService;
    }

    @PostMapping("/buy")
    public ResponseEntity<Map<String, String>> buyStock(@RequestBody TransactionRequestDTO request) {

        transactionService.buyStock(
                request.getStockId(),
                request.getQuantity(),
                request.getPrice()
        );

        return ResponseEntity.ok(Map.of("message", "Stock bought successfully"));
    }

    @PostMapping("/sell")
    public ResponseEntity<Map<String, String>> sellStock(@RequestBody TransactionRequestDTO request) {

        transactionService.sellStock(
                request.getStockId(),
                request.getQuantity(),
                request.getPrice()
        );

        return ResponseEntity.ok(Map.of("message", "Stock sold successfully"));
    }

    @GetMapping
    public ResponseEntity<List<TransactionDTO>> getAllTransactions() {
        return ResponseEntity.ok(transactionService.getAllTransactions());
    }
}