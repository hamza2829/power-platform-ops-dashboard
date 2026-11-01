# Requirements template: new KPI or report

[Wiki home](Home.md)

Copy the blank form into a new issue or document, fill every field, and send it to the data analysis team. Check [KPI definitions](KPI-Definitions.md) first: the measure you need may already exist.

## Blank form

```markdown
### Request: <short title>

**Requested by:** <name, department>    **Date:** <yyyy-mm-dd>

1. Business question
   What decision will this help you make? Write it as one question.

2. Data source
   Which tables/columns? (Orders, Tickets, Customers, Products, Date — or a new source?)
   If new: who owns it, what format, how do we get it?

3. Owner
   Business owner (agrees the definition):
   Data owner (maintains the measure/report):

4. Frequency
   How often must it be updated and looked at? (e.g. monthly review)

5. Definition
   Plain-language definition, including what is excluded and how unknown/missing values are handled.
   Filters/slicers it must respond to:

6. Definition of done
   - [ ] Definition agreed by business owner
   - [ ] Expected value for one known period written down before building
   - [ ] Built and checked against that value
   - [ ] Added to the KPI definitions page (CI check passes)
   - [ ] Requester has seen it in the report
```

## Filled example

This is a **sample request** to show how the form is used. The measure below is **not built** and is not in `dax/measures.dax`.

### Request: High-priority ticket resolution by region

**Requested by:** Service manager, After-sales department  **Date:** 2026-11-01

1. **Business question:** Are High-priority tickets resolved equally fast in every region?
2. **Data source:** Existing model only: `Tickets[priority]`, `Tickets[resolution_days]`, `Customers[region]` (Tickets has a relationship to Customers). No new source.
3. **Owner:** Business owner: After-sales service manager. Data owner: data analysis team.
4. **Frequency:** Monthly service review. The data itself is a fixed snapshot (31 Dec 2025), so it does not refresh on its own.
5. **Definition:** Average calendar days from creation to closure for tickets with priority High, per region. Open tickets and tickets with Unknown status have no duration and are excluded, the same as the existing *Average Ticket Resolution Days*. It must respond to the Date (creation), region and product slicers.
   *Analyst note:* this may need no new measure. Put the existing `[Average Ticket Resolution Days]` on a bar by `Customers[region]` and set the priority slicer to High.
6. **Definition of done:**
   - [ ] Definition agreed by service manager
   - [ ] Expected value written down first: all regions together, full 18 months, High priority = **4.1 days** (4.092308 in [reference_totals.json](../reference_totals.json))
   - [ ] Visual built; with no region selected it still shows 4.1 days
   - [ ] KPI page updated if a new measure was added
   - [ ] Service manager reviewed it
