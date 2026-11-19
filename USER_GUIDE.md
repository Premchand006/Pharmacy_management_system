# User guide

How to do the everyday jobs at the counter. Staff sign in at `/login`,
customers at `/portal/login`.

## First-time setup (admin)

1. **Settings**: enter the pharmacy name, address, phone, GSTIN and drug
   licence numbers (Form 20, Form 21, and Form 20F if you stock Schedule X
   drugs). Set the invoice prefix. Tick the composition scheme box only if
   you are registered under it.
2. **Staff**: add each person. Give a username and password to anyone who
   will use the system. Enter the pharmacist registration number for
   registered pharmacists; only they can be recorded as the dispensing
   pharmacist on prescription sales. Choose **Admin** access only for
   people who should manage staff and settings.
3. **Suppliers**: add each distributor with their wholesale drug licence
   number and its validity date.
4. **Products**: add what you sell with the correct schedule, HSN code,
   GST rate, MRP and reorder level. Scan the barcode into the barcode field
   so the counter can find it by scanning.

## Receiving stock

**Stock → Purchases → Receive stock.** Choose the supplier, enter their
invoice number and date, then one line per batch: product, batch number,
expiry, quantity, cost per pack and the MRP printed on the pack. Saving
adds the batches to stock.

## Making a bill

1. **New bill.** Scan or type the medicine name and press Enter. Repeat for
   each item and change quantities in the list.
2. Optionally pick the customer by phone number or name. Their name and
   address fill the prescription fields.
3. If any item is Schedule H, H1, X or NDPS, the **Prescription details**
   box appears. Fill in the patient's and doctor's names, addresses and the
   doctor's registration number, and choose the dispensing pharmacist. If
   the customer sent the prescription through the portal, type its number
   instead and the doctor's details are filled in for you.
4. Choose the payment mode, add a discount if any, and press
   **Save and print**. The print dialog opens; choose A5 or 80 mm.

The bill is refused, with the reason shown, if stock is short, a batch has
expired, prescription details are missing, or a prescription has already
been dispensed as many times as the doctor allowed.

### Cancelling a bill

Open the invoice, type the reason and press **Void**. The stock goes back
into its batches and the invoice stays on record marked VOID. Counter
staff can void only today's bills; older ones need an admin.

## Expired and damaged stock

**Stock → Batches**, filter **Expired, still on shelf**. For each batch
enter the quantity, choose the reason and press **Remove**. The dashboard
shows how many expired batches are still counted as stock.

## Registers and returns

- **Drug registers**: choose the schedule and dates. Print it or download
  the CSV. The H1 register must be kept for three years.
- **Schedule X register**: one page per drug with every receipt, supply and
  the running balance.
- **Purchase register**: everything bought, with supplier licence, batch
  and manufacturer.
- **GST returns**: choose the month. The B2C, HSN, B2B and documents-issued
  tables match the GSTR-1 sections; the CSV buttons give files your
  accountant can use.
- **Trace a batch** (under Stock & sales): enter a batch number to see who
  supplied it and every bill it went out on. Use it for a recall.

## Customers

Add a customer with name and phone; the address is only needed when they
buy prescription drugs. To let them use the portal, set a portal password
and tell them their customer ID.

If a customer asks for their data to be deleted, an admin presses **Erase
profile** in the customer list. Their contact details and login are
removed. Past invoices and register entries keep the name and address
copied at the time of sale, because the Drugs Rules and GST law require
those records to be kept.

## For customers

Sign in with the customer ID on your bill and the password the pharmacy
gave you. You can see your prescriptions and bills, and **Send a
prescription** before you visit. Bring the original prescription when you
collect the medicines.

## Troubleshooting

- **"Too many failed attempts"**: wait 15 minutes. An admin can set a new
  password from the Staff page.
- **"Form expired"**: you were signed out after an hour of inactivity.
  Reload the page and sign in again.
- **A product does not appear at the counter**: it has no unexpired stock,
  or it has been discontinued on the Products page.
- **Invoice shows no GSTIN or licence**: fill them in under Settings.
