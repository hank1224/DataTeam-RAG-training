from bs4 import BeautifulSoup
import json

def chinese_to_arabic(chinese_num):
    chinese_to_digit = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '十': 10
    }
    if chinese_num == '十':
        return 10
    result = 0
    if '十' in chinese_num:
        parts = chinese_num.split('十')
        if parts[0] == '':
            result += 10
        else:
            result += chinese_to_digit[parts[0]] * 10
        if parts[1] != '':
            result += chinese_to_digit[parts[1]]
    else:
        result = chinese_to_digit[chinese_num]
    return result

def parse_law_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    metadata = []
    current_part = {"number": None, "title": None}
    current_chapter = {"number": None, "title": None}
    current_section = {"number": None, "title": None}
    current_subsection = {"number": None, "title": None}
    current_item = {"number": None, "title": None}

    def extract_number_from_text(text):
        chinese_num = text.split(' ')[1]
        return chinese_to_arabic(chinese_num)

    for element in soup.find_all(["div", "a"]):
        if "class" in element.attrs:
            classes = element.attrs["class"]
            if "h3" in classes:
                text = element.get_text(strip=True)
                number = extract_number_from_text(text)
                if "char-1" in classes:
                    current_part = {"number": number, "title": text}
                    # Reset lower levels
                    current_chapter = {"number": None, "title": None}
                    current_section = {"number": None, "title": None}
                    current_subsection = {"number": None, "title": None}
                    current_item = {"number": None, "title": None}
                elif "char-2" in classes:
                    current_chapter = {"number": number, "title": text}
                    # Reset lower levels
                    current_section = {"number": None, "title": None}
                    current_subsection = {"number": None, "title": None}
                    current_item = {"number": None, "title": None}
                elif "char-3" in classes:
                    current_section = {"number": number, "title": text}
                    # Reset lower levels
                    current_subsection = {"number": None, "title": None}
                    current_item = {"number": None, "title": None}
                elif "char-4" in classes:
                    current_subsection = {"number": number, "title": text}
                    # Reset lower level
                    current_item = {"number": None, "title": None}
                elif "char-5" in classes:
                    current_item = {"number": number, "title": text}
            elif "col-no" in classes:
                article_number = element.get_text(strip=True).replace("第 ", "").replace(" 條", "")
                article_title = element.get_text(strip=True)
                source_url = element.find("a")["href"]

                article_content = []
                next_col_data = element.find_next_sibling("div", class_="col-data")
                if next_col_data:
                    temp_content = []
                    for line in next_col_data.find_all("div", class_="line-0000"):
                        if temp_content:
                            article_content.append(''.join(temp_content))
                            temp_content = []
                        temp_content.append(line.get_text(strip=True))
                        for subline in line.find_next_siblings("div", class_="line-0004"):
                            temp_content.append(subline.get_text(strip=True)[2:])  # Remove the number prefix
                    if temp_content:
                        article_content.append(''.join(temp_content))

                metadata.append({
                    "article_number": article_number,
                    "article_title": article_title,
                    "artcile_content": article_content,
                    "part_number": current_part["number"],
                    "part_title": current_part["title"],
                    "chapter_number": current_chapter["number"],
                    "chapter_title": current_chapter["title"],
                    "section_number": current_section["number"],
                    "section_title": current_section["title"],
                    "subsection_number": current_subsection["number"],
                    "subsection_title": current_subsection["title"],
                    "item_number": current_item["number"],
                    "item_title": current_item["title"],
                    "source_url": source_url
                })

    return metadata

def save_metadata_to_json(metadata, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(metadata, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    html_file_path = '1223-MultiHop-RAG/data-pre-process/民法-110-01-20.html'
    output_json_path = '1223-MultiHop-RAG/data-pre-process/民法-110-01-20-metadata.json'

    metadata = parse_law_html(html_file_path)
    save_metadata_to_json(metadata, output_json_path)
    print("Metadata extraction complete. Saved to", output_json_path)
