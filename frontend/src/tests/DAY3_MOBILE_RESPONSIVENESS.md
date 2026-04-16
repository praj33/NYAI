# DAY 3 - Mobile Responsiveness Test Guide

**Date:** March 4, 2026  
**Phase:** DAY 3 of 3-Day Nyaya Agent Implementation  
**Task:** Verify Gravitas Decision Page works on mobile and tablet devices  

---

## Quick Test Checklist

### Desktop (1920x1080)
- [ ] Query form loads properly
- [ ] Button clickable and responsive
- [ ] Decision banner renders correctly
- [ ] All sections expandable/collapsible
- [ ] Text readable and not cut off
- [ ] Export button works
- [ ] New Query button resets form

### Tablet (iPad - 768x1024)
- [ ] Layout adapts to tablet width
- [ ] Query form not cramped
- [ ] Buttons large enough to tap
- [ ] Expandable sections work smoothly
- [ ] Confidence bars display correctly
- [ ] Timeline renders legibly
- [ ] Enforcement banner visible and clear

### Mobile (iPhone/Android - 375-428px)
- [ ] Query textarea full width
- [ ] Button full width and tapable
- [ ] Enforcement banner color clear
- [ ] Sections stack vertically
- [ ] No horizontal scroll
- [ ] Font sizes readable (min 14px)
- [ ] Toggle icons clickable
- [ ] Export button functional
- [ ] No text overflow

### Extra Small Mobile (320px)
- [ ] App still functional
- [ ] Critical elements visible
- [ ] No essential content hidden
- [ ] Scrolling only vertical

---

## Device Testing Setup

### Option 1: Chrome DevTools
```
1. Open DecisionPage in Chrome/Edge
2. Press F12 (DevTools)
3. Press Ctrl+Shift+M (Toggle device mode)
4. Select device from dropdown:
   - iPhone X: 375x812
   - iPad: 768x1024
   - Galaxy S10: 360x800
   - Pixel 4: 412x869
```

### Option 2: Real Devices
```
Mobile: Test on actual iPhone/Android
Tablet: Test on actual iPad/tablet
Desktop: Test on monitor at 1920x1080
```

### Option 3: Responsive Tester Extensions
- Chrome: "Responsive Viewer"
- Firefox: Built-in responsive design mode

---

## Test Scenarios by Device Size

### Mobile Testing (375px width)

#### Test 1: Form Submission
```
1. Open http://localhost:5173/decision
2. Tap query textarea
3. Type: "Can I file a civil suit in India?"
4. Tap "Get Legal Decision"
5. Wait for response
6. Result: ✓ Decision loads, banner visible, sections expandable
```

#### Test 2: Expand Sections
```
1. Tap "Procedural Steps" header
2. Observe: Section expands
3. Tap again: Section collapses
4. Result: ✓ Smooth toggle, content readable
```

#### Test 3: Read Timeline
```
1. Scroll to find "Timeline" section
2. Tap to expand
3. Verify: Timeline shows 3-4 items vertically
4. Result: ✓ Timeline readable without horizontal scroll
```

#### Test 4: Confidence Breakdown
```
1. Scroll to "Confidence Analysis"
2. Tap to expand
3. Verify: Bars stack vertically
4. Percentages visible on right
5. Result: ✓ No overflow, readable layout
```

#### Test 5: Export & New Query
```
1. Tap "📥 Export Decision" button
2. Verify: JSON file downloads
3. Tap "🔄 New Query" button
4. Result: ✓ Form clears, ready for new query
```

---

### Tablet Testing (768px width)

#### Test 6: Information Grid
```
1. Open decision on tablet (iPad size)
2. Check decision summary grid
3. Verify: 2 columns of items (Domain, Jurisdiction, Confidence, Trace ID)
4. Result: ✓ Grid layouts 2x2, readable
```

#### Test 7: Legal Route
```
1. Expand "Legal Route" section
2. Verify: Steps display as boxes with arrows (→)
3. Check: All steps visible, no truncation
4. Result: ✓ Route shows clearly
```

