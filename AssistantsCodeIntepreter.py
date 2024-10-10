from openai import OpenAI

from openai.types.beta.threads import Text, TextDelta
from typing_extensions import override
from openai import AssistantEventHandler

client = OpenAI()

# Cargamos el archivo a procesar
file = client.files.create(
    file=open("aproach_ai.csv", "rb"),
    purpose="assistants"
)

# Creamos el asistente
assitant = client.beta.assistants.create(
    name="Skynet",
    description="Eres un gran asistente de creacion de visulizacion de datos, tu analisis los datos de archivos CSV, comprende los patrones, visualizas los datos relevantes de esos patrones y tambien compartes un breve resumen de esos patrones observados",
    model="gpt-4o-mini-2024-07-18",
    tools=[{"type": "code_interpreter"}],
    tool_resources={
        "code_interpreter": {
            "file_ids": [file.id]
        }
    }
)

thread = client.beta.threads.create(
    messages=[{
        "role": "user",
        "content": "Crear 3 visulizaciones de datos basados en los patrones en este archivo",
        "attachments":[{
            "file_id":file.id,
            "tools": [{"type": "code_interpreter"}]
        }]
    }]
)

# Creamos un manejador de evemnto para el Streaming
class EvenHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassitant text created > {text}:", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot) -> None:
        print(delta.value, end="", flush=True)
        #print(f"\nSnapshot:{snapshot}")
    
    @override
    def on_tool_call_created(self, tool_call) -> None:
        print(f"\nassitant tool call created > {tool_call.type}\n", flush=True)
    
    @override
    def on_tool_call_delta(self, delta, snapshot) -> None:
        if delta.type == "code_interpreter":
            if delta.code_interpreter.input:
                print(f"\n Tool call Delta Input> {delta.code_interpreter.input}", end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n Tool call Delta Outputs> {delta.code_interpreter.outputs}", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n Logs > {output.logs}", flush=True)

# Ejecutamos en modo Streaming
with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assitant.id,
    instructions="Dirigite al usuario como Emeric Espiritu. El usuario tiene una cuenta premium",
    event_handler=EvenHandler(),
) as stream:
    stream.until_done()

        
