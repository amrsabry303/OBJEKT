---
name: paymob-shopify
description: Connect Paymob Accept (Egypt) to a Shopify store so customers can pay by card, Apple Pay, mobile wallet, kiosk or BNPL (valU, Sympl, Souhoola). Use when someone asks to add Paymob to Shopify, set up Paymob on a Shopify checkout, move a Shopify store from test to live Paymob payments, or troubleshoot Paymob payments that don't arrive in Shopify.
---

# Paymob Accept on a Shopify store

This is a no-code integration. Paymob publishes official Shopify payment apps, so nobody writes a gateway. The work is configuration in two places: the Paymob dashboard and the Shopify admin. Do not build a custom checkout, a theme hack, or a "pay by link" workaround when the official app fits.

Sources (re-check them before each setup; Paymob changes these flows):
- https://developers.paymob.com/paymob-docs/integration-paths/plugins/shopify (current guide)
- https://docs.paymob.com/docs/shopify-v2 (older Egypt guide)
- https://apps.shopify.com/paymob-accept-card-alpha (the Card app's App Store listing)

## 0. Before you start: what you need from the merchant

Ask for these. Never ask them to paste a password, API key or HMAC secret into the chat: they type those into Paymob or Shopify themselves.

- [ ] An **active Paymob merchant account** (Egypt portal: https://accept.paymob.com). A new account is in **test mode** until Paymob approves it, which needs company KYC and a signed agreement.
- [ ] **Shopify admin access** with permission to change payment settings, on a plan that allows third-party payment providers.
- [ ] Store currency **EGP**. The Paymob integrations are per currency.
- [ ] Which **payment methods** they want: card, Apple Pay, wallets, kiosk, valU, Sympl, Souhoola. This decides which app to install (step 1).

## 1. Pick the app

| App | What the customer sees | Use when |
|---|---|---|
| **Paymob Multi App** | Redirected to Paymob Unified Checkout, which lists every method enabled on the account (card, wallet, kiosk and so on) | They want several methods behind one button. This is the default choice. |
| **Paymob Card App** | Enters card details on the Shopify checkout itself, then goes to the bank's OTP (3-D Secure) page; Apple Pay is enabled too | They want a card-first checkout with no redirect before OTP |
| **valU / Sympl / Souhoola apps** | Redirected to Unified Checkout showing only that BNPL option | They want BNPL as a separate, labelled option at checkout |

Several apps can be installed together. A common setup is Card App plus valU App.

## 2. Paymob dashboard: create the integrations

In the Paymob dashboard (accept.paymob.com), open **Developers → Payment Integrations** (older dashboards call it the **Payment Integrations** tab), then **Add**:

1. Create one integration per payment method: Card, Wallet, Kiosk, valU and so on.
   - Set **Currency** to **EGP**.
   - If the form shows a **"Use Shopify"** toggle, turn it on. The older Egypt guide requires it.
2. Start with **test** integrations. Live integration IDs only appear after Paymob activates the account.
3. Note the integration IDs for the merchant's records. The current apps read them from the account after you log in, so you normally don't type them into Shopify. If the app ever asks for one, it is on this page.

**Legacy plugin only:** the old app asked for the **Accept portal username** and a **secret key**, which is the HMAC value under **Settings → Account info → HMAC** in the dashboard. The current apps log in with username and password instead.

## 3. Shopify: install and activate

1. Shopify admin → **Settings → Payments**.
2. **Add payment method** → **Search by provider** → search **"Paymob"**. Alternatively, install the chosen app from the Shopify App Store.
3. Install the app chosen in step 1.
4. In the app:
   - Select **Region**: **Egypt**, then **Next**.
   - The merchant enters their **Paymob dashboard username and password** themselves.
   - When it returns to Shopify: tick **Test mode** if the account has no live integrations yet, then click **Activate**.
5. **Required:** **Settings → Payments → Payment capture method** must be **Automatic**. Paymob's guide warns that payments will not be processed otherwise.

## 4. Test before going live

Place real test orders on the storefront while the app is in test mode. Use Paymob's published test cards (developers.paymob.com → test credentials); never use a real card in test mode.

| Check | Expected |
|---|---|
| Successful card payment | Order shows **Paid** in Shopify; transaction appears in Paymob → Transactions with the same amount |
| Declined / failed OTP | Customer returns to checkout; no paid order is created |
| Customer closes the page mid-payment | Order is not marked paid. Note what Shopify shows (abandoned checkout or pending). |
| Refund from Shopify (Orders → Refund) | Refund appears in Paymob; check partial refund too if the app supports it |
| Each extra method (wallet, kiosk, valU) | Appears at checkout and completes |
| Mobile checkout | Works on a phone, including the bank OTP page |

Record each result with the order number, Paymob transaction ID, time and outcome. A setup is not done until a test order and a refund have both been seen end to end.

## 5. Go live

1. Paymob activates the account and issues **live** integrations. Confirm they show in the dashboard.
2. In the Shopify app, untick **Test mode** and save.
3. Place one small real order with a real card, then refund it. Confirm both in Shopify and Paymob.
4. Tell the merchant where settlements appear (Paymob dashboard → payouts/settlements) and the payout schedule in their Paymob agreement. Don't guess the schedule.

## 6. Troubleshooting

| Symptom | Check first |
|---|---|
| Paymob is not listed under Payments | The store's country/plan supports third-party providers; search by provider name; try installing from the App Store listing |
| Customer paid but the order isn't marked paid | Payment capture set to **Automatic**; test vs live mismatch (test mode on with live integrations or the reverse); the transaction in the Paymob dashboard |
| "Integration not found" or a currency error | Integration currency is EGP; the right integration is active; "Use Shopify" is on where shown |
| Only card shows, no wallet or kiosk | Card App is installed instead of Multi App, or those integrations are missing or inactive on the Paymob account |
| Works in test, fails live | Live integrations not yet issued or not active; app still in test mode |
| Refund not reaching the customer | Look it up in the Paymob dashboard; card refunds take time to post at the bank |

If none of these explain it, contact Paymob support with:
- the Shopify order number;
- the Paymob transaction ID;
- the time, with time zone;
- whether the app was in test or live mode.

## Rules

- **Credentials stay with the merchant.** Usernames, passwords, API keys and HMAC secrets are typed by the merchant into Paymob or Shopify. Never put them in chat, docs, tickets or code.
- **Do not edit `checkout.liquid` or theme code to add Paymob.** The official app adds it as a payment method; Shopify controls checkout.
- **Never report "payments work" from a test order alone.** Live is proven by one real order and refund.
- **Paymob's screens move.** If a menu or field named here isn't where this file says, follow the current guide at developers.paymob.com and update this skill.
