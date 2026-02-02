# CrankCase Strategic Proposals

## Current Product State

CrankCase is a bike maintenance tracking application designed for serious cyclists who own multiple bikes and want to stay on top of component wear and service schedules.

### Core Features
- **Multi-bike management**: Users can track multiple bikes (road, gravel, MTB, etc.)
- **Component tracking**: Add parts with brand/model, cost, and install date
- **Maintenance logging**: Log various maintenance actions including:
  - Chain care (drip wax, hot wax applications)
  - Component inspection
  - General service
  - Part replacement with reason tracking (worn/damaged)
  - Cleaning
- **Part lifecycle management**: Move parts between bikes, track replacement history
- **Strava integration**: Sync ride data to track mileage/usage
- **Push notifications**: Alert users when maintenance is due
- **Timeline view**: Visual history of all maintenance activities

### Current State Assessment
- Product is functional but appears to be single-user/hobbyist focused
- No visible monetization (free tier only)
- Strong foundation for tracking but limited social/community features
- Strava integration provides valuable usage data for predictive maintenance
- No marketplace or e-commerce integration

---

## Strategic Proposal 1: Premium Subscription Tier ("CrankCase Pro")

### Description
Introduce a freemium model with a Pro subscription offering advanced features for serious cyclists. Free tier remains for basic tracking (1-2 bikes, manual entry only). Pro tier unlocks unlimited bikes, Strava auto-sync, predictive maintenance alerts based on mileage thresholds, and detailed cost analytics/reporting.

### Revenue Model
- **Monthly subscription**: $4.99/month or $39.99/year
- **Target conversion**: 5-10% of active users
- **LTV focus**: Annual plans with discount to reduce churn

### Key Features to Gate
- Unlimited bikes (free: 2 bikes max)
- Strava auto-sync (free: manual entry only)
- Predictive maintenance alerts ("Chain at 80% life based on 2,500 miles")
- Cost analytics and reporting (total spend, cost-per-mile, budget planning)
- Export data (CSV/PDF for insurance or resale documentation)
- Priority support

### Effort Estimate
**Medium** - Requires implementing subscription infrastructure (Stripe), feature gating, and building analytics/prediction features. Core app architecture exists.

### Key Risks
- Market may not support subscription fatigue for "yet another app"
- Free alternatives (spreadsheets, Strava notes) may be sufficient for casual users
- Need to deliver enough Pro value to justify recurring cost

---

## Strategic Proposal 2: B2B for Bike Shops ("CrankCase Shop")

### Description
Pivot to offer a white-label or B2B version for local bike shops (LBS) and bike fitters. Shops can manage customer bikes, track service history, send automated maintenance reminders, and build recurring revenue through proactive service outreach. Customers get a "my mechanic" experience while shops increase return visits.

### Revenue Model
- **SaaS per shop**: $49-149/month based on customer count tiers
- **Per-customer fee alternative**: $1-2/month per active customer managed
- **Revenue share on services booked**: 5-10% of services booked through reminders

### Key Features to Build
- Shop dashboard: manage multiple customer bikes
- Customer handoff: "Add to my CrankCase" after shop visit
- Automated service reminders (email/SMS) branded to the shop
- Service booking integration
- Inventory tracking for common parts
- Multi-user shop accounts (mechanics, front desk)

### Effort Estimate
**High** - Requires significant new functionality: multi-tenant architecture, shop admin portal, customer relationship management, email/SMS infrastructure, potentially booking system integration.

### Key Risks
- Long sales cycle for B2B customers
- Bike shops operate on thin margins, may resist monthly SaaS fees
- Need to prove ROI (increased return visits, higher ticket values)
- Competition from existing POS/shop management systems

---

## Strategic Proposal 3: Component Marketplace Integration

### Description
Partner with or build integrations to online bike component retailers (e.g., Competitive Cyclist, Jenson USA, Chain Reaction Cycles). When users log that a part is worn or due for replacement, surface affiliate links to purchase replacements. Also explore user-to-user marketplace for lightly-used takeoff parts.

### Revenue Model
- **Affiliate commissions**: 3-8% on purchases made through CrankCase links
- **Sponsored placements**: Brands pay for preferred positioning when showing replacement options
- **P2P marketplace fees**: 10-15% transaction fee on user-to-user part sales

### Key Features to Build
- Part catalog database (SKUs, compatibility, pricing across retailers)
- "Replace Now" button that shows purchase options
- Price comparison across retailers
- Optional P2P marketplace (list takeoff parts, in-app messaging, payment processing)
- Brand partnership dashboard for sponsored content

### Effort Estimate
**Medium** - Affiliate integration is relatively straightforward. P2P marketplace is more complex (payments, disputes, shipping). Could start with affiliate-only MVP.

### Key Risks
- Affiliate margins are thin; need high volume to generate meaningful revenue
- P2P marketplace requires trust/safety investment (fraud, disputes)
- Users may prefer to shop directly on trusted retailers
- Dependency on third-party affiliate programs (can change terms)

---

## Recommendation

**Start with Proposal 1 (Premium Subscription)** as the initial monetization strategy:
- Lowest implementation effort
- Validates willingness to pay before larger investments
- Builds recurring revenue foundation
- Can layer on Proposal 3 (affiliate marketplace) as a complementary revenue stream
- Proposal 2 (B2B) should be explored once consumer product-market fit is proven

### Suggested Roadmap
1. **Phase 1 (1-2 months)**: Implement subscription infrastructure, define Pro features
2. **Phase 2 (2-3 months)**: Build predictive maintenance and cost analytics
3. **Phase 3 (3-4 months)**: Add affiliate marketplace integration
4. **Phase 4 (6+ months)**: Explore B2B pilot with 2-3 local bike shops
