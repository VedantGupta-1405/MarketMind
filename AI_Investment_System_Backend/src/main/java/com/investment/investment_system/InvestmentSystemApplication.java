package com.investment.investment_system;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication //scans com.investment.investment_system.* for components, configurations, and services

public class InvestmentSystemApplication {

	public static void main(String[] args) {
		SpringApplication.run(InvestmentSystemApplication.class, args);
	}

}