#### Test 8: Full Page Scroll
```
1. From top, scroll through entire page
2. Verify: All sections accessible
3. Check: No sticky elements blocking content
4. Result: ✓ Smooth scrolling, all content reachable
```

#### Test 9: Error Message Display
```
1. Go back to query form
2. Leave textarea empty
3. Tap submit
4. Verify: Error message shows with warning icon
5. Check: Message readable and clear
6. Result: ✓ Error displayed properly
```

#### Test 10: Enforcement Banner
```
1. Check enforcement banner on different states
2. For ALLOW: Green banner visible, ✅ label clear
3. For BLOCK: Red banner unmistakable, 🚫 label bold
4. For ESCALATE: Orange banner stands out
5. For SAFE_REDIRECT: Purple color distinct
6. Result: ✓ All colors distinguishable
```

---

### Desktop Testing (1920x1080)

#### Test 11: Full Grid Layout
```
1. Open decision on desktop
2. Check info grid: 4 columns (Domain | Jurisdiction | Confidence | Trace ID)
3. Verify: All items aligned and spaced
4. Result: ✓ Professional layout
```

#### Test 12: Wide Sections
```
1. Check expandable sections
2. Verify: Content area is 900-1000px wide
3. Check: Text line length reasonable (not too wide)
4. Result: ✓ Readable text, proper spacing
```

#### Test 13: Multi-Column Layout
```
1. If any future sections use grid
2. Verify: Grid responsive based on screen width
3. Result: ✓ Scales appropriately
```

---

## Responsive Breakpoints to Validate

The DecisionPage.css should handle these breakpoints:

### Breakpoint 1: Tablet (max-width: 768px)
```css
/* Expected changes: */
✓ 1-column layout
✓ Full-width buttons
✓ Reduced padding
✓ Smaller fonts (12-14px from 14-16px)
✓ Simplified grid layouts
```

### Breakpoint 2: Mobile (max-width: 480px)
```css
/* Expected changes: */
✓ Very tight padding
✓ Full-width everything
✓ Extra small fonts where possible
✓ Single column only
✓ Simplified visual elements
```

---

## Visual Regression Checks

### Font Sizes
```
Desktop:
  Header: 2.5rem (40px) ✓
  Section title: 1.2rem (19px) ✓
  Normal text: 1rem (16px) ✓

Tablet:
  Header: 1.8rem (29px) ✓
  Section title: 1rem (16px) ✓
  Normal text: 0.95rem (15px) ✓

Mobile:
  Header: 1.4rem (22px) ✓
  Section title: 1rem (16px) ✓
  Normal text: 0.9rem (14px) ✓
```

### Button/Touch Target Sizes
```
Desktop: 12px × 32px buttons OK
Tablet: Need 14px × 40px minimum
Mobile: Need 14px × 40px minimum (Apple HIG: 44pt = 44px)
```

### Spacing & Padding
```
Desktop:
  ✓ Sections: 30px padding
  ✓ Gap between items: 16px
  ✓ Margins: 20px 

Mobile:
  ✓ Sections: 16px padding
  ✓ Gap between items: 12px
  ✓ Margins: 0 16px
```

---

## Performance on Mobile

### Page Load Time
```
Target: < 3 seconds on 4G
Measure: Open DevTools Network tab
Note any slow-loading assets
```

### Scroll Performance
```
Target: 60 FPS smooth scrolling
Test: Open DevTools Performance tab, scroll page
Check: In DevTools Rendering, "Paint flashing" should be minimal
```

### Input Response
```
Target: Instant response to taps
Test: Tap buttons, should have immediate visual feedback
Check: No lag between tap and visual change
```

---

## Accessibility on Mobile

### Touch Targets
```
✓ All buttons ≥ 44px tall
✓ All clickable elements ≥ 44px × 44px
✓ Buttons have clear visual state (active/hover)
```

### Text Contrast
```
✓ Enforcement banner: White text on colored background
✓ Error messages: Dark text on light background
✓ Links/buttons: Sufficient contrast (WCAG AA)
```

### Orientation Changes
```
Test: Rotate device between portrait/landscape
✓ Layout should adapt
✓ Content should remain readable
✓ No content should be cut off
```

---

## Test Report Template

