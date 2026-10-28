// Query name: Products. Targets are calendar days, not working days.
let
    Source = Csv.Document(File.Contents(DataFolder & "\products.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TextTypes = Table.TransformColumnTypes(Headers,
        {{"product_group", type text}, {"target_lead_time_days", type text}}),
    Trimmed = Table.TransformColumns(TextTypes, {
        {"product_group", each if _ = null then "" else Text.Trim(_), type text}}),
    Indexed = Table.AddIndexColumn(Trimmed, "source_row", 0, 1, Int64.Type),
    Unique = Table.Distinct(Table.Buffer(Table.Sort(Indexed, {{"source_row", Order.Ascending}})), {"product_group"}),
    ValidKeys = Table.SelectRows(Unique, each [product_group] <> ""),
    Typed = Table.TransformColumns(ValidKeys, {{"target_lead_time_days", each
        try (let n = Number.FromText(_, "en-US")
             in if n > 0 and Number.RoundDown(n) = n then Int64.From(n) else null)
        otherwise null, Int64.Type}}),
    Result = Table.RemoveColumns(Typed, {"source_row"})
in
    Result
