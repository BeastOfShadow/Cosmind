# test_rag

# Multicast nei sistemi distribuiti
Abbiamo diversi possibili casi:
- FIFO multicast
- Causal multicast
- Total order multicast
- FIFO-total order multicast
- Causal-total order multicast
## FIFO multicast
Devo seguire l'ordine dei messaggi dei vari nodi, nel senso che bisogna rispettare l'ordine di invio dei messaggi dei vari nodi.
![FIFO_multicast](assets/img_1775833975_7b17a7ae.png)
In questo esempio, per il nodo $A$, siamo costretti a seguire l'ordine $m_1, m_3$. Infatti gli ordini validi sono: 
$(m_2,m_1,m_3)$ or $(m_1,m_2,m_3)$  $(m_1,m_3,m_2)$
![FIFO_multicast_variation](assets/img_1775834094_f4414dc1.png)
Anche il risultato della seconda immagine sarà uguale, cambierebbe solamente se avessi un altro messaggio dopo $m_2$ (chiamato $m_4$), poiché avrei un altro vincolo.
## Casual multicast
In questo caso, gli ordini validi variano in base al nodo, seguendo l'ordine dei messaggi.
![Casual_multicast](assets/img_1775834874_885b950a.png)
In questo esempio, l'ordine valido sarà:
A: $(m_1, m_3, m_2)$, B: $(m_1, m_2, m_3)$, C: $(m_1, m_3, m_2)$
![Casual_multicast_variation](assets/img_1775834971_1658f24c.png)
In questo altro esempio, cambia l'ordine sulla C:
A: $(m_1, m_3, m_2)$, B: $(m_1, m_2, m_3)$, C: $(m_1, m_2, m_3)$
![Casual_multicast_hold_back](assets/img_1775835108_bbd549af.png)
In questo caso, può presentarsi l'hold-back.
## Total order multicast
Il total order dipende dall'ordine di arrivo dei messaggi e tutti i nodi devono avere lo stesso ordine. Infatti in questo caso abbiamo un hold back per rispettare l'ordine dei nodi B e C:
$(m_1, m_2, m_3)$
![Total_order_multicast](assets/img_1775835221_2ea15cbb.png)
## FIFO-total order multicast
Unisce le regole del FIFO e del total order. Infatti nello schema di sinistra, l'ordine sarà:
$(m_1, m_2, m_3)$
mentre nello schema di destra sarà:
$(m_1, m_3, m_2)$
![Fifo_total_order_multicast](assets/img_1775835741_d495a655.png)
Anch'esso può presentare degli hold-back.
## Casual-total order multicast
In questo ultimo caso, invece, unisce le regole del casual e del total order multicast. Infine anche questo multicast può presentare degli hold-back.