package com.investment.investment_system.service;

import com.investment.investment_system.dto.FinnhubCandleResponseDTO;
import com.investment.investment_system.dto.MarketCandleDTO;
import com.investment.investment_system.entity.PriceHistory;
import com.investment.investment_system.entity.Stock;
import com.investment.investment_system.repository.PriceHistoryRepository;
import com.investment.investment_system.repository.StockRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.*;

@Service
public class MarketDataService {

    private static final Logger logger = LoggerFactory.getLogger(MarketDataService.class);

    private final RestTemplate restTemplate;
    private final StockRepository stockRepository;
    private final PriceHistoryRepository priceHistoryRepository;

    @Value("${finnhub.api-key:}")
    private String finnhubApiKey;

    @Value("${finnhub.base-url:https://finnhub.io/api/v1}")
    private String finnhubBaseUrl;

    private static final Set<String> SUPPORTED_SYMBOLS = Set.of("AAPL", "GOOGL", "MSFT", "AMZN");

    public MarketDataService(StockRepository stockRepository,
                             PriceHistoryRepository priceHistoryRepository) {
        this.restTemplate = new RestTemplate();
        this.stockRepository = stockRepository;
        this.priceHistoryRepository = priceHistoryRepository;
    }

    public List<MarketCandleDTO> getCandles(String symbol, String resolution, Long from, Long to) {
        if (symbol == null || symbol.trim().isEmpty()) {
            throw new IllegalArgumentException("Stock symbol must not be empty");
        }

        String normalizedSymbol = symbol.trim().toUpperCase();
        if (!SUPPORTED_SYMBOLS.contains(normalizedSymbol)) {
            throw new IllegalArgumentException("Unsupported stock symbol: " + normalizedSymbol);
        }

        String res = (resolution == null || resolution.trim().isEmpty()) ? "D" : resolution.trim();

        long toTime = (to != null && to > 0) ? to : Instant.now().getEpochSecond();
        long fromTime = (from != null && from > 0) ? from : (toTime - (180L * 24 * 60 * 60)); // default ~6 months

        if (fromTime >= toTime) {
            fromTime = toTime - (180L * 24 * 60 * 60);
        }

        // Try Finnhub if API key is provided
        if (finnhubApiKey != null && !finnhubApiKey.trim().isEmpty()) {
            try {
                String url = UriComponentsBuilder.fromHttpUrl(finnhubBaseUrl + "/stock/candle")
                        .queryParam("symbol", normalizedSymbol)
                        .queryParam("resolution", res)
                        .queryParam("from", fromTime)
                        .queryParam("to", toTime)
                        .queryParam("token", finnhubApiKey.trim())
                        .toUriString();

                FinnhubCandleResponseDTO response = restTemplate.getForObject(url, FinnhubCandleResponseDTO.class);

                if (response != null && "ok".equalsIgnoreCase(response.getStatus())
                        && response.getTimestamp() != null && !response.getTimestamp().isEmpty()) {

                    List<MarketCandleDTO> candles = new ArrayList<>();
                    int size = response.getTimestamp().size();

                    for (int i = 0; i < size; i++) {
                        long ts = response.getTimestamp().get(i);
                        String dateStr = LocalDate.ofInstant(Instant.ofEpochSecond(ts), ZoneOffset.UTC).toString();

                        Double open = (response.getOpen() != null && i < response.getOpen().size()) ? response.getOpen().get(i) : null;
                        Double high = (response.getHigh() != null && i < response.getHigh().size()) ? response.getHigh().get(i) : null;
                        Double low = (response.getLow() != null && i < response.getLow().size()) ? response.getLow().get(i) : null;
                        Double close = (response.getClose() != null && i < response.getClose().size()) ? response.getClose().get(i) : null;
                        Long volume = (response.getVolume() != null && i < response.getVolume().size()) ? response.getVolume().get(i) : 0L;

                        if (close != null && close > 0) {
                            if (open == null || open <= 0) open = close;
                            if (high == null || high <= 0) high = Math.max(open, close);
                            if (low == null || low <= 0) low = Math.min(open, close);

                            candles.add(new MarketCandleDTO(dateStr, ts, open, high, low, close, volume));
                        }
                    }

                    if (!candles.isEmpty()) {
                        candles.sort(Comparator.comparing(MarketCandleDTO::getTimestamp));
                        logger.info("Loaded {} candle bars from Finnhub for {}", candles.size(), normalizedSymbol);
                        return candles;
                    }
                } else {
                    logger.warn("Finnhub returned non-ok status or empty data for {}", normalizedSymbol);
                }
            } catch (Exception e) {
                logger.warn("Failed to fetch candle data from Finnhub for {}: {}", normalizedSymbol, e.getMessage());
            }
        } else {
            logger.debug("Finnhub API key not configured, using database historical prices for {}", normalizedSymbol);
        }

        // Fallback to internal database historical data
        return getFallbackCandlesFromDb(normalizedSymbol);
    }

    private List<MarketCandleDTO> getFallbackCandlesFromDb(String symbol) {
        Optional<Stock> stockOpt = stockRepository.findAll().stream()
                .filter(s -> symbol.equalsIgnoreCase(s.getSymbol()))
                .findFirst();

        if (stockOpt.isEmpty()) {
            return Collections.emptyList();
        }

        List<PriceHistory> history = priceHistoryRepository.findByStock(stockOpt.get());
        if (history == null || history.isEmpty()) {
            return Collections.emptyList();
        }

        List<MarketCandleDTO> candles = new ArrayList<>();
        for (PriceHistory ph : history) {
            if (ph.getDate() == null) {
                continue;
            }

            String dateStr = ph.getDate().toString();
            long ts = ph.getDate().atStartOfDay(ZoneOffset.UTC).toEpochSecond();

            double close = ph.getClosePrice();
            if (close <= 0) {
                continue;
            }

            double open = ph.getOpenPrice() > 0 ? ph.getOpenPrice() : close;
            double high = ph.getHigh() > 0 ? ph.getHigh() : Math.max(open, close);
            double low = ph.getLow() > 0 ? ph.getLow() : Math.min(open, close);
            long volume = ph.getVolume() != null ? ph.getVolume() : 0L;

            candles.add(new MarketCandleDTO(dateStr, ts, open, high, low, close, volume));
        }

        candles.sort(Comparator.comparing(MarketCandleDTO::getDate));
        return candles;
    }
}
