# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: gravitas.spec.ts >> Additional Integration Tests >> should maintain trace_id across page refreshes
- Location: e2e\gravitas.spec.ts:264:7

# Error details

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
      - generic [ref=e35]:
        - heading "NYAI" [level=1] [ref=e36]
        - paragraph [ref=e37]: AI-powered legal intelligence across India, UK, and UAE jurisdictions
      - generic [ref=e38]:
        - button "Ask Legal Question Get instant AI-powered legal analysis" [ref=e40] [cursor=pointer]:
          - heading "Ask Legal Question" [level=3] [ref=e41]
          - paragraph [ref=e42]: Get instant AI-powered legal analysis
        - button "Legal Decisions Query structured legal decisions with advisory recommendations" [ref=e44] [cursor=pointer]:
          - heading "Legal Decisions" [level=3] [ref=e45]
          - paragraph [ref=e46]: Query structured legal decisions with advisory recommendations
        - button "Jurisdiction Procedure Navigate through legal procedures by jurisdiction" [ref=e48] [cursor=pointer]:
          - heading "Jurisdiction Procedure" [level=3] [ref=e49]
          - paragraph [ref=e50]: Navigate through legal procedures by jurisdiction
        - button "Case Timeline Generate timeline for your legal case" [ref=e52] [cursor=pointer]:
          - heading "Case Timeline" [level=3] [ref=e53]
          - paragraph [ref=e54]: Generate timeline for your legal case
        - button "Legal Glossary Search legal terms and definitions" [ref=e56] [cursor=pointer]:
          - heading "Legal Glossary" [level=3] [ref=e57]
          - paragraph [ref=e58]: Search legal terms and definitions
      - generic [ref=e59]:
        - heading "About Us" [level=3] [ref=e60]
        - generic [ref=e61]:
          - generic [ref=e62]: Sovereign Compliant
          - generic [ref=e63]: Transparent AI
          - generic [ref=e64]: Real-time Analysis
          - generic [ref=e65]: Multi-Jurisdiction
```