import streamlit as st
import speech_recognition as srpi

# Função para transcrever áudio
def transcrever_audio():
    recognizer = sr.Recognizer()
    with sr.AudioFile('audio1.ogg') as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language='pt-BR')
    except sr.UnknownValueError:
        return "Áudio não entendido"
    except sr.RequestError:
        return "Erro na transcrição"

# Função principal da aplicação
def main():
    st.title("Central de Ordens de Serviço")

    # Seção para inserir texto da ordem de serviço
    ordem_texto = st.text_area("Descrição da Ordem de Serviço", placeholder="Digite ou cole o texto da ordem de serviço...")

    # Seção para transcrição de áudio
    if st.button("Carregar e Transcrever Áudio"):
        transcricao = transcrever_audio()
        st.write("Transcrição do Áudio:", transcricao)

    # Checklist interativo
    st.subheader("Checklist de Etapas")
    checklist = {
        "Receber a ordem de serviço": False,
        "Ler e entender a ordem": False,
        "Marcar como concluída": False,
        "Finalizar a ordem": False
    }

    for etapa, concluido in checklist.items():
        checklist[etapa] = st.checkbox(etapa, value=concluido)

    # Exibir status das etapas
    st.write("Etapas Concluídas:" if any(checklist.values()) else "Nenhuma etapa concluída ainda.")
    for etapa, concluido in checklist.items():
        if concluido:
            st.write(f"✓ {etapa}")

    # Notificações de etapas
    if all(checklist.values()):
        st.success("Todas as etapas foram concluídas!")

if __name__ == "__main__":
    main()