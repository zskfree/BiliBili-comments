import json


def read_json_file(file_path):
    """读取JSON文件并返回内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def check_data_format(data, expected_keys):
    """检查数据格式是否符合预期"""
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                return False
            if not all(key in item for key in expected_keys):
                return False
    elif isinstance(data, dict):
        if not all(key in data for key in expected_keys):
            return False
    else:
        return False
    return True

def analyze_data_structure(data, file_name):
    """分析数据结构并输出详细信息"""
    print(f"\n=== {file_name} 数据分析 ===")
    print(f"数据类型: {type(data).__name__}")
    
    if isinstance(data, list):
        print(f"数组长度: {len(data)}")
        if len(data) > 0:
            print(f"第一个元素类型: {type(data[0]).__name__}")
            if isinstance(data[0], dict):
                print(f"第一个元素的键: {list(data[0].keys())}")
                print(f"第一个元素内容预览: {str(data[0])[:200]}...")
                # 检查数据完整性
                missing_data_count = 0
                for item in data:
                    if any(v is None or v == '' for v in item.values()):
                        missing_data_count += 1
                print(f"包含空值或缺失数据的记录数: {missing_data_count}")
    elif isinstance(data, dict):
        print(f"字典键: {list(data.keys())}")
        print(f"内容预览: {str(data)[:200]}...")
    
    print("-" * 50)

def main():
    files = [
        'data/search_comments_2025-07-14.json',
        'data/search_contents_2025-07-14.json',
        'data/search_creators_2025-07-14.json'
    ]
    
    # 根据实际数据结构更新预期字段
    expected_keys = {
        'search_comments_2025-07-14': ['comment_id', 'video_id', 'content', 'user_id', 'nickname', 'create_time'],
        'search_contents_2025-07-14': ['video_id', 'title', 'desc', 'user_id', 'nickname', 'create_time'],
        'search_creators_2025-07-14': ['user_id', 'nickname', 'sex', 'sign', 'avatar', 'total_fans']
    }
    
    for file in files:
        try:
            data = read_json_file(file)
            # 修复文件类型提取逻辑
            file_type = file.split('/')[-1].split('.')[0]  # 获取完整的文件名（不含扩展名）
            
            # 分析数据结构
            analyze_data_structure(data, file)
            
            if file_type in expected_keys:
                if check_data_format(data, expected_keys[file_type]):
                    print(f"✅ {file} 数据格式正确，包含所有必需字段")
                else:
                    print(f"❌ {file} 数据格式错误或缺少必需字段")
                    # 详细检查缺失的字段
                    if isinstance(data, list) and len(data) > 0:
                        missing_keys = set(expected_keys[file_type]) - set(data[0].keys())
                        if missing_keys:
                            print(f"   缺失字段: {list(missing_keys)}")
            else:
                print(f"⚠️  {file} 未定义预期格式，跳过格式检查")
                
        except FileNotFoundError:
            print(f"❌ 文件 {file} 不存在")
        except json.JSONDecodeError:
            print(f"❌ 文件 {file} JSON格式错误")
        except Exception as e:
            print(f"❌ 处理文件 {file} 时发生错误: {e}")

if __name__ == "__main__":
    main()
