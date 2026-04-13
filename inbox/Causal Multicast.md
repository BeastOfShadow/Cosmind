---
id: 20260412182904
aliases: []
tags:
  - status/1-draft
  - domain/Computer Networks and Distributed Systems
created: 2026-04-12
modified: 2026-04-12
---

# 📌 Causal Multicast nei sistemi distribuiti

## 🧠 TL;DR
> [!summary] Abstract
> - Causal multicast con ordini validi variando per nodo.

---

## 📝 Body
- Gli ordini validi variano in base al nodo, seguendo l'ordine dei messaggi.
  ![Casual_multicast](assets/img_1775834874_885b950a.png)
  ![Casual_multicast_variation](assets/img_1775834971_1658f24c.png)

In questo esempio, l'ordine valido sarà:
A: $(m_1, m_3, m_2)$, B: $(m_1, m_2, m_3)$, C: $(m_1, m_3, m_2)$

![Casual_multicast_hold_back](assets/img_1775835108_bbd549af.png)
Perciò può presentarsi l'hold-back.

---

## 🔗 Knowledge Graph
- **Derives from:** [[Multicast nei sistemi distribuiti]]
- **Leads to:** 
- **Similar:** 

## 📚 Sources
- User Source Note
