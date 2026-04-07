import sys

# Importiamo dai nostri moduli puliti
from src.pipeline.orchestrator import run_pipeline
from src.agents.chat_agent import chat_with_brain
from src.database.visualizer import visualize_3d_chroma

def menu():
    print("\n🧠 BENVENUTO NEL TUO SECOND BRAIN AI")
    print("====================================")
    print("1. 📝 Processa note in Inbox (Orchestrator)")
    print("2. 💬 Chatta con le tue note (RAG)")
    print("3. 🌌 Visualizza Mappa 3D del Vault")
    print("4. ❌ Esci")
    
    scelta = input("\nCosa vuoi fare? [1/2/3/4]: ")
    return scelta

def main():
    while True:
        scelta = menu()
        
        if scelta == '1':
            import glob
            # Peschiamo le note grezze dalla cartella "raw_notes"
            note_grezze = glob.glob("raw_notes/*.md")
            if not note_grezze:
                print("Nessuna nota da processare in 'raw_notes/'.")
            for nota in note_grezze:
                run_pipeline(nota)
                
        elif scelta == '2':
            print("Scrivi 'exit' per tornare al menu principale.")
            while True:
                domanda = input("\nFai una domanda al tuo Vault: ")
                if domanda.lower() == 'exit':
                    break
                chat_with_brain(domanda)
                
        elif scelta == '3':
            visualize_3d_chroma()
            
        elif scelta == '4':
            print("Uscita in corso... Ciao! 👋")
            sys.exit(0)
            
        else:
            print("Scelta non valida, riprova.")

if __name__ == "__main__":
    main()