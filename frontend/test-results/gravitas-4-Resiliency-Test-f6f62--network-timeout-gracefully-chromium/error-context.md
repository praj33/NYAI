# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: gravitas.spec.ts >> 4. Resiliency Test - Backend Failure >> should handle network timeout gracefully
- Location: e2e\gravitas.spec.ts:240:7

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
      - button "← Back to Dashboard" [ref=e35] [cursor=pointer]
      - generic [ref=e36]:
        - generic [ref=e37]:
          - heading "NYAI Legal Agent" [level=1] [ref=e38]
          - paragraph [ref=e39]: Real-time structured legal advisory with TANTRA-canonical recommendations
        - generic [ref=e41]:
          - generic [ref=e42]:
            - generic [ref=e43]:
              - generic [ref=e44]: Enter Your Legal Query
              - textbox "Enter Your Legal Query" [ref=e45]:
                - /placeholder: "Example: What are the procedures for filing a civil suit in India?"
                - text: test timeout query
            - button "Get Legal Decision" [ref=e46] [cursor=pointer]
          - generic [ref=e47]:
            - generic [ref=e48]: ⚠️
            - paragraph [ref=e49]: timeout of 30000ms exceeded
            - button "×" [ref=e50] [cursor=pointer]
    - generic [ref=e53]: "System Operating in Offline Mode: Data is being saved locally. Analysis will resume when the connection is restored."
```