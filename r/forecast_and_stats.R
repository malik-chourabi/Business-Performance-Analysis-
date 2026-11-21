# R: statistical analysis and forecasting comparison (run from project root: Rscript r/forecast_and_stats.R)
suppressPackageStartupMessages({library(forecast)})
d <- read.csv("data/processed/cleaned_sales.csv", stringsAsFactors = FALSE)
d$Order.Date <- as.Date(d$Order.Date)
cat("Rows:", nrow(d), "| Sales:", round(sum(d$Sales), 2), "| Profit:", round(sum(d$Profit), 2), "\n")

## ---------- 1. Statistical analysis ----------
d$disc_group <- factor(d$Discount.Group, levels = c("No Discount", "Low (>0-20%)", "Medium (>20-40%)", "High (>40%)"))
rho <- cor.test(d$Discount, d$Profit, method = "spearman", exact = FALSE)
pear <- cor.test(d$Discount, d$Profit.Margin)
hi <- d$Discount > 0.20
w <- t.test(Profit ~ hi, data = d)                      # Welch t-test: <=20% vs >20%
kw_disc <- kruskal.test(Profit ~ disc_group, data = d)
kw_reg  <- kruskal.test(Profit.Margin ~ Region, data = d)
kw_seg  <- kruskal.test(Profit.Margin ~ Segment, data = d)
kw_cat  <- kruskal.test(Profit.Margin ~ Category, data = d)
stats_out <- data.frame(
  Test = c("Spearman discount vs profit", "Pearson discount vs margin", "Welch t-test profit, discount >20% vs <=20%",
           "Kruskal-Wallis profit by discount group", "Kruskal-Wallis margin by category", "Kruskal-Wallis margin by region", "Kruskal-Wallis margin by segment"),
  Statistic = c(unname(rho$estimate), unname(pear$estimate), unname(w$statistic), unname(kw_disc$statistic), unname(kw_cat$statistic), unname(kw_reg$statistic), unname(kw_seg$statistic)),
  P_value = c(rho$p.value, pear$p.value, w$p.value, kw_disc$p.value, kw_cat$p.value, kw_reg$p.value, kw_seg$p.value))
write.csv(stats_out, "r/r_stat_tests.csv", row.names = FALSE)
print(stats_out, digits = 4)
cat("Mean profit per line: >20% =", round(mean(d$Profit[hi]), 2), " <=20% =", round(mean(d$Profit[!hi]), 2), "\n")

## Factors affecting profit margin: multiple regression (line level, margin capped to [-1,1] to limit outlier leverage)
d$m <- pmax(pmin(d$Profit.Margin, 1), -1)
fit <- lm(m ~ Discount + Category + Region + Segment + Ship.Mode, data = d)
s <- summary(fit)
cat("\nLinear model margin ~ Discount + Category + Region + Segment + Ship.Mode\nR-squared:", round(s$r.squared, 3), " Adj:", round(s$adj.r.squared, 3), "\n")
co <- as.data.frame(s$coefficients); co$term <- rownames(co); write.csv(co, "r/r_margin_regression.csv", row.names = FALSE); print(round(s$coefficients, 4))
fit2 <- lm(m ~ Discount, data = d); cat("R-squared discount alone:", round(summary(fit2)$r.squared, 3), "\n")
an <- anova(fit); an$share_of_explained_SS <- an[["Sum Sq"]] / sum(an[["Sum Sq"]][-nrow(an)]) * 100; print(round(an[, c("Sum Sq", "F value", "share_of_explained_SS")], 2))
write.csv(data.frame(term = rownames(an), an, row.names = NULL), "r/r_margin_anova.csv", row.names = FALSE)

## ---------- 2. Forecasting comparison ----------
ms <- aggregate(Sales ~ format(Order.Date, "%Y-%m"), data = d, FUN = sum); names(ms) <- c("ym", "sales")
y <- ts(ms$sales, start = c(2014, 1), frequency = 12)
mape <- function(a, f) mean(abs((a - f) / a)) * 100; mae <- function(a, f) mean(abs(a - f)); rmse <- function(a, f) sqrt(mean((a - f)^2))
run_fold <- function(train_end, test_year) {
  tr <- window(y, end = train_end); te <- window(y, start = c(test_year, 1), end = c(test_year, 12)); h <- length(te)
  f <- list(
    "Naive (last value)"            = naive(tr, h = h)$mean,
    "Seasonal naive"                = snaive(tr, h = h)$mean,
    "Trend + seasonal regression"   = forecast(tslm(tr ~ trend + season), h = h)$mean,
    "ETS (auto)"                    = forecast(ets(tr), h = h)$mean,
    "ARIMA (auto)"                  = forecast(auto.arima(tr, seasonal = TRUE), h = h)$mean,
    "STL + ETS"                     = tryCatch(forecast(stlf(tr, method = "ets"), h = h)$mean, error = function(e) rep(NA_real_, h)))
  res <- do.call(rbind, lapply(names(f), function(n) data.frame(Model = n, TestYear = test_year, MAE = mae(te, f[[n]]), RMSE = rmse(te, f[[n]]), MAPE = mape(te, f[[n]]))))
  list(res = res, fc = f, te = te)
}
A <- run_fold(c(2015, 12), 2016); B <- run_fold(c(2016, 12), 2017)
res <- rbind(A$res, B$res); write.csv(res, "r/r_forecast_metrics.csv", row.names = FALSE)
cat("\nForecast accuracy:\n"); print(res, digits = 4, row.names = FALSE)
fc17 <- data.frame(month = format(as.Date(paste0(time(B$te) %/% 1, "-", round((time(B$te) %% 1) * 12) + 1, "-01")), "%Y-%m"), actual = as.numeric(B$te)); for (n in names(B$fc)) fc17[[n]] <- as.numeric(B$fc[[n]])
write.csv(fc17, "r/r_forecast_2017.csv", row.names = FALSE)
## Final model: refit best model on all 48 months and forecast 2018 (indicative)
avg <- aggregate(MAPE ~ Model, data = res[!is.na(res$MAPE), ], FUN = mean, na.action = na.omit); avg <- avg[avg$Model %in% names(table(res$Model[!is.na(res$MAPE)])[table(res$Model[!is.na(res$MAPE)]) == 2]), ]; print(avg[order(avg$MAPE), ], row.names = FALSE)
cand <- avg[avg$Model %in% c("Trend + seasonal regression", "ETS (auto)", "ARIMA (auto)", "STL + ETS"), ]; best <- cand$Model[which.min(cand$MAPE)]
cat("Best by average MAPE over both folds:", best, "\n")
fin <- switch(best, "ETS (auto)" = forecast(ets(y), h = 12, level = 80), "ARIMA (auto)" = forecast(auto.arima(y, seasonal = TRUE), h = 12, level = 80),
              "STL + ETS" = stlf(y, method = "ets", h = 12, level = 80), "Trend + seasonal regression" = forecast(tslm(y ~ trend + season), h = 12, level = 80))
out <- data.frame(month = format(seq(as.Date("2018-01-01"), by = "month", length.out = 12), "%Y-%m"), forecast = as.numeric(fin$mean), lo80 = as.numeric(fin$lower), hi80 = as.numeric(fin$upper))
write.csv(out, "r/r_forecast_2018.csv", row.names = FALSE); cat("2018 total forecast:", round(sum(out$forecast)), " vs 2017 actual:", round(sum(window(y, start = c(2017, 1)))), "\n")
writeLines(best, "r/best_model.txt")
