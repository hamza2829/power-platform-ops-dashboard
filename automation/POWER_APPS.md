# Optional canvas app: service ticket intake

**Design and formulas only; not built, executed, exported or tested.** Use a blank tablet canvas app with **classic controls** and the lists in [SHAREPOINT_SCHEMA.md](SHAREPOINT_SCHEMA.md). Add data sources named `ServiceTickets` and `OrdersReference`. Keep formula-level error management enabled. Formulas use English authoring separators (commas for arguments, semicolons for action chains); some locales require semicolons/double semicolons instead. No `.msapp` or tenant setup is provided.

## Screen and form

Create a screen `scrTickets` with an Edit form `frmTicket`, Save button `btnSave`, priority filter dropdown `ddPriorityFilter`, open-ticket gallery `galOpen`, and refresh button `btnRefresh`. Set these properties:

```powerfx
// scrTickets.OnVisible
NewForm(frmTicket)

// frmTicket.DataSource
ServiceTickets

// frmTicket.Item
Defaults(ServiceTickets)

// frmTicket.DefaultMode
FormMode.New
```

Add the following form fields, **unlock the data cards**, and name their classic child controls as shown. Leave their `DataField` binding as the actual SharePoint internal name. Set each visible card's Required = true. Keep the standard card error label bound to `Parent.Error`.

| Card field | Child control / relevant property | Card Update formula |
| --- | --- | --- |
| Title | Text input `txtTitle`; Default = `Parent.Default` | `Trim(txtTitle.Text)` |
| OrderId | Text input `txtOrderId`; Default = `Parent.Default` | `Trim(txtOrderId.Text)` |
| CreatedDate | Date picker `dtCreated`; DefaultDate = `Today()` | `dtCreated.SelectedDate` |
| Category | Dropdown `ddCategory`; Items below; Default = `"Damage"` | `ddCategory.Selected.Value` |
| Priority | Dropdown `ddPriority`; Items below; Default = `"Medium"` | `ddPriority.Selected.Value` |
| TicketStatus | Hidden card; Visible = `false` | `"Open"` |
| ClosedDate | Hidden card; Visible = `false` | `Blank()` |

```powerfx
// ddCategory.Items (display column Value)
["Damage", "Missing parts", "Assembly", "Warranty"]

// ddPriority.Items (display column Value)
["High", "Medium", "Low"]

// btnSave.DisplayMode
If(frmTicket.Valid, DisplayMode.Edit, DisplayMode.Disabled)

// btnSave.OnSelect: validate trimmed required fields, existing order and dates.
// Equality on the indexed OrderId is intended to delegate to SharePoint.
Set(varOrder, LookUp(OrdersReference, OrderId = Trim(txtOrderId.Text)));
If(
    IsBlank(Trim(txtTitle.Text)) || IsBlank(Trim(txtOrderId.Text)) ||
        IsBlank(dtCreated.SelectedDate) || IsBlank(ddCategory.Selected.Value) ||
        IsBlank(ddPriority.Selected.Value) || !frmTicket.Valid,
    Notify("Complete all required fields.", NotificationType.Error),
    IsBlank(varOrder.ID),
    Notify("Enter a known order ID from the test order list.", NotificationType.Error),
    IsBlank(varOrder.OrderDate),
    Notify("This order has no valid order date; ask the data owner to review it.", NotificationType.Error),
    dtCreated.SelectedDate < varOrder.OrderDate || dtCreated.SelectedDate > Today(),
    Notify("Ticket date must be on or after the order date and not in the future.", NotificationType.Error),
    SubmitForm(frmTicket)
)

// frmTicket.OnSuccess: success belongs here because SubmitForm is asynchronous.
Notify("Ticket created: " & Text(frmTicket.LastSubmit.ID), NotificationType.Success);
ResetForm(frmTicket);
NewForm(frmTicket);
Refresh(ServiceTickets)

// frmTicket.OnFailure: do not reset the user's input after failure.
Notify("Ticket was not saved. " & frmTicket.Error, NotificationType.Error)
```

No custom ID is generated: SharePoint assigns its built-in ID. CreatedDate is a date-only business field, while SharePoint Created is the system timestamp. The date check is against the order date; it does not claim to validate delivery. This app is a live-date design using Today(), separate from the historical CSV snapshot.

## Open-ticket gallery and status update

```powerfx
// ddPriorityFilter.Items (display column Value)
["All", "High", "Medium", "Low"]

// ddPriorityFilter.Default
"All"

// galOpen.Items: branch first, then send a simple text equality filter to SharePoint.
If(
    ddPriorityFilter.Selected.Value = "All",
    Filter(ServiceTickets, TicketStatus = "Open"),
    Filter(ServiceTickets,
        TicketStatus = "Open" && Priority = ddPriorityFilter.Selected.Value)
)

// Gallery title label.Text
"#" & Text(ThisItem.ID) & " | " & ThisItem.OrderId

// Gallery subtitle label.Text
ThisItem.Title & " | " & ThisItem.Priority & " | " &
    Text(ThisItem.CreatedDate, "yyyy-mm-dd")

// btnClose is INSIDE the gallery template. btnClose.Text
"Mark closed"

// btnClose.OnSelect: all IfError result branches return a Boolean.
// Refresh only on success, so a failed write cannot look like a successful close.
IfError(
    Patch(ServiceTickets, ThisItem,
        {TicketStatus: "Closed", ClosedDate: Today()}).ID > 0,
    Notify("Could not close ticket. " & FirstError.Message, NotificationType.Error); false,
    Notify("Ticket closed.", NotificationType.Success);
    Refresh(ServiceTickets); true
)

// btnRefresh.OnSelect
Refresh(ServiceTickets);
Refresh(OrdersReference)

// Optional App.OnError: catches errors not handled by a form or IfError.
Notify("Unexpected error. " & FirstError.Message, NotificationType.Error)
```

Use Gallery fields bound to **ThisItem**, not Gallery.Selected inside each row. Closing removes a ticket from the open gallery after refresh. This is a simple two-state demo; reopening and multiuser conflict handling are future work. Text equality filters are chosen for delegation; check Studio's delegation warnings against your actual SharePoint schema. Do not replace this with a `ClearCollect` of all tickets, which can silently truncate large lists.

Manual test checklist:

- Blank/space-only summary or order ID, missing date: validation blocks save.
- Unknown order ID, future date, date before order: useful error; no row created.
- Valid High ticket: one row with Open and blank ClosedDate; test flow sends to your mailbox if separately built.
- Gallery filter All/High/Medium/Low narrows open rows correctly; Mark closed sets ClosedDate and removes the row.
- Revoke write permission in a test account: OnFailure/IfError reports failure and does not announce success; restore permissions.
- Inspect delegation warnings and test against more rows than the app's nondelegation limit before calling this scalable.

References: [forms and SubmitForm](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-form), [Patch](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-patch), [IfError](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-iferror), [error handling](https://learn.microsoft.com/en-us/power-platform/power-fx/error-handling), [SharePoint delegation](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-sharepoint-online#power-apps-delegable-functions-and-operations-for-sharepoint).
