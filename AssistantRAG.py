#AssistantRAG.py
from openai import OpenAI

from typing_extensions import override
from openai import AssistantEventHandler, OpenAI

client = OpenAI()

# Paso 1: Creamos el agente
assistant = client.beta.assistants.create(
    name="AI Genius",
    instructions="Eres un experto en Inteligencia Artificial, usa tu conocimiento base para responder a las preguntas de investigacion en IA",
    model="gpt-4o-mini-2024-07-18",
    tools=[{"type": "file_search"}]
)

# Paso 2: Creamos una almacenamiento de vectores
vector_store = client.beta.vector_stores.create(name="AI Scientist")

file_paths = ["files/IA_Singularity.pdf"]
file_streams = [open(path, "rb") for path in file_paths]

file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id,
    files=file_streams
)

print(file_batch.status)
print(file_batch.file_counts)

# Paso 3: Actualizamos el asistente para el uso de Vector Store
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={
        "file_search": { "vector_store_ids": [vector_store.id]}
    }
)

# Paso 4: Creamos un thread de conversacion con un archivo adicional subido por el usuario
message_file = client.files.create(
    file=open("files/Engineering_LLM_From_Scratch.pdf", "rb"),
    purpose="assistants"
)

# Mensaje con adjunto
thread = client.beta.threads.create(
    messages=[
        {
            "role":"user",
            "content": "Cuantas tareas SOTA se usaron en la comparacion para evaluar el modelo",
            "attachments": [
                { "file_id": message_file.id, "tools": [{"type": "file_search"}]}
            ]
        }
    ]
)

# Mensaje sin adjunto
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Resumeme los puntos mas relevantes de la investigacion sobre la singularidad tecnologica que propone el autor en el documento: IA_Singularity.pdf"
)

print("Pre resultado---------------------------")
print(thread.tool_resources.file_search)

# Paso 5: Creamos un Runner y verificamos la salida
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:
        # print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        print("\n".join(citations))

# Then, we use the stream SDK helper
# with the EventHandler class to create the Run
# and stream the response.

with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Dirigete al usuario como Emeric Espiritu. El usuario tiene una cuenta premium.",
    event_handler=EventHandler(),
) as stream:
    stream.until_done()
