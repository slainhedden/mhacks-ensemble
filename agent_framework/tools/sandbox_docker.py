import os
import llm_sandbox 
import docker

def run_code_in_sandbox(codeFile, testFile = "", language="python", libraries=[]):
    """
    Run code in a sandboxed environment using Docker containers for different languages.
    :param language: The language of the code.
    :param code: The code to run.
    :param libraries: The libraries to use inside both files (if applicable for the language).
    :return: The output of the code.
    """
    
    # Define the base command for each language
    language_commands = {
        "python": ["python3"],
        "cpp": ["bash", "-c", "g++ -o main main.cpp && ./main"],
        "java": ["bash", "-c", "javac Main.java && java Main"],
        "javascript": ["node"],
        "go": ["go", "run"],
        "ruby": ["ruby"]
    }
    
    # Define the Docker image to use for each language
    language_images = {
        "python": "python:3.9.19-bullseye",
        "cpp": "gcc",
        "java": "openjdk",
        "javascript": "node",
        "go": "golang",
        "ruby": "ruby"
    }

    # If languages have no application
    if language not in language_commands:
        raise ValueError(f"Unsupported language: {language}")

    # Use the corresponding Docker image for the language
    image = language_images.get(language)


    tls_config =  docker.tls.TLSConfig(
        client_cert=("/Users/samhedden/mhacks-ensemble/agent_framework/tools/AWS/cert.pem", "/Users/samhedden/mhacks-ensemble/agent_framework/tools/AWS/key.pem"),
        ca_cert="/Users/samhedden/mhacks-ensemble/agent_framework/tools/AWS/ca.pem",
        verify=True
    )
    try:
        # Read content from codeFile
        codePath = os.path.join("agentFiles/src", codeFile)
        with open(codePath, 'r') as codefp:
            codeText = codefp.read()

        # Run the Docker container with the code
        docker_client = docker.DockerClient(base_url="tcp://3.149.240.104:5432", tls=tls_config)
        with llm_sandbox.SandboxSession(client=docker_client, image=image, lang = language, verbose = True) as sandbox:
            # Run the code in the sandbox
            result = sandbox.run(codeText, libraries).text  
            print(result)          
            return result
    except:
        raise("ERROR: Code is not compatible for Sandbox.")
        
run_code_in_sandbox("ok.py")