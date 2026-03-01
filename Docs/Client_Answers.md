# Client Answers & Business Rules

This document summarizes answers received from the Hungry Hub client regarding data definitions, business rules, and constraints that govern the data pipeline.

---

## 1. Outlier Restaurant Exclusion

**Client Answer:** *"Please always ignore Copper Beyond Buffet in your metrics as it's an outlier."*

**Restaurant IDs to exclude:** `4503`, `4502`, `933`, `837`

**Implementation:** Hardcoded exclusion filter applied in `01_Data_Cleaning.ipynb`.

---

## 2. Strict GMV (Revenue) Calculation Logic

**Client Answer:** GMV & Revenue calculations must apply these filters:

| Filter | Value |
|--------|-------|
| `active` | TRUE |
| `no_show` | 0 |
| `revenue` | > 0 |
| `is_temporary` | 0 |
| `for_locking_system` | 0 |
| `channel` | ≠ 5 |
| `ack` | TRUE |

**Additional:** Revenue in the raw data is stored in *cents* and must be divided by 100 for local currency (Thai Baht).

**Implementation:** These filters are applied during data cleaning before any revenue or booking aggregation.

---

## 3. Temporary & Invalid Bookings

**Client Answer:**
- When `start_time` & `end_time` match → "temporary booking to lock seats"
- Only `is_valid_reservation = true` bookings should be counted
- `is_temporary = TRUE` → booking is not yet paid
- `for_locking_system` distinguishes between held bookings and confirmed reservations
- `ack = False` + `arrived = True` + `no_show = False` → booking still needs confirmation

**Implementation:** Success metrics (`total_bookings`, `no_show_rate`, conversion rates) are calculated after filtering for valid, confirmed reservations only.

---

## 4. Payment Methods

**Client Answer:**
- True Wallet and ShopeePay are no longer used
- If all payment methods are `FALSE`, the user likely paid on site
- `revenue = NULL` usually means the user booked without a package and will pay on site

**Implementation:** Rows with `revenue = NULL` are not dropped (they represent valid bookings) but do not contribute to calculated GMV.

---

## 5. Booking Edits vs. True Cancellations

**Client Answer:** When a booking is edited, a new row is created and the old row's status is changed to "canceled". The link is through `old_reservation_id` and `new_reservation_id`.

**Implementation:** `cancel_rate` calculations distinguish between true cancellations and edits to avoid overstating lost business.

---

## 6. Marketing Attribution Limitations

**Client Answer:** *"You cannot know which CRM / Facebook / KOL activity corresponds to which Media Pack campaign in a measurable way. What you have instead is timing-based correlation."*

**Implementation:** No deterministic features linking specific ad clicks to campaign purchases. The pipeline uses temporal overlap and aggregate KOL engagement metrics instead.
