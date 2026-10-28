// Query name: Tickets. Depends on cleaned Orders, which depends on Products.
let
    Source = Csv.Document(File.Contents(DataFolder & "\service_tickets.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Trimmed = Table.TransformColumns(Headers, List.Transform(Table.ColumnNames(Headers),
        (c) => {c, each if _ = null then "" else Text.Trim(_), type text})),
    Indexed = Table.AddIndexColumn(Trimmed, "source_row", 0, 1, Int64.Type),
    Unique = Table.Distinct(Table.Buffer(Table.Sort(Indexed, {{"source_row", Order.Ascending}})), {"ticket_id"}),
    ValidKeys = Table.SelectRows(Unique, each [ticket_id] <> ""),
    // Preserve this evidence before converting invalid dates to null.
    HasClosure = Table.AddColumn(ValidKeys, "closure_supplied", each [closed_date] <> "", type logical),
    Typed = Table.TransformColumns(HasClosure, {
        {"created_date", each try Date.FromText(_, [Format="yyyy-MM-dd", Culture="en-US"]) otherwise null, type nullable date},
        {"closed_date", each try Date.FromText(_, [Format="yyyy-MM-dd", Culture="en-US"]) otherwise null, type nullable date},
        {"priority", each if List.Contains({"High", "Medium", "Low"}, _) then _ else "Unknown", type text}}),
    ClosureClean = Table.AddColumn(Typed, "closed_clean", each
        if [created_date] <> null and [closed_date] <> null and [closed_date] < [created_date] then null
        else [closed_date], type nullable date),
    RemovedRaw = Table.RemoveColumns(ClosureClean, {"closed_date", "source_row"}),
    Renamed = Table.RenameColumns(RemovedRaw, {{"closed_clean", "closed_date"}}),
    Status = Table.AddColumn(Renamed, "ticket_status", each
        if not [closure_supplied] then "Open" else if [closed_date] = null then "Unknown" else "Closed", type text),
    Resolution = Table.AddColumn(Status, "resolution_days", each
        if [created_date] <> null and [closed_date] <> null
        then Duration.Days([closed_date] - [created_date]) else null, Int64.Type),
    // Carry shared dimension keys into Tickets; do not create a fact-to-fact relationship.
    JoinOrder = Table.NestedJoin(Resolution, {"order_id"}, Orders, {"order_id"}, "order", JoinKind.LeftOuter),
    Dimensions = Table.ExpandTableColumn(JoinOrder, "order", {"customer_id", "product_group"}),
    Quality = Table.AddColumn(Dimensions, "data_quality_issue", each
        [created_date] = null or [ticket_status] = "Unknown" or [priority] = "Unknown"
        or [customer_id] = null or [product_group] = null, type logical),
    Result = Table.RemoveColumns(Quality, {"closure_supplied"})
in
    Result
