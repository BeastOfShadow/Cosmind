---
id: 20260412182904
aliases: []
tags:
  - status/1-draft
  - domain/Computer Networks and Distributed Systems
created: 2026-04-12
modified: 2026-04-12
---

# 📌 FIFO Multicast nei sistemi distribuiti

## 🧠 TL;DR
> [!summary] Abstract
> - FIFO multicast segua l'ordine di invio dei messaggi dai vari nodi.

---

## 📝 Body
- Deve rispettare l'ordine di invio dei messaggi dai vari nodi.
  ![FIFO_multicast](assets/img_1775833975_7b17a7ae.png)
  ![FIFO_multicast_variation](assets/img_1775834094_f4414dc1.png)

Nell'esempio, per il nodo $A$, siamo costretti a seguire l'ordine $m_1, m_3$. Infatti gli ordini validi sono: 
$(m_2,m_1,m_3)$ or $(m_1,m_2,m_3)$  $(m_1,m_3,m_2)$

---

## 🔗 Knowledge Graph
- **Derives from:** [[Multicast nei sistemi distribuiti]]
- **Leads to:** 
- **Similar:** 

## 📚 Sources
- User Source Note
