# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: gravitas.spec.ts >> 2. Recommendation Gatekeeper Test - State Accuracy >> INSUFFICIENT_DATA state: should show insufficient-data UI
- Location: e2e\gravitas.spec.ts:146:7

# Error details

```
TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[type="submit"]').first()
    - locator resolved to <button type="submit" class="query-button">Get Legal Decision</button>
  - attempting click action
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - performing click action

```

```
Tearing down "context" exceeded the test timeout of 60000ms.
```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic:
    - status "Loading content"
  - generic [ref=e3]:
    - navigation [ref=e7]:
      - generic [ref=e8] [cursor=pointer]:
        - img "NYAI Logo" [ref=e9]
        - generic [ref=e10]: NYAI
      - button "Menu" [ref=e11] [cursor=pointer]
    - complementary [ref=e12]:
      - list [ref=e14]:
        - listitem [ref=e15]:
          - link [ref=e16] [cursor=pointer]:
            - /url: "#"
            - generic [ref=e17]: Chat Mode
        - listitem [ref=e18]:
          - link [ref=e19] [cursor=pointer]:
            - /url: "#"
            - generic [ref=e20]: Decision Draft
        - listitem [ref=e21]:
          - link [ref=e22] [cursor=pointer]:
            - /url: "#"
            - generic [ref=e23]: Law Agent
        - listitem [ref=e24]:
          - link [ref=e25] [cursor=pointer]:
            - /url: "#"
            - generic [ref=e26]: Explore
        - listitem [ref=e27]:
          - link [ref=e28] [cursor=pointer]:
            - /url: "#"
            - generic [ref=e29]: E2E
        - listitem [ref=e30]:
          - link [ref=e31] [cursor=pointer]:
            - /url: "#"
            - generic [ref=e32]: Logout
    - generic [ref=e34]:
      - button "← Back to Dashboard" [ref=e35] [cursor=pointer]
      - generic [ref=e36]:
        - generic [ref=e37]:
          - heading "NYAI Legal Agent" [level=1] [ref=e38]
          - paragraph [ref=e39]: Real-time structured legal advisory with TANTRA-canonical recommendations
        - generic [ref=e42]:
          - generic [ref=e43]:
            - generic [ref=e44]: Enter Your Legal Query
            - textbox "Enter Your Legal Query" [ref=e45]:
              - /placeholder: "Example: What are the procedures for filing a civil suit in India?"
              - text: vague legal question
          - button "Get Legal Decision" [ref=e46] [cursor=pointer]
        - generic [ref=e47]:
          - generic [ref=e49]:
            - heading "❓ INSUFFICIENT DATA" [level=2] [ref=e50]
            - paragraph [ref=e51]: INSUFFICIENT_DATA
            - paragraph [ref=e52]: Insufficient data to provide reliable legal guidance
          - generic [ref=e55]:
            - generic [ref=e56]:
              - generic [ref=e57]: Domain
              - generic [ref=e58]: CIVIL
            - generic [ref=e59]:
              - generic [ref=e60]: Jurisdiction
              - generic [ref=e61]: India
            - generic [ref=e62]:
              - generic [ref=e63]: Confidence
              - generic [ref=e64]: 85%
            - generic [ref=e65]:
              - generic [ref=e66]: Trace ID
              - generic [ref=e67]: e2e-trace-001
          - generic [ref=e68]:
            - heading "Legal Analysis" [level=3] [ref=e69]
            - paragraph [ref=e71]: Civil suit filing procedure guidance for district court.
          - button "Procedural Steps ▼" [ref=e73] [cursor=pointer]:
            - heading "Procedural Steps" [level=3] [ref=e74]
            - generic [ref=e75]: ▼
          - button "Timeline ▼" [ref=e77] [cursor=pointer]:
            - heading "Timeline" [level=3] [ref=e78]
            - generic [ref=e79]: ▼
          - button "Decision Provenance ▼" [ref=e81] [cursor=pointer]:
            - heading "Decision Provenance" [level=3] [ref=e82]
            - generic [ref=e83]: ▼
          - button "Confidence Analysis ▼" [ref=e85] [cursor=pointer]:
            - heading "Confidence Analysis" [level=3] [ref=e86]
            - generic [ref=e87]: ▼
          - generic [ref=e88]:
            - button "📥 Export Decision" [ref=e89] [cursor=pointer]
            - button "🔄 New Query" [ref=e90] [cursor=pointer]
```