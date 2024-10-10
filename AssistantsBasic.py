# AssistantsBasic.py
from openai import OpenAI

client = OpenAI()

# Creamos un agente 
assitant = client.beta.assistants.create(
    name="Jarvis",
    instructions="Eres un tutor personal de Matematica. Escribe y ejecuta codigo para responder preguntas matematicas.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o-mini-2024-07-18"
)

# Creamos un thread
thread = client.beta.threads.create()

# Agreamos un mensaje al thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Necesito resolver la ecuacion `3x**2 + 2x + 11 = 130`. Puedes ayudarme?"
)

# Ejecutamos
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assitant.id,
    instructions="Dirigite al usuario como Emeric Espiritu. El usuario tiene una cuenta premium"
)

# Listamos los mensajes
if run.status == "completed":
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    print("Mensajes...")
    for m in messages.data:
        print("\n",m)
else:
    print("Estatus...")
    print(run.status)