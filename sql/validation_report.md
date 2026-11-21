# SQL vs Python validation

| Check                                   |          SQL |       Python | Result   |
|:----------------------------------------|-------------:|-------------:|:---------|
| Total sales                             | 2,297,200.86 | 2,297,200.86 | PASS     |
| Total profit                            |   286,397.02 |   286,397.02 | PASS     |
| Profit margin %                         |        12.47 |        12.47 | PASS     |
| Distinct orders                         |     5,009.00 |     5,009.00 | PASS     |
| Distinct customers                      |       793.00 |       793.00 | PASS     |
| Total quantity                          |    37,873.00 |    37,873.00 | PASS     |
| Average order value                     |       458.61 |       458.61 | PASS     |
| Average shipping days                   |         3.96 |         3.96 | PASS     |
| Average discount                        |         0.16 |         0.16 | PASS     |
| Category sales: Technology              |   836,154.03 |   836,154.03 | PASS     |
| Category profit: Technology             |   145,454.95 |   145,454.95 | PASS     |
| Category sales: Furniture               |   741,999.80 |   741,999.80 | PASS     |
| Category profit: Furniture              |    18,451.27 |    18,451.27 | PASS     |
| Category sales: Office Supplies         |   719,047.03 |   719,047.03 | PASS     |
| Category profit: Office Supplies        |   122,490.80 |   122,490.80 | PASS     |
| Region profit: West                     |   108,418.45 |   108,418.45 | PASS     |
| Region sales: West                      |   725,457.82 |   725,457.82 | PASS     |
| Region profit: East                     |    91,522.78 |    91,522.78 | PASS     |
| Region sales: East                      |   678,781.24 |   678,781.24 | PASS     |
| Region profit: South                    |    46,749.43 |    46,749.43 | PASS     |
| Region sales: South                     |   391,721.91 |   391,721.91 | PASS     |
| Region profit: Central                  |    39,706.36 |    39,706.36 | PASS     |
| Region sales: Central                   |   501,239.89 |   501,239.89 | PASS     |
| Segment sales: Consumer                 | 1,161,401.34 | 1,161,401.34 | PASS     |
| Segment orders: Consumer                |     2,586.00 |     2,586.00 | PASS     |
| Segment sales: Corporate                |   706,146.37 |   706,146.37 | PASS     |
| Segment orders: Corporate               |     1,514.00 |     1,514.00 | PASS     |
| Segment sales: Home Office              |   429,653.15 |   429,653.15 | PASS     |
| Segment orders: Home Office             |       909.00 |       909.00 | PASS     |
| Loss-making products (by Product ID)    |       299.00 |       299.00 | PASS     |
| Profit lost on loss-making products     |   -76,721.13 |   -76,721.13 | PASS     |
| Discount band profit: No discount       |   320,987.60 |   320,987.60 | PASS     |
| Discount band lines: No discount        |     4,798.00 |     4,798.00 | PASS     |
| Discount band profit: 1-10%             |     9,029.18 |     9,029.18 | PASS     |
| Discount band lines: 1-10%              |        94.00 |        94.00 | PASS     |
| Discount band profit: 11-20%            |    91,756.30 |    91,756.30 | PASS     |
| Discount band lines: 11-20%             |     3,709.00 |     3,709.00 | PASS     |
| Discount band profit: 21-30%            |   -10,369.28 |   -10,369.28 | PASS     |
| Discount band lines: 21-30%             |       227.00 |       227.00 | PASS     |
| Discount band profit: 31-50%            |   -48,447.73 |   -48,447.73 | PASS     |
| Discount band lines: 31-50%             |       310.00 |       310.00 | PASS     |
| Discount band profit: >50%              |   -76,559.05 |   -76,559.05 | PASS     |
| Discount band lines: >50%               |       856.00 |       856.00 | PASS     |
| Discount group profit: No Discount      |   320,987.60 |   320,987.60 | PASS     |
| Discount group lines: No Discount       |     4,798.00 |     4,798.00 | PASS     |
| Discount group profit: Low (>0-20%)     |   100,785.47 |   100,785.47 | PASS     |
| Discount group lines: Low (>0-20%)      |     3,803.00 |     3,803.00 | PASS     |
| Discount group profit: Medium (>20-40%) |   -35,817.47 |   -35,817.47 | PASS     |
| Discount group lines: Medium (>20-40%)  |       460.00 |       460.00 | PASS     |
| Discount group profit: High (>40%)      |   -99,558.59 |   -99,558.59 | PASS     |
| Discount group lines: High (>40%)       |       933.00 |       933.00 | PASS     |
| Months in monthly query                 |        48.00 |        48.00 | PASS     |
| Sum of monthly sales                    | 2,297,200.87 | 2,297,200.86 | PASS     |
| Year 2014 sales                         |   484,247.50 |   484,247.50 | PASS     |
| Year 2015 sales                         |   470,532.51 |   470,532.51 | PASS     |
| Year 2016 sales                         |   609,205.60 |   609,205.60 | PASS     |
| Year 2017 sales                         |   733,215.26 |   733,215.26 | PASS     |
| Top customer sales                      |    25,043.05 |    25,043.05 | PASS     |
| 10th customer sales                     |    12,129.07 |    12,129.07 | PASS     |
| Loss-making states                      |        10.00 |        10.00 | PASS     |
| Customers with loss                     |       155.00 |       155.00 | PASS     |
| Order_lines vs flat sales diff          |         0.00 |         0.00 | PASS     |

**62 of 62 checks passed.**
