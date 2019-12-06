
import os


def tick():
    version_str = "1.3.0"
    with open("version.txt", "r") as f:
        version_str = f.readline()


    version = [int(x) for x in version_str.split(".")]
    version[2] += 1
    version_str = ".".join([str(x) for x in version])

    with open("version.txt", "w") as f:
        f.write(version_str)

    return version_str


def tick_python(path, version):
    file_path = f"{path}/setup.py"
    with open(file_path, "r") as f:

        lines = [line for line in f]
        for i in range(0, len(lines)):
            line = lines[i]
            if line.strip().startswith("VERSION"):
                line = f"VERSION = '{version}'\n"
                lines[i] = line

    with open(file_path, "w") as f:
        f.write("".join(lines))


def tick_dotnet(path, version):
    full_path = os.path.dirname(path+"/")
    assembly_name = os.path.basename(full_path)
    csproj_path = f"{full_path}/{assembly_name}.csproj"

    with open(csproj_path, "r") as f:

        lines = [line for line in f]
        for i in range(0, len(lines)):
            line = lines[i]
            if line.strip().startswith("<Version>"):
                line = f"\t\t<Version>{version}</Version>\n"
                lines[i] = line

    with open(csproj_path, "w") as f:
        f.write("".join(lines))


version = tick()
tick_python("src/hyper-model", version)
