import csv

# 输入和输出的 CSV 文件名
input_csv_filename = "ll_traindata.csv"
output_csv_filename = "ll_deal.csv"

# 读取输入的 CSV 文件并根据条件筛选行
selected_rows = []
with open(input_csv_filename, "r", newline="", encoding="utf-8") as input_csvfile:
    reader = csv.DictReader(input_csvfile)
    for row in reader:
        if row["intent"] == "knowledge_query":
            selected_rows.append(row)

# 将满足条件的行写入新的 CSV 文件
with open(output_csv_filename, "w", newline="", encoding="utf-8") as output_csvfile:
    fieldnames = ["text", "intent"]
    writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(selected_rows)

print(f"满足条件的行已保存到 {output_csv_filename} 文件中。")
