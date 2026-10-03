package com.investment.investment_system.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class FinnhubCandleResponseDTO {

    @JsonProperty("c")
    private List<Double> close;

    @JsonProperty("h")
    private List<Double> high;

    @JsonProperty("l")
    private List<Double> low;

    @JsonProperty("o")
    private List<Double> open;

    @JsonProperty("s")
    private String status;

    @JsonProperty("t")
    private List<Long> timestamp;

    @JsonProperty("v")
    private List<Long> volume;

    public FinnhubCandleResponseDTO() {}

    public List<Double> getClose() {
        return close;
    }

    public void setClose(List<Double> close) {
        this.close = close;
    }

    public List<Double> getHigh() {
        return high;
    }

    public void setHigh(List<Double> high) {
        this.high = high;
    }

    public List<Double> getLow() {
        return low;
    }

    public void setLow(List<Double> low) {
        this.low = low;
    }

    public List<Double> getOpen() {
        return open;
    }

    public void setOpen(List<Double> open) {
        this.open = open;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public List<Long> getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(List<Long> timestamp) {
        this.timestamp = timestamp;
    }

    public List<Long> getVolume() {
        return volume;
    }

    public void setVolume(List<Long> volume) {
        this.volume = volume;
    }
}
