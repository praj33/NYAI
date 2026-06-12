# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: gravitas.spec.ts >> 3. Rendering Fidelity Test - Data Matching >> should verify JSON response keys match UI selectors exactly
- Location: e2e\gravitas.spec.ts:182:7

# Error details

```
TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: /^Timeline$/i })

```

```
Tearing down "context" exceeded the test timeout of 60000ms.
```

# Page snapshot

```yaml
- generic [ref=e1]:
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
              - text: What are the procedures for filing a civil suit in India?
          - button "Get Legal Decision" [ref=e46] [cursor=pointer]
        - generic [ref=e47]:
          - generic [ref=e49]:
            - heading "ℹ️ INFORMATIONAL" [level=2] [ref=e50]
            - paragraph [ref=e51]: INFORM
            - paragraph [ref=e52]: Legal pathway clear
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
          - generic [ref=e72]:
            - button "Procedural Steps ▼" [active] [ref=e73] [cursor=pointer]:
              - heading "Procedural Steps" [level=3] [ref=e74]
              - generic [ref=e75]: ▼
            - list [ref=e77]:
              - listitem [ref=e78]: Verify jurisdiction
              - listitem [ref=e79]: Draft plaint
              - listitem [ref=e80]: Pay court fee
              - listitem [ref=e81]: File in court
              - listitem [ref=e82]: Serve notice to defendant
          - button "Timeline ▼" [ref=e84] [cursor=pointer]:
            - heading "Timeline" [level=3] [ref=e85]
            - generic [ref=e86]: ▼
          - button "Decision Provenance ▼" [ref=e88] [cursor=pointer]:
            - heading "Decision Provenance" [level=3] [ref=e89]
            - generic [ref=e90]: ▼
          - button "Confidence Analysis ▼" [ref=e92] [cursor=pointer]:
            - heading "Confidence Analysis" [level=3] [ref=e93]
            - generic [ref=e94]: ▼
          - generic [ref=e95]:
            - button "📥 Export Decision" [ref=e96] [cursor=pointer]
            - button "🔄 New Query" [ref=e97] [cursor=pointer]
```