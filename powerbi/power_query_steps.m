// =====================================================================================
// POWER QUERY (M) — one query per CSV. Home > Transform data > New Source > Blank Query > Advanced Editor.
// 1) Create a Parameter first: Manage Parameters > New: Name = DataFolder, Type = Text,
//    Current Value = full path to the folder data\processed\powerbi\  (end with a backslash)
// 2) Paste each query below and name it exactly as shown (Fact_Sales, Dim_Date, ...).
// Why Power Query? It records every transformation step (applied steps) so the refresh is repeatable.
// =====================================================================================

// ----- Fact_Sales ------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "Fact_Sales.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"Row ID", Int64.Type}, {"Order ID", type text}, {"Order Date", type date}, {"Ship Date", type date},
        {"Ship Mode", type text}, {"Customer ID", type text}, {"Product ID", type text}, {"Geography ID", Int64.Type},
        {"Sales", type number}, {"Quantity", Int64.Type}, {"Discount", type number}, {"Profit", type number},
        {"Shipping Days", Int64.Type}, {"Discount Band", type text}, {"Is Loss", Int64.Type}, {"Possible Duplicate", Int64.Type}},
        "en-US"),                                   // culture en-US so "261.96" is read as a decimal, not text
    NoNulls = Table.SelectRows(Typed, each [Row ID] <> null and [Sales] <> null)   // safety filter (no rows are removed today)
in
    NoNulls

// ----- Dim_Date ---------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "Dim_Date.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {{"Date", type date}, {"Year", Int64.Type}, {"Quarter", type text}, {"Month Number", Int64.Type},
        {"Month Name", type text}, {"Year-Month", type text}, {"Month Start", type date}, {"Weekday", type text}, {"Weekday Number", Int64.Type}}, "en-US")
in
    Typed

// ----- Dim_Product ------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "Dim_Product.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {{"Product ID", type text}, {"Product Name", type text}, {"Category", type text}, {"Sub-Category", type text}})
in
    Typed

// ----- Dim_Customer -----------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "Dim_Customer.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {{"Customer ID", type text}, {"Customer Name", type text}, {"Segment", type text}})
in
    Typed

// ----- Dim_Geography ----------------------------------------------------------------
// IMPORTANT: Postal Code must be TEXT, otherwise Power Query drops the leading zero (05408 -> 5408)
let
    Source = Csv.Document(File.Contents(DataFolder & "Dim_Geography.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {{"Geography ID", Int64.Type}, {"Country", type text}, {"Region", type text},
        {"State", type text}, {"City", type text}, {"Postal Code", type text}})
in
    Typed

// ----- Dim_DiscountBand -------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolder & "Dim_DiscountBand.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {{"Discount Band", type text}, {"Band Order", Int64.Type}})
in
    Typed

// ----- Data checks to run in Power Query after loading (View > Column quality / Column profile) -----
// Fact_Sales: 9,994 rows, 0 errors, 0 empty.  Dim_Product 1,862 | Dim_Customer 793 | Dim_Geography 632 | Dim_Date 1,461 | Dim_DiscountBand 6
