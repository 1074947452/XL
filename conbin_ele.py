def merge_txt_files(file1, file2, output_file):
    try:
        with open(file1, 'r', encoding='utf-8') as f1, \
             open(file2, 'r', encoding='utf-8') as f2, \
             open(output_file, 'w', encoding='utf-8') as out:
            content1 = f1.read()
            content2 = f2.read()
            out.write(content1 + '\n\n' + content2)
        print(f"已成功将 {file1} 和 {file2} 合并为 {output_file}")
    except Exception as e:
        print(f"合并文件出错: {e}")
if __name__ == "__main__":
    merge_txt_files("elements_llm.txt", "elements_url.txt", "elements_all.txt")
