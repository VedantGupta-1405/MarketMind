package com.investment.investment_system.service;

import com.investment.investment_system.entity.News;
import com.investment.investment_system.entity.Stock;
import com.investment.investment_system.repository.StockRepository;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.parser.Parser;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
public class NewsScraperService {

    private final StockRepository stockRepository;
    private final NewsService newsService;

    private final HttpClient httpClient = HttpClient.newHttpClient();

    public NewsScraperService(StockRepository stockRepository,
                              NewsService newsService) {
        this.stockRepository = stockRepository;
        this.newsService = newsService;
    }

    public void scrapeLatestNews() {

        List<Stock> stocks = stockRepository.findAll();

        for (Stock stock : stocks) {
            scrapeNewsForStock(stock);
        }
    }

    private void scrapeNewsForStock(Stock stock) {

        try {
            String query = URLEncoder.encode(
                    stock.getSymbol() + " stock",
                    StandardCharsets.UTF_8
            );

            String feedUrl =
                    "https://news.google.com/rss/search?q="
                    + query
                    + "&hl=en-US&gl=US&ceid=US:en";

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(feedUrl))
                    .header("User-Agent", "Mozilla/5.0")
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(
                    request,
                    HttpResponse.BodyHandlers.ofString()
            );

            if (response.statusCode() != 200) {
                System.out.println(
                        "Failed to fetch news for " + stock.getSymbol()
                );
                return;
            }

            Document document = Jsoup.parse(
                    response.body(),
                    "",
                    Parser.xmlParser()
            );

            for (Element item : document.select("item")) {

                String title = item.select("title").text();
                String url = item.select("link").text();
                String description = item.select("description").text();
                String pubDate = item.select("pubDate").text();

                if (title.isBlank() || url.isBlank()) {
                    continue;
                }

                News news = new News();

                news.setTitle(title);
                news.setContent(description);
                news.setUrl(url);
                news.setPublishedAt(parsePublishedDate(pubDate));
                news.setStock(stock);

                newsService.saveScrapedNews(news);
            }

        } catch (IOException | InterruptedException e) {

            System.out.println(
                    "Error scraping news for "
                    + stock.getSymbol()
                    + ": "
                    + e.getMessage()
            );
        }
    }

    private LocalDateTime parsePublishedDate(String pubDate) {

        if (pubDate == null || pubDate.isBlank()) {
            return LocalDateTime.now();
        }

        try {
            return ZonedDateTime
                    .parse(pubDate, DateTimeFormatter.RFC_1123_DATE_TIME)
                    .withZoneSameInstant(ZoneOffset.UTC)
                    .toLocalDateTime();

        } catch (Exception e) {
            return LocalDateTime.now();
        }
    }
}