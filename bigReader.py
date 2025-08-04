import datetime
import kagglehub

# Download latest version
path = kagglehub.dataset_download("tavuksuzdurum/user-animelist-dataset")

print("Path to dataset files:", path)
f = "sptech.txt"

def createFile(text):
    with open(f, 'w') as file:
        file.write(text * 100_000_000)


createFile("Sptech irada - ")
def reader():
    with open(f, 'r') as file:
        print(f"Start time: {datetime.datetime.now()}")
        file.read(101)
        print(file.read(1))

        print(file.read(10))
    print(f"Finish TIme: {datetime.datetime.now()}")

reader()
