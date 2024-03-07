import os
import csv

# Chemin vers le répertoire contenant les fichiers ZIP
repo_dir = r"C:\Users\jpn\Desktop\GitExtract"



import os


def list_files(directory):
    """Retourne une liste des fichiers dans le répertoire spécifié."""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(root, filename), start=directory))
    return files


def compare_directories(dirA, dirB):
    """Compare les fichiers entre deux répertoires et retourne les fichiers qui sont dans dirA mais pas dans dirB."""
    files_in_A = set(list_files(dirA))
    files_in_B = set(list_files(dirB))
    return files_in_A - files_in_B


if __name__ == "__main__":
    directory_A = r"C:\Users\jpn\Desktop\dumpGitExtract"  # Chemin absolu ou relatif du répertoire A
    directory_B = r"C:\Users\jpn\Desktop\GitExtract"  # Chemin absolu ou relatif du répertoire B

    differing_files = compare_directories(directory_A, directory_B)

    print("Fichiers présents dans {} mais pas dans {} :".format(directory_A, directory_B))
    for file_path in differing_files:
        print(file_path)
