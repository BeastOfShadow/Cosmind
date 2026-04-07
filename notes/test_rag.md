# 0 Introduzione

Esistono diversi sistemi operativi, come: Windows, Apple, IoS, Linux, Andorid auto.

Il sistema operativo serve a:

- fornire un insieme di risorse astratte ai programmi utente che modellano un computer;
- gestire le risorse hardware.
- Immagine .
    
    ![Untitled](0%20Introduzione/Untitled.png)
    

Il sistema operativo si interfaccia tra l’interfaccia utente e l’hardware.

- Posizionamento .
    
    ![Untitled](0%20Introduzione/Untitled%201.png)
    

Ci troviamo nel livello L3.

- Livello .
    
    ![Untitled](0%20Introduzione/Untitled%202.png)
    
    ![Untitled](0%20Introduzione/Untitled%203.png)
    

L3 realizzata su L2 tramite il software del sistema operativo:

L3 comprende tutte le istruzioni di L2 più altre (system call) che permettono di accedere alle funzioni aggiuntive, ossia: lanciare ed eseguire più programmi contemporaneamente, tenere conto dei diversi utenti, creare/modificare/leggere file e raccoglierli in directory.

## Punto di vista del programmatore

Macchina virtuale di livello 3: fornisce operazioni astratte per l’interazione con i dispositivi di I/O e per l’esecuzione contemporanea di più programmi.

I programmatori devono avere familiarità con le funzioni e i servizi del sistema operativo per poter sviluppare software efficienti e affidabili.

- Rappresentazione .
    
    ![Untitled](0%20Introduzione/Untitled%204.png)
    

## Punto di vista del sistema operativo

- 1. **Gestire**: coordina l’uso condiviso delle risorse del sistema (gli hardware) da più programmi. Pro:
    
    ![Untitled](0%20Introduzione/Untitled%205.png)
    
- minimizza tempi morti;
- minimizza le attese;
- 2. **Controllare**: evita che un programma in esecuzione acceda ad informazioni di altri programmi in esecuzione o del S.O.;
    
    ![Untitled](0%20Introduzione/Untitled%206.png)
    
1. **Sistemi operativi diversi**: funzionano in modo diverso. Le system call funzionano diversamente perché sono progettati e realizzati in modo diverso. Quindi il ruolo di gestore e controllore funzionano in modo diverso.

### Intermediario tra programmi e risorse

1. **Risorse del sistema (CPU. memoria, dischi…)**: permette a diversi programmi la condivisione della CPU, della memoria (suddividendola in sezioni), dello spazio sul disco suddividendolo in sezioni separate e assegnate a utenti diversi, vari dispositivi I/O;
2. **Evita le interferenze**: garantisce che i programmi in esecuzione:
- non interferiscano con il S.O.;
- non monopolizzano le risorse;
- non interferiscano tra loro.

## Modalità di accesso

Il SO vero e proprio è il così detto kernel eseguito in modalità kernel, a differenza del codice dei programmi eseguiti in modalità utente. 

Modalità kernel:

- stampare;
- controllare l’hardware;
- controllare processi: creare, finire, tempi;
- accedere ad indirizzi di memoria riservati al S.O.

Modalità utente

- accedere ai file;
- eseguire applicazioni;
- eseguire operazioni di I/O;
- usare periferiche.

### Modalità kernel

Si passa dalla modalità kernel all’eseguire il codice del S.O:

**Chiamata di sistema**

servizi del S.O. (aprire o scrivere dati di/in un file)

**Trap**

istruzioni che entrano nel kernel (notificare eccezioni)

**Interruzione**

eventi causati dall’hardware (operazioni di I/O)

Nei S.O. con architetture microkernel, solo alcune funzioni “minime” del S.O. fanno parte del kernel, altri moduli girano in modalità utente, rendendo il S.O. più robusto.

Le operazioni “delicate” sono effettuate da una piccola parte del codice, sperando di renderlo più facilmente privo di bug.

<aside>
<img src="https://www.notion.so/icons/computer-chip_gray.svg" alt="https://www.notion.so/icons/computer-chip_gray.svg" width="40px" /> Il sistema operativo fa da intermediario tra programmi e risorse e permette l’esecuzione protetta e simultanea di più programmi

</aside>