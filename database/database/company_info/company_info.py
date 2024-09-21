def read_companies(filename):
    with open(filename, 'r') as file:
        return set(line.strip().upper() for line in file)

def write_companies(filename, companies):
    with open(filename, 'w') as file:
        for company in sorted(companies):
            file.write(f"{company}\n")

def compare_companies(file1, file2):
    companies1 = read_companies(file1)
    companies2 = read_companies(file2)

    file1_unique = companies1 - companies2
    file2_unique = companies2 - companies1
    common = companies1 & companies2

    write_companies('file1_unique.txt', file1_unique)
    write_companies('file2_unique.txt', file2_unique)
    write_companies('common.txt', common)

    print(f"Companies unique to {file1}: {len(file1_unique)}")
    print(f"Companies unique to {file2}: {len(file2_unique)}")
    print(f"Companies in both files: {len(common)}")
    print(f"Total companies in db: {len(file1_unique) + len(file2_unique) + len(common)}")


compare_companies('companies_1.txt', 'companies_2.txt')