# User Acquisition and Retention Strategy

## Executive Summary

CrankCase has a solid foundation for bike maintenance tracking but lacks the growth mechanisms needed to build a thriving user community. This strategy focuses on three pillars: **streamlined onboarding** to reduce friction for new users, **social features** to create engagement loops, and **Strava community integration** to tap into the existing cycling social graph.

The goal is to grow monthly active users (MAU) by 3x over 6 months while improving 30-day retention from an estimated baseline of 20% to 50%+. This user growth will create the foundation for the monetization strategies outlined in the broader product roadmap.

---

## Goals and Success Metrics

### Primary Goals
1. **Reduce onboarding friction** - Get users to their first meaningful action (adding a bike + component) within 2 minutes
2. **Increase engagement** - Create reasons for users to return weekly beyond reactive maintenance logging
3. **Leverage Strava network effects** - Use Strava's social graph to drive organic acquisition and retention

### Key Metrics

| Metric | Current (Est.) | 3-Month Target | 6-Month Target |
|--------|----------------|----------------|----------------|
| Day 1 Retention | 40% | 60% | 70% |
| Day 7 Retention | 25% | 40% | 50% |
| Day 30 Retention | 15% | 30% | 45% |
| Weekly Active Users (WAU) | Baseline | +50% | +150% |
| Strava-connected users | Unknown | 60% | 80% |
| Organic referrals/month | ~0 | 100 | 500 |

### North Star Metric
**Weekly maintenance actions per user** - Users who log at least one maintenance action per week are retained users. Target: increase from estimated 0.3 to 1.0 actions/week/user.

---

## Feature Breakdown

### Pillar 1: Streamlined Onboarding

#### 1.1 Quick-Start Bike Templates
Instead of requiring users to manually enter every bike detail, offer pre-configured templates for common bike types:
- Road bike (Shimano 105/Ultegra/Dura-Ace groupsets)
- Gravel bike (GRX groupset)
- Mountain bike (SRAM Eagle, Shimano XT/XTR)
- Commuter/Urban bike

Users select a template, customize brand/model, and get a bike with standard components pre-populated.

#### 1.2 Strava Bike Import
For users who connect Strava, auto-import their bikes with mileage data:
- Pull bike names and total distance from Strava
- Pre-populate the bike in CrankCase
- Prompt user to add components (with suggestions based on mileage)

#### 1.3 Guided First Maintenance Log
After adding their first bike, guide users through logging their most recent maintenance:
- "When did you last clean your chain?"
- "When did you last replace your chain?"
- Use this to set up intelligent reminders

#### 1.4 Progress Indicator
Show users their profile completion percentage:
- "Your garage is 60% complete"
- Checklist: Add bike ✓, Add components, Log maintenance, Connect Strava, Set reminders

### Pillar 2: Social Features

#### 2.1 Public Garage Profiles
Allow users to optionally make their bike garage public:
- Shareable URL (e.g., crankcase.cc/u/username)
- Shows bikes, build specs, and maintenance history
- Great for bike forums, classifieds (prove maintenance history), cycling clubs

#### 2.2 Activity Feed
Show a feed of recent activity from users you follow:
- "Josh added a new bike: 2024 Canyon Aeroad"
- "Sarah completed 5,000 miles on her Enve SES wheels"
- "Mike replaced his chain after 3,200 miles"

#### 2.3 Component Milestones & Achievements
Gamification to encourage logging and return visits:
- "Chain Warrior: Logged 10 chain waxes"
- "High Miler: Reached 10,000 miles on a single bike"
- "Meticulous Mechanic: Maintained 100% maintenance schedule"

#### 2.4 Follow System
Simple follow/following system:
- Follow friends, local cyclists, or pro athletes
- See their activity in your feed
- Get notified when someone follows you

### Pillar 3: Strava Community Integration

#### 3.1 Deep Strava Sync
Beyond basic mileage sync, pull richer data:
- Sync individual activities (not just totals)
- Show "miles since last maintenance" context
- Attribute maintenance to specific bikes automatically

#### 3.2 Strava Club Integration
Allow cycling clubs to have a CrankCase presence:
- Club admins can create a club garage
- Members can optionally share their bikes with the club
- Great for racing teams tracking shared equipment

#### 3.3 Post-Ride Maintenance Prompts
After syncing a ride from Strava, intelligently prompt:
- "You rode 50 miles in the rain. Log a chain cleaning?"
- "You've ridden 300 miles since your last wax. Time to re-wax?"
- These prompts drive engagement and habit formation