```
Mobile Responsiveness Test Report
Date: March 4, 2026
Tester: [Name]

Device: __________ (e.g., iPhone X, iPad, Galaxy S10)
Screen Size: __________ (e.g., 375x812)
Browser: __________ (Chrome, Safari, Firefox)
OS: __________ (iOS 15, Android 12)

FORM SECTION:
[ ] Textarea full width
[ ] Button clickable
[ ] Placeholder text visible
[ ] Submit button works

DECISION DISPLAY:
[ ] Enforcement banner visible
[ ] Color distinguishable
[ ] Title readable
[ ] Summary grid shows (2 or 4 columns based on device)

EXPANDABLE SECTIONS:
[ ] Toggle icons clickable
[ ] Sections expand smoothly
[ ] Text doesn't overflow
[ ] Collapse works

SPECIAL ELEMENTS:
[ ] Timeline renders properly
[ ] Confidence bars show completely
[ ] Legal route doesn't scroll horizontally
[ ] Export button works

ACTIONS:
[ ] Export decision downloads file
[ ] New Query button resets form
[ ] Error messages display clearly

ISSUES FOUND:
1. ______________________
2. ______________________
3. ______________________

OVERALL: [ ] PASS [ ] FAIL

Tester: __________ Date: __________
```

---

## Common Mobile Issues & Fixes

### Issue 1: Text Too Small
**Symptom:** Can't read text on mobile
**Cause:** Base font size too small
**Fix:** In DecisionPage.css, check body font-size at mobile breakpoint
```css
@media (max-width: 480px) {
  body {
    font-size: 14px;  /* Minimum readable size */
  }
}
```

### Issue 2: Buttons Not Clickable
**Symptom:** Can't tap button on mobile
**Cause:** Button too small or padding missing
**Fix:** Ensure min-height: 44px for buttons
```css
.action-button {
  min-height: 44px;
  padding: 12px 24px;
}
```

### Issue 3: Horizontal Scroll on Mobile
**Symptom:** Have to scroll left-right on phone
**Cause:** Element wider than viewport
**Fix:** Ensure max-width: 100% on all containers
```css
.decision-page {
  max-width: 100%;
  overflow-x: hidden;
}
```

### Issue 4: Layout Breaks on Landscape
**Symptom:** App doesn't look right when rotated
**Cause:** No media query for orientation change
**Fix:** Test @media (orientation: landscape)
```css
@media (orientation: landscape) and (max-height: 500px) {
  .decision-header {
    padding: 20px;  /* Reduce for landscape */
  }
}
```

### Issue 5: Fields Overflow on Extra Small Devices (320px)
**Symptom:** Text/buttons chopped off on very small screen
**Cause:** Fixed widths on mobile
**Fix:** Test on 320px width, use vw units carefully
```css
@media (max-width: 328px) {
  .decision-section {
    padding: 12px;
  }
}
```

---

## Testing Across Real Browsers

### iOS Safari (iPhone)
```
1. Open http://localhost:5173/decision on iPhone
2. Run through all tests above
3. Check: Viewport meta tag works
4. Verify: -webkit CSS doesn't cause issues
```

### Android Chrome
```
1. Open http://localhost:5173/decision on Android phone
2. Run through all tests above
3. Check: Touch events responsive
4. Verify: Layout stable
```

### Android Firefox
```
1. Open http://localhost:5173/decision in Firefox
2. Check: Rendering consistent with Chrome
3. Verify: No platform-specific issues
```

---

## Final Mobile Checklist

Before declaring DAY 3 mobile testing complete:

- [ ] Tested on at least 3 different devices/sizes
- [ ] All test scenarios passed
- [ ] No horizontal scrolling on mobile
- [ ] Button sizes ≥ 44px
- [ ] Text readable (min 14px)
- [ ] No console errors on device
- [ ] Performance acceptable (load < 3s)
- [ ] Error messages display correctly
- [ ] All enforcement states visible
- [ ] Export and reset buttons work

---

**Test Date:** ___________
**Tester Name:** ___________
**Pass/Fail:** [ ] PASS / [ ] FAIL

Signature: ___________
