---
title: Home
layout: home
---

Welcome!

Testing mermaid integration

```mermaid
graph TD
    A[Start] --> B{Have Passport?}
    B -->|Yes| C[Fill Application]
    B -->|No| D[Get Passport First]
    C --> E[Submit Documents]
    D --> B
    E --> F[Pay Fees]
    F --> G[Receive Visa]
```