# Explain the project simply

Read the source, build the report, and reproduce the checks before presenting this as your hands-on Power BI work. Do not say you built or tested the optional app/flow unless you have done so.

## A short walkthrough

"This is a synthetic operations scenario for a furniture manufacturer. I want to show how order demand, delivery reliability and service workload vary by product group and region. The code generates 5,000 orders and 1,500 service tickets over 18 months. It includes deliberately dirty records so the cleaning decisions are visible."

"Orders and tickets are different events at different grains. I use shared customer, product-group and date dimensions so slicers filter both facts. I copy the customer and product keys from an order to its tickets during preparation; I do not connect the two facts directly in the model. Date means booking date for Orders and creation date for Tickets."

"On-time rate includes only deliveries with reliable actual dates and original promises. A target-based estimated promise is useful for display but cannot prove the original commitment was met. Unknown dates remain blank. Revenue here is booked non-cancelled value, not an accounting revenue figure."

"AI helped prepare source code, formulas and instructions. Python tests check reproducibility, foreign keys and data patterns; reference totals support manual Power BI validation. The M and DAX still need to run in Desktop. The optional service app and notification flow are design documents until I implement and test them."

After your own build, replace future-tense statements with the specific steps **you actually did**, describe one error you found or one check you reproduced, and point to your real screenshots. Do not recite AI-written claims of personal experience.

## Questions you should be able to answer

| Question | Plain-language answer |
| --- | --- |
| What is a fact's grain? | What one row represents: one full order or one ticket. Mixing them would double-count order value when orders have several tickets. |
| Why one-to-many relationships? | A customer/group/date describes many events, but its dimension key appears once. Single direction gives one clear filter path. |
| What does CALCULATE do? | It evaluates a measure under changed filters; Total Revenue keeps the current selection while excluding cancelled orders. |
| Why FILTER in Eligible Deliveries? | It inspects each selected order and includes only Delivered rows whose late flag is known. |
| Why not fill every blank date? | It would invent business events and distort lead times and monthly counts. I flag uncertainty rather than guess actuals. |
| Why fewer rows under the full date slicer? | Each fact has one unknown event date. The record remains in the table but cannot belong to a dated period. |
| Can tickets per 100 orders exceed 100? | Yes. It compares creations with bookings in the period. There may be repeat tickets and tickets for older orders; it is not a percentage of orders with complaints. |
| Why is priority not changing revenue? | It is a ticket-only field. A shared dimension filters both facts; a field on Tickets does not filter Orders back through single-direction relationships. |
| Is Open Tickets historical backlog? | No. It is still-open status at the fixed snapshot, grouped/filtered by ticket creation date. |
| What does the rolling measure mean? | Three whole calendar months including the displayed month, divided by three; incomplete initial windows are blank. |
| Why not compare all 2025 with 2024? | 2024 only has July–December. Matched July–December months are the valid YoY demonstration. |
| What would production need? | Real data access and contracts, privacy/security, monitored refresh, business-approved KPI definitions, and tested app/flow deployments. None is claimed here. |

The intentionally worse East delivery rate and September sofa spike are built-in data assumptions. Describe them as a scenario you can detect, not a real-world discovery or proof of causation.
