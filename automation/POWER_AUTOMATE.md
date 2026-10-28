# Optional high-priority ticket notification flow

**Design only; not built or tested.** Use the [SharePoint contract](SHAREPOINT_SCHEMA.md). Choose an automated cloud flow. Rename actions exactly as below before entering expressions. Expressions in the Expression editor omit the leading `@`; trigger conditions in Settings include it. Use your **own test mailbox** initially. No credentials or real recipients are stored here.

| Order / action | Configuration and purpose |
| --- | --- |
| 1. SharePoint — When an item is created | Site: your test site; List: ServiceTickets. This triggers once on creation, not subsequent status edits. |
| 2. Scope `Try_Notify_and_Log` | Container for notification and success logging. Default sequential run-after on success. |
| 2a. Compose `RunId` | Expression: `workflow()?['run']?['name']` to correlate the log with run history. |
| 2b. Compose `Subject` | `concat('[HIGH] Ticket ', string(triggerBody()?['ID']), ' | Order ', coalesce(triggerBody()?['OrderId'], 'Unknown'))` |
| 2c. Office 365 Outlook — Send an email (V2), `Send_Email` | To: explicitly chosen service/test mailbox. Subject: `outputs('Subject')`. Body: dynamic fields ID, Title, OrderId, Category, Priority, CreatedDate and Link to item. Use the connector's dynamic content picker for Link to item. |
| 2d. SharePoint — Create item, `Log_Sent` | List ServiceNotificationLog. Title `concat(outputs('RunId'), ':Sent')`; TicketId `triggerBody()?['ID']`; RunId `outputs('RunId')`; Outcome `Sent`; LoggedAt `utcNow()`; Detail `Notification accepted by email connector`. This is evidence of connector acceptance, not inbox delivery. |
| 3. Scope `Catch_Failure` | Configure run after Try_Notify_and_Log **has failed** and **has timed out**, uncheck successful/skipped. |
| 3a. Compose `FailureDetail` | `string(result('Try_Notify_and_Log'))` gives action results for diagnosis. Inspect run history for the exact failing action. Avoid sensitive content in a real deployment. |
| 3b. SharePoint — Create item, `Log_Failed` | Same log list. Title `concat(workflow()?['run']?['name'], ':Failed')`; TicketId `triggerBody()?['ID']`; RunId `workflow()?['run']?['name']`; Outcome `Failed`; LoggedAt `utcNow()`; Detail `outputs('FailureDetail')`. It does not depend on a Compose that may have failed inside Try. |
| 4. Terminate `Terminate_Failed` (outside scopes) | Run after Catch_Failure is **successful, failed, or timed out**, **not skipped**. Status Failed, code `TICKET_NOTIFICATION_FAILED`, message `Notification or logging failed; inspect run history and log.` If failure logging also fails, the overall run still fails visibly. |

Trigger > Settings > Trigger conditions:

```text
@equals(triggerBody()?['Priority'], 'High')
```

Priority is **plain text** in this design. If you choose a SharePoint Choice column instead, inspect the trigger body and use the actual choice value path (often Priority/Value); the app formulas also need Choice records. Do not mix those schemas.

Example email body using dynamic fields (the designer lets you insert each token):

```text
A high-priority service ticket needs review.
Ticket: <ID> | Order: <OrderId>
Category: <Category> | Business date: <CreatedDate>
Summary: <Title>
Open ticket: <Link to item>
```

Use normal connector retry policies for transient failures and record their settings when you build. If email succeeds but logging fails, the catch path runs; replaying the run can send a second email. Trigger redelivery and retries can also duplicate sends. This small design is **best effort**, not exactly once. RunId helps investigate duplicates; a production outbox/deduplication design would be separate work. No automatic infinite retry loop or self-updating ticket trigger is used.

Teams alternative: replace Send_Email with Microsoft Teams **Post message in a chat or channel**; select your test team/channel and include the same ticket fields and link. Keep success logging after that action and test Teams permissions yourself. Do not send both channels unless you intentionally want two notifications.

Manual smoke tests before marking it built:

1. Create a High ticket in the test list: one flow run, test notification received, a Sent log row with matching TicketId/RunId.
2. Create Medium and Low tickets: trigger condition prevents notification runs. Change an existing ticket to High: the creation-only trigger does not run again.
3. In a disposable copy of the flow, deliberately make Log_Sent target a nonexistent test list. Create a High ticket: email may already have sent, Catch runs, a Failed log is attempted and the flow ends Failed. Restore the list; don't blindly replay to the team mailbox.
4. In that disposable copy, also break Log_Failed: Terminate_Failed still marks the run Failed. Inspect run history because the log store is unavailable. Delete test changes, save evidence, and restore all settings.

References: [SharePoint triggers](https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/sharepoint-connector-actions-triggers), [scopes](https://learn.microsoft.com/en-us/power-automate/scopes), [run-after and error handling](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/error-handling).
