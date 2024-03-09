import gradio as gr
from agent import coder_agent_model

if __name__ == '__main__':
    iface = gr.ChatInterface(coder_agent_model)
    iface.launch()


# import draft.test