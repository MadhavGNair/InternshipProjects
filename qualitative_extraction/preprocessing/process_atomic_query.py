def process_atomic_query(file_path):
    """
    Process the given text file to remove all text after the first question mark
    in each line and save the result in the same file.
    
    :param file_path: Path to the text file to be processed
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # process each line to remove text after the first question mark
    processed_lines = []
    for line in lines:
        if '?' in line:
            # find the index of the first question mark and keep text up to that point
            processed_line = line[:line.find('?') + 1]
        else:
            processed_line = line
        processed_lines.append(processed_line)

    # Write the processed lines back to the file
    with open(file_path, 'w') as file:
        file.write("\n".join(processed_lines))

    print("Processing complete. The file has been updated.")