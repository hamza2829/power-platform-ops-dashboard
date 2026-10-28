// Query name: Orders. Depends on Products. ISO dates and dot decimals are explicit.
let
    Source = Csv.Document(File.Contents(DataFolder & "\orders.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Trimmed = Table.TransformColumns(Headers, List.Transform(Table.ColumnNames(Headers),
        (c) => {c, each if _ = null then "" else Text.Trim(_), type text})),
    Indexed = Table.AddIndexColumn(Trimmed, "source_row", 0, 1, Int64.Type),
    Unique = Table.Distinct(Table.Buffer(Table.Sort(Indexed, {{"source_row", Order.Ascending}})), {"order_id"}),
    ValidKeys = Table.SelectRows(Unique, each [order_id] <> ""),
    Typed = Table.TransformColumns(ValidKeys, {
        {"order_date", each try Date.FromText(_, [Format="yyyy-MM-dd", Culture="en-US"]) otherwise null, type nullable date},
        {"promised_date", each try Date.FromText(_, [Format="yyyy-MM-dd", Culture="en-US"]) otherwise null, type nullable date},
        {"delivered_date", each try Date.FromText(_, [Format="yyyy-MM-dd", Culture="en-US"]) otherwise null, type nullable date},
        {"order_value", each try Number.FromText(_, "en-US") otherwise null, type nullable number}}),
    MoneyType = Table.TransformColumnTypes(Typed, {{"order_value", Currency.Type}}),
    JoinTarget = Table.NestedJoin(MoneyType, {"product_group"}, Products, {"product_group"}, "product", JoinKind.LeftOuter),
    Target = Table.ExpandTableColumn(JoinTarget, "product", {"target_lead_time_days"}),
    // A missing/illogical promise is estimated only when the order date and target exist.
    PromiseImputed = Table.AddColumn(Target, "promise_imputed", each
        ([promised_date] = null or ([order_date] <> null and [promised_date] < [order_date]))
        and [order_date] <> null and [target_lead_time_days] <> null, type logical),
    PromiseClean = Table.AddColumn(PromiseImputed, "promised_clean", each
        if [promise_imputed] then Date.AddDays([order_date], [target_lead_time_days])
        else if [order_date] <> null and [promised_date] <> null and [promised_date] < [order_date] then null
        else [promised_date], type nullable date),
    // Unknown actual dates remain unknown. A delivered status is not a delivery date.
    DeliveryClean = Table.AddColumn(PromiseClean, "delivered_clean", each
        if [status] <> "Delivered" then null
        else if [order_date] <> null and [delivered_date] <> null and [delivered_date] < [order_date] then null
        else [delivered_date], type nullable date),
    RemovedRaw = Table.RemoveColumns(DeliveryClean, {"promised_date", "delivered_date", "source_row"}),
    Renamed = Table.RenameColumns(RemovedRaw, {{"promised_clean", "promised_date"}, {"delivered_clean", "delivered_date"}}),
    Quality = Table.AddColumn(Renamed, "data_quality_issue", each
        [order_date] = null or [order_value] = null or [promised_date] = null or [promise_imputed]
        or ([status] = "Delivered" and [delivered_date] = null), type logical),
    LeadTime = Table.AddColumn(Quality, "lead_time_days", each
        if [status] = "Delivered" and [order_date] <> null and [delivered_date] <> null
        then Duration.Days([delivered_date] - [order_date]) else null, Int64.Type),
    // Null means not assessable, not on time. Imputed promises cannot prove punctuality.
    LateFlag = Table.AddColumn(LeadTime, "late_flag", each
        if [status] = "Delivered" and [delivered_date] <> null and [promised_date] <> null and not [promise_imputed]
        then [delivered_date] > [promised_date] else null, type nullable logical)
in
    LateFlag
