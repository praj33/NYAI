# Trace Log Examples

## Example 1: Normal Query Trace

```json
{
  "trace_id": "abc123-def456-ghi789-jkl012",
  "event_chain": [
    {
      "index": 1,
      "timestamp": "2024-12-30T10:00:00.123456Z",
      "event_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
      "prev_hash": "00000000000000000000000000000000000000000000000000000000",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T10:00:00.123456Z",
          "agent_id": "api_gateway",
          "jurisdiction": "global",
          "event_name": "query_received",
          "request_hash": 12345678,
          "details": {
            "query": "What are the penalties for theft under Indian law?",
            "jurisdiction_hint": "India",
            "domain_hint": "criminal"
          },
          "trace_id": "abc123-def456-ghi789-jkl012"
        },
        "signature": "MEUCIQCv8dXJZ8Vq2Yp9N3x7Rt4Gh5Jk2Lm9N0Pq3Rs4Tu5Vw6Xy7Za8Bc9D",
        "key_id": "primary-key-2025"
      }
    },
    {
      "index": 2,
      "timestamp": "2024-12-30T10:00:00.234567Z",
      "event_hash": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2",
      "prev_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T10:00:00.234567Z",
          "agent_id": "jurisdiction_router_agent",
          "jurisdiction": "global",
          "event_name": "jurisdiction_resolved",
          "request_hash": 12345678,
          "details": {
            "resolved_jurisdiction": "IN",
            "confidence": 0.95,
            "routing_reason": "query contains 'Indian law' keyword"
          },
          "trace_id": "abc123-def456-ghi789-jkl012"
        },
        "signature": "MEUCIQDx7Yv3Qp9N3x7Rt4Gh5Jk2Lm9N0Pq3Rs4Tu5Vw6Xy7Za8Bc9D",
        "key_id": "primary-key-2025"
      }
    },
    {
      "index": 3,
      "timestamp": "2024-12-30T10:00:00.345678Z",
      "event_hash": "c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2c3",
      "prev_hash": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T10:00:00.345678Z",
          "agent_id": "india_legal_agent",
          "jurisdiction": "India",
          "event_name": "agent_classified",
          "request_hash": 12345678,
          "details": {
            "agent_id": "india_legal_agent",
            "confidence": 0.87,
            "classification": "criminal_law",
            "relevant_sections": ["IPC_240", "IPC_241", "IPC_242"]
          },
          "trace_id": "abc123-def456-ghi789-jkl012"
        },
        "signature": "MEUCIQFv8eXm2Yp9N3x7Rt4Gh5Jk2Lm9N0Pq3Rs4Tu5Vw6Xy7Za8Bc9D",
        "key_id": "primary-key-2025"
      }
    },
    {
      "index": 4,
      "timestamp": "2024-12-30T10:00:00.456789Z",
      "event_hash": "d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2c3d4",
      "prev_hash": "c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2c3",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T10:00:00.456789Z",
          "agent_id": "india_legal_agent",
          "jurisdiction": "India",
          "event_name": "reasoning_explained",
          "request_hash": 12345678,
          "details": {
            "response": "Theft is penalized under Section 378 of IPC with imprisonment up to 3 years and fine.",
            "confidence": 0.87,
            "constitutional_articles": ["Article 21", "Article 14"],
            "reasoning_steps": ["Identified relevant IPC sections", "Determined penalty", "Checked constitutional provisions"]
          },
          "trace_id": "abc123-def456-ghi789-jkl012"
        },
        "signature": "MEUCIQHs9fYn3Zq8Rt4Gh5Jk2Lm9N0Pq3Rs4Tu5Vw6Xy7Za8Bc9D",
        "key_id": "primary-key-2025"
      }
    },
    {
      "index": 5,
      "timestamp": "2024-12-30T10:00:00.567890Z",
      "event_hash": "e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2c3d4e5",
      "prev_hash": "d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2c3d4",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T10:00:00.567890Z",
          "agent_id": "api_gateway",
          "jurisdiction": "global",
          "event_name": "trace_completed",
          "request_hash": 12345678,
          "details": {
            "final_confidence": 0.87,
            "legal_route": ["jurisdiction_router_agent", "india_legal_agent"],
            "response_sent": true
          },
          "trace_id": "abc123-def456-ghi789-jkl012"
        },
        "signature": "MEUCIQJt0gZo4Ap5Bq6Cr7Ds8Et9Fu0Gv1Hw2Ix3Jy4Kz5Lm6Np7Q",
        "key_id": "primary-key-2025"
      }
    }
  ],
  "agent_routing_tree": {
    "root": "api_gateway",
    "children": {
      "jurisdiction_router_agent": {
        "jurisdiction": "global",
        "events": ["jurisdiction_resolved"]
      },
      "india_legal_agent": {
        "jurisdiction": "India",
        "events": ["agent_classified", "reasoning_explained"]
      }
    }
  },
  "jurisdiction_hops": ["global", "India"],
  "rl_reward_snapshot": {
    "placeholder": "RL data would be fetched here"
  },
  "context_fingerprint": "fingerprint_abc123_def456",
  "nonce_verification": true,
  "signature_verification": true
}
```

