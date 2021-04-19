from cx_Freeze import setup, Executable

# On appelle la fonction setup
setup(
    name = "serveur_chat",
    version = "1",
    description = "programme server",
    executables = [Executable("server.py")],
)