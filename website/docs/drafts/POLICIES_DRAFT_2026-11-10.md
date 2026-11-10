# Delivery & Returns and policies: draft for Sabry's approval

Draft, 10 Nov 2026. Not on the store. English only; Arabic goes to the translator after approval.
Built only from Sabry's answers of 10 Nov (CONTENT_TO_SUPPLY sections 1, 5, 6). Lines marked **[confirm]** need a yes or a fix. **[legal]** marks points for a lawyer's check before launch.

---

## 1. Page: Delivery & Returns (`/pages/delivery-returns`)

### Ready to deliver
Paid in full at checkout. Delivered in 3–5 business days.

### Made to order
Made for you after you order. Each product page shows its lead time: 7–14 days or 30–45 days, counted from the day we confirm your deposit. **[confirm: counted from deposit confirmation]**

- **Deposit.** 50% at order, by card through checkout or by InstaPay to 01000411116. If you pay by InstaPay, send a screenshot of the receipt on WhatsApp with your order number. Production starts once the deposit is confirmed. **[confirm]**
- **Balance.** The remaining 50% is paid on delivery, in cash or by InstaPay.
- The deposit is non-refundable. **[legal]**

### Delivery
We deliver within Egypt. Standard delivery is 118 EGP per order. We contact you on WhatsApp to arrange the day. **[confirm]**

### Returns
- **Ready pieces.** Returnable within 48 hours of delivery, unused. Return delivery is paid by you. **[legal: see note]** Refunds are made by the same method you paid with, within **[confirm: number of days]** of receiving the piece back.
- **Made-to-order pieces.** Not returnable, except for damage or a defect.

### Damage
If a piece arrives damaged, tell us within 48 hours of delivery on WhatsApp, with photos. You choose what happens next: repair, replacement or refund.

### Contact
WhatsApp +20 100 082 2240.
Samples of our work are on view in our showroom in New Cairo, by appointment.

---

## 2. Shopify policy: Shipping policy
Same text as "Ready to deliver", "Made to order" (lead times only) and "Delivery" above.

## 3. Shopify policy: Refund policy
Same text as "Made to order" (deposit lines), "Returns" and "Damage" above.

## 4. Shopify policy: Terms of service (short) **[legal: full review]**
1. **Who we are.** This store is run by objekt, New Cairo, Egypt. Contact: WhatsApp +20 100 082 2240.
2. **Prices.** In Egyptian pounds (EGP), including 14% VAT. Delivery is added at checkout.
3. **Orders.** An order is confirmed when payment (ready pieces) or the deposit (made-to-order pieces) is received.
4. **Made to order.** Pieces are made for you after your order. Lead times are shown on each product page. Colours and finishes of handmade pieces may vary slightly from images.
5. **Payment, delivery, returns.** As set out on the Delivery & Returns page and in the Shipping and Refund policies.
6. **Images.** Some product images are computer renders, not photographs. **[confirm: needed while AI renders are on the site]**
7. **Law.** These terms are governed by the laws of Egypt. **[legal]**

## 5. Shopify policy: Contact information (new)
objekt
ElBanafseg 2, Unit 28, Apt. 1, Ground Floor, New Cairo, Egypt (showroom, by appointment)
WhatsApp +20 100 082 2240

## 6. Privacy policy: contact fix only
The Shopify-generated policy (30 Oct) stays as is, except its last paragraph:

> Now: "…please email us at amr@xdough.com. You can find our other contact details on our contact information policy."
>
> New: "…please contact us on WhatsApp at +20 100 082 2240. You can find our other contact details on our contact information policy."

---

## Legal note
As far as we know, Egypt's Consumer Protection Law (No. 181 of 2018) gives buyers a 14-day return right, with exceptions such as goods made to the buyer's specification. The 48-hour window for ready pieces and the non-refundable deposit may conflict with it. Not verified: a lawyer should check before 19 Nov.

## After approval (store writes, each needs Sabry's yes)
- Create page Delivery & Returns; add it to the `footer` (Support) menu.
- Set Shipping, Refund, Terms of service and Contact information policies; fix the privacy contact. Add them to `footer-policies`.
- Product lead time: a per-item choice (7–14 days / 30–45 days) set when listing, shown in days. Needs a metafield and a change to `snippets/availability.liquid` (now in weeks).
