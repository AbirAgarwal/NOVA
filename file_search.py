import os


def find_file(keyword):

    matches = []

    for root, dirs, files in os.walk("."):

        for file in files:

            if keyword.lower() in file.lower():

                matches.append(
                    os.path.join(root, file)
                )

    if not matches:
        return "No matching files found."

    return "\n".join(matches[:20])


def open_file(keyword):

    for root, dirs, files in os.walk("."):

        for file in files:

            if keyword.lower() in file.lower():

                path = os.path.join(
                    root,
                    file
                )

                os.startfile(path)

                return f"Opening {file}"

    return "No matching file found."

def open_folder(keyword):

    import os

    for root, dirs, files in os.walk("."):

        for folder in dirs:

            if keyword.lower() in folder.lower():

                path = os.path.join(
                    root,
                    folder
                )

                os.startfile(path)

                return f"Opening folder {folder}"

    return "No matching folder found."