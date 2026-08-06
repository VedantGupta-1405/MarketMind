package com.investment.investment_system; // Investment System Application

import org.springframework.boot.SpringApplication; // Spring Boot Application
import org.springframework.boot.autoconfigure.SpringBootApplication;

//imports are used for starting the Spring Boot application and enabling auto-configuration.

@SpringBootApplication 

public class InvestmentSystemApplication {

	public static void main(String[] args) {
		SpringApplication.run(InvestmentSystemApplication.class, args);
	}

}
