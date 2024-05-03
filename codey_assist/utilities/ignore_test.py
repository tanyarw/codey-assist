# Example usage
root_directory = "/Users/tanyawarrier/Desktop/projects/codey-assist"
ignore_patterns_dict = get_ignore_patterns_dict(root_directory)



for dirpath, dirnames, filenames in os.walk(root_directory):
    for filename in filenames:
        file = os.path.join(dirpath, filename)

        if not should_ignore(file, ignore_patterns_dict):
            print(f"Not ignoring: {file}")
