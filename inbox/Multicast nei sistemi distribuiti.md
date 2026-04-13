---
id: 20260412182904
aliases: ["FIFO multicast", "Causal multicast", "Total order multicast", "FIFO-total order multicast", "Casual-total order multicast"]
tags:
  - status/1-draft
  - domain/Computer Networks and Distributed Systems
created: 2026-04-12
modified: 2026-04-12
---

# 📌 Casi di multicast nei sistemi distribuiti

## 🧠 TL;DR
> [!summary] Abstract
> - Diversi casi di multicast nei sistemi distribuiti
- FIFO multicast: seguendo l'ordine dei messaggi da diversi nodi
- Causal multicast: ordini validi variano per nodo, basati sull'ordine dei messaggi
- Total order multicast: tutti i nodi devono avere lo stesso ordine di arrivo dei messaggi
- FIFO-total order multicast e Casual-total order multicast combinano regole del FIFO/total order con casual/total order

---

## 📝 Body
- **FIFO Multicast**
  - Deve rispettare l'ordine di invio dei messaggi dai vari nodi.
  ![FIFO_multicast](assets/img_1775833975_7b17a7ae.png)
  ![FIFO_multicast_variation](assets/img_1775834094_f4414dc1.png)
- **Causal Multicast**
  - Gli ordini validi variano in base al nodo, seguendo l'ordine dei messaggi.
  ![Casual_multicast](assets/img_1775834874_885b950a.png)
  ![Casual_multicast_variation](assets/img_1775834971_1658f24c.png)
  ![Casual_multicast_hold_back](assets/img_1775835108_bbd549af.png)
- **Total Order Multicast**
  - Il total order dipende dall'ordine di arrivo dei messaggi e tutti i nodi devono avere lo stesso ordine.
  ![Total_order_multicast](assets/img_1775835221_2ea15cbb.png)
- **FIFO-Total Order Multicast**
  - Unisce le regole del FIFO e del total order.
  ![Fifo_total_order_multicast](assets/img_1775835741_d495a655.png)
- **Casual-Total Order Multicast**
  - Unisce le regole del casual e del total order multicast.

---

## 🔗 Knowledge Graph
- **Derives from:** 
- **Leads to:** [[FIFO multicast]], [[Causal multicast]], [[Total order multicast]], [[FIFO-total order multicast]], [[Casual-total order multicast]]
- **Similar:** 

## 📚 Sources
- User Source Note
