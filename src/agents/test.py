import ollama

# Initialize the Ollama client
client = ollama.Client()

# Function to format the prompt
def format_prompt(instruction):
    return f"<s>[INST] {instruction} [/INST]"

# Main chat loop
def chat_with_mistral():
    print("Chat with Mistral-7B-Instruct (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        response = client.chat(model="mistral-7b-instruct:latest", 
                               messages=[{"role": "user", "content": format_prompt(user_input)}])
        
        print("Mistral:", response['message']['content'])

if __name__ == "__main__":
    chat_with_mistral()
