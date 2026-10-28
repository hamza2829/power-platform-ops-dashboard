// Query name: Customers. Create the text parameter DataFolder first.
let
    Source = Csv.Document(File.Contents(DataFolder & "\customers.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers,
        {{"customer_id", type text}, {"region", type text}, {"segment", type text}}),
    Trimmed = Table.TransformColumns(Typed, List.Transform(Table.ColumnNames(Typed),
        (c) => {c, each if _ = null then "" else Text.Trim(_), type text})),
    // Buffer the original row order so the first occurrence wins, including conflicts.
    Indexed = Table.AddIndexColumn(Trimmed, "source_row", 0, 1, Int64.Type),
    Unique = Table.Distinct(Table.Buffer(Table.Sort(Indexed, {{"source_row", Order.Ascending}})), {"customer_id"}),
    ValidKeys = Table.SelectRows(Unique, each [customer_id] <> ""),
    Filled = Table.TransformColumns(ValidKeys, {
        {"region", each if _ = "" then "Unknown" else _, type text},
        {"segment", each if _ = "" then "Unknown" else _, type text}}),
    Result = Table.RemoveColumns(Filled, {"source_row"})
in
    Result