#### 3.4 Strava Activity Sharing
When logging maintenance, optionally share to Strava:
- "Just hot-waxed my chain on CrankCase 🔧"
- Creates awareness among Strava connections
- Drives organic discovery

#### 3.5 "Find Cyclists Like You"
Use Strava data to suggest users to follow:
- Similar weekly mileage
- Same local area
- Similar bike types
- Mutual Strava connections

---

## Rollout Phases

### Phase 1: Foundation (Weeks 1-4)
**Focus: Reduce friction, improve first-time experience**

- [ ] Implement bike templates for quick setup
- [ ] Add Strava bike import functionality
- [ ] Create guided first maintenance flow
- [ ] Add profile completion progress indicator
- [ ] Track and baseline retention metrics

**Success criteria:** Day 1 retention improves to 55%+

### Phase 2: Social Foundation (Weeks 5-8)
**Focus: Enable sharing and discovery**

- [ ] Build public garage profiles with shareable URLs
- [ ] Implement follow/following system
- [ ] Create basic activity feed infrastructure
- [ ] Add component milestones and achievements

**Success criteria:** 20% of users make profile public, 10% follow at least one user

### Phase 3: Strava Deep Integration (Weeks 9-12)
**Focus: Leverage Strava network effects**

- [ ] Implement deep Strava activity sync
- [ ] Add post-ride maintenance prompts
- [ ] Enable Strava activity sharing for maintenance logs
- [ ] Build "Find Cyclists Like You" recommendations

**Success criteria:** 70% of users connect Strava, 30-day retention hits 35%+

### Phase 4: Community & Virality (Weeks 13-16)
**Focus: Enable organic growth**

- [ ] Launch Strava club integration
- [ ] Add social sharing features (share build, share milestone)
- [ ] Implement referral program with incentives
- [ ] Optimize viral loops based on data

**Success criteria:** 100+ organic referrals/month, WAU growth curve inflecting upward

---

## Dependencies and Risks

### Dependencies

| Dependency | Risk Level | Mitigation |
|------------|------------|------------|
| Strava API access | Medium | Maintain good standing, have fallback manual entry |
| User-generated content moderation | Low | Start with limited social features, add moderation tools as needed |
| Push notification infrastructure | Low | Already exists per proposals doc |
| Analytics/tracking infrastructure | Medium | Implement proper event tracking before Phase 1 |

### Risks

#### Risk 1: Strava API Rate Limits or Policy Changes
**Likelihood:** Medium | **Impact:** High

Strava has historically restricted API access for competitive apps. CrankCase is complementary (maintenance, not training), but risk remains.

**Mitigation:**
- Position clearly as complementary to Strava, not competitive
- Build core value that works without Strava (manual entry + reminders)
- Don't store/display Strava's proprietary data (segment times, etc.)

#### Risk 2: Social Features Feel Empty at Launch
**Likelihood:** High | **Impact:** Medium

Social features require network density to feel valuable. Early users may see empty feeds.

**Mitigation:**
- Seed with "suggested follows" (power users, staff accounts)
- Focus on personal milestones/achievements first (don't require network)
- Gate social discovery until user base reaches critical mass

#### Risk 3: Onboarding Templates Reduce Engagement
**Likelihood:** Low | **Impact:** Low

If templates are too generic, users may not feel invested in their garage.

**Mitigation:**
- Always prompt for customization after template selection
- Templates are starting points, not locked configurations
- Track template usage vs. manual entry and optimize

#### Risk 4: Privacy Concerns with Public Profiles
**Likelihood:** Medium | **Impact:** Medium

Users may be uncomfortable sharing bike details (theft risk, location inference).

**Mitigation:**
- Default to private profiles (opt-in public)
- Never show location data on public profiles
- Allow granular visibility controls (hide specific bikes/components)

---

## Success Criteria Summary

This strategy succeeds if, after 6 months:

1. **Acquisition:** Monthly new user signups increase 2x through organic/Strava channels
2. **Activation:** 70%+ of new users add a bike within first session
3. **Retention:** 30-day retention exceeds 40%
4. **Engagement:** Average weekly maintenance actions per user exceeds 0.8
5. **Virality:** 15%+ of new users come from referrals or Strava shares

These metrics indicate a healthy, growing user base ready for monetization via premium features.

---

## Appendix: Issue Breakdown

See linked GitHub issues for implementation details:
- Quick-start bike templates
- Strava bike import
- Guided first maintenance flow
- Profile completion indicator
- Public garage profiles
- Follow system and activity feed
- Milestones and achievements
- Deep Strava sync
- Post-ride maintenance prompts
- Strava sharing integration
