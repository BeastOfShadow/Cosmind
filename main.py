import sys

# Import from our clean modules
from src.pipeline.orchestrator import run_pipeline
from src.agents.chat_agent import chat_with_brain
from src.database.visualizer import visualize_3d_chroma
from src.database.vector_db import sync_notes

def menu():
    print("\n🧠 WELCOME TO COSMIND")
    print("====================================")
    print("1. 📝 Process notes in Inbox (Orchestrator)")
    print("2. 💬 Chat with your notes (RAG)")
    print("3. 🌌 Visualize 3D Map of the Vault")
    print("4. 🔄 Sync local Database (Sync)")
    print("5. ❌ Exit")

    scelta = input("\nWhat do you want to do? [1/2/3/4/5]: ")
    return scelta

def main():
    while True:
        scelta = menu()
        
        if scelta == '1':
            import glob
            # Pick up the raw notes from the "raw_notes" folder
            note_grezze = glob.glob("raw_notes/*.md")
            if not note_grezze:
                print("No notes to process in 'raw_notes/'.")
            for nota in note_grezze:
                run_pipeline(nota)

        elif scelta == '2':
            print("Type 'exit' to return to the main menu.")
            while True:
                domanda = input("\nAsk a question to your Vault: ")
                if domanda.lower() == 'exit':
                    break
                chat_with_brain(domanda)

        elif scelta == '3':
            visualize_3d_chroma()

        elif scelta == '4':
            print("\n🔄 Syncing the database...")
            sync_notes()

        elif scelta == '5':
            print("Exiting... Bye! 👋")
            sys.exit(0)

        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()