## Example 2: Feedback-Triggered Trace

```json
{
  "trace_id": "xyz789-abc123-def456-ghi789",
  "event_chain": [
    {
      "index": 1,
      "timestamp": "2024-12-30T11:00:00.111111Z",
      "event_hash": "x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7",
      "prev_hash": "00000000000000000000000000000000000000000000000000000000",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T11:00:00.111111Z",
          "agent_id": "api_gateway",
          "jurisdiction": "global",
          "event_name": "query_received",
          "request_hash": 98765432,
          "details": {
            "query": "What are employee rights in UK labor law?",
            "jurisdiction_hint": "UK",
            "domain_hint": "labor"
          },
          "trace_id": "xyz789-abc123-def456-ghi789"
        },
        "signature": "MEUCIQXv9eXm2Yp9N3x7Rt4Gh5Jk2Lm9N0Pq3Rs4Tu5Vw6Xy7Za8Bc9D",
        "key_id": "primary-key-2025"
      }
    },
    {
      "index": 2,
      "timestamp": "2024-12-30T11:00:00.222222Z",
      "event_hash": "y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8",
      "prev_hash": "x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T11:00:00.222222Z",
          "agent_id": "jurisdiction_router_agent",
          "jurisdiction": "global",
          "event_name": "jurisdiction_resolved",
          "request_hash": 98765432,
          "details": {
            "resolved_jurisdiction": "UK",
            "confidence": 0.98,
            "routing_reason": "explicit UK jurisdiction hint"
          },
          "trace_id": "xyz789-abc123-def456-ghi789"
        },
        "signature": "MEUCIQYw0fYn3Zq8Rt4Gh5Jk2Lm9N0Pq3Rs4Tu5Vw6Xy7Za8Bc9D",
        "key_id": "primary-key-2025"
      }
    },
    {
      "index": 3,
      "timestamp": "2024-12-30T11:00:00.333333Z",
      "event_hash": "z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9",
      "prev_hash": "y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T11:00:00.333333Z",
          "agent_id": "uk_legal_agent",
          "jurisdiction": "UK",
          "event_name": "agent_classified",
          "request_hash": 98765432,
          "details": {
            "agent_id": "uk_legal_agent",
            "confidence": 0.72,
            "classification": "labor_law",
            "relevant_sections": ["UK_Employment_Rights_Act_1996", "Working_Time_Regulations_1998"]
          },
          "trace_id": "xyz789-abc123-def456-ghi789"
        },
        "signature": "MEUCIQZx1gZo4Ap5Bq6Cr7Ds8Et9Fu0Gv1Hw2Ix3Jy4Kz5Lm6Np7Q",
        "key_id": "primary-key-2025"
      }
    },
    {
      "index": 4,
      "timestamp": "2024-12-30T11:00:00.444444Z",
      "event_hash": "a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0",
      "prev_hash": "z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T11:00:00.444444Z",
          "agent_id": "uk_legal_agent",
          "jurisdiction": "UK",
          "event_name": "reasoning_explained",
          "request_hash": 98765432,
          "details": {
            "response": "UK employees have rights to minimum wage, working time limits, and protection from unfair dismissal.",
            "confidence": 0.72,
            "reasoning_steps": ["Identified Employment Rights Act", "Determined employee protections", "Checked working time regulations"]
          },
          "trace_id": "xyz789-abc123-def456-ghi789"
        },
        "signature": "MEUCIQay2hAp5Bq6Cr7Ds8Et9Fu0Gv1Hw2Ix3Jy4Kz5Lm6Np7Q",
        "key_id": "primary-key-2025"
      }
    },
    {
      "index": 5,
      "timestamp": "2024-12-30T11:05:00.555555Z",
      "event_hash": "b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0b1",
      "prev_hash": "a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T11:05:00.555555Z",
          "agent_id": "api_gateway",
          "jurisdiction": "global",
          "event_name": "feedback_received",
          "request_hash": 98765432,
          "details": {
            "trace_id": "xyz789-abc123-def456-ghi789",
            "rating": 2,
            "feedback_type": "correctness",
            "comment": "Response missed important points about UK labor law",
            "user_id": "user_12345"
          },
          "trace_id": "xyz789-abc123-def456-ghi789"
        },
        "signature": "MEUCIQbz3iBq6Cr7Ds8Et9Fu0Gv1Hw2Ix3Jy4Kz5Lm6Np7Q",
        "key_id": "primary-key-2025"
      }
    },
    {
      "index": 6,
      "timestamp": "2024-12-30T11:05:00.666666Z",
      "event_hash": "c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0b1c2",
      "prev_hash": "b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0b1",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T11:05:00.666666Z",
          "agent_id": "rl_engine",
          "jurisdiction": "global",
          "event_name": "reward_computed",
          "request_hash": 98765432,
          "details": {
            "trace_id": "xyz789-abc123-def456-ghi789",
            "rating": 2,
            "computed_reward": -0.3,
            "confidence_adjustment": -0.05,
            "penalty_reason": "low correctness rating"
          },
          "trace_id": "xyz789-abc123-def456-ghi789"
        },
        "signature": "MEUCIQc04jCq7Ds8Et9Fu0Gv1Hw2Ix3Jy4Kz5Lm6Np7Q",
        "key_id": "primary-key-2025"
      }
    },
    {
      "index": 7,
      "timestamp": "2024-12-30T11:05:00.777777Z",
      "event_hash": "d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0b1c2d3",
      "prev_hash": "c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0b1c2",
      "signed_event": {
        "event": {
          "timestamp": "2024-12-30T11:05:00.777777Z",
          "agent_id": "api_gateway",
          "jurisdiction": "global",
          "event_name": "trace_completed",
          "request_hash": 98765432,
          "details": {
            "final_confidence": 0.72,
            "legal_route": ["jurisdiction_router_agent", "uk_legal_agent"],
            "response_sent": true,
            "feedback_processed": true,
            "rl_adjustment_applied": true
          },
          "trace_id": "xyz789-abc123-def456-ghi789"
        },
        "signature": "MEUCIQd15kDr8Et9Fu0Gv1Hw2Ix3Jy4Kz5Lm6Np7Q",
        "key_id": "primary-key-2025"
      }
    }
  ],
  "agent_routing_tree": {
    "root": "api_gateway",
    "children": {
      "jurisdiction_router_agent": {
        "jurisdiction": "global",
        "events": ["jurisdiction_resolved"]
      },
      "uk_legal_agent": {
        "jurisdiction": "UK",
        "events": ["agent_classified", "reasoning_explained"]
      },
      "rl_engine": {
        "jurisdiction": "global",
        "events": ["reward_computed"]
      }
    }
  },
  "jurisdiction_hops": ["global", "UK"],
  "rl_reward_snapshot": {
    "rating": 2,
    "computed_reward": -0.3,
    "confidence_adjustment": -0.05,
    "penalty_reason": "low correctness rating"
  },
  "context_fingerprint": "fingerprint_xyz789_abc123",
  "nonce_verification": true,
  "signature_verification": true
}
```