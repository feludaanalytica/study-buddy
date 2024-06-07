import subprocess


def vosk_install():
    """installing vosk using the subprocess module using poetry
    """
    subprocess.check_call(["pip", "install", "-r", "requirements.txt"])


if __name__ == "__main__":
    vosk_install()
