import subprocess
import sys
import os
import platform

# 国内镜像源配置
MIRROR_SOURCES = {
    "清华": "https://pypi.tuna.tsinghua.edu.cn/simple/",
    "阿里云": "https://mirrors.aliyun.com/pypi/simple/", 
    "豆瓣": "https://pypi.douban.com/simple/",
    "中科大": "https://pypi.mirrors.ustc.edu.cn/simple/",
    "华为云": "https://repo.huaweicloud.com/repository/pypi/simple/"
}

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print("❌ 需要Python 3.12或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
    return True

def select_mirror():
    """选择镜像源"""
    print("\n=== 选择镜像源 ===")
    print("可用的国内镜像源：")
    sources = list(MIRROR_SOURCES.items())
    
    for i, (name, url) in enumerate(sources, 1):
        print(f"{i}. {name}: {url}")
    
    while True:
        try:
            choice = input(f"\n请选择镜像源 (1-{len(sources)}) [默认: 1-清华]: ").strip()
            if not choice:
                choice = "1"
            
            index = int(choice) - 1
            if 0 <= index < len(sources):
                selected_name, selected_url = sources[index]
                print(f"✅ 已选择: {selected_name} - {selected_url}")
                return selected_url
            else:
                print(f"❌ 请输入 1-{len(sources)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效的数字")

def test_mirror_speed(mirror_url):
    """测试镜像源连接速度"""
    print(f"\n🔍 测试镜像源连接: {mirror_url}")
    try:
        import time
        import urllib.request
        
        start_time = time.time()
        response = urllib.request.urlopen(mirror_url, timeout=10)
        end_time = time.time()
        
        if response.status == 200:
            speed = end_time - start_time
            print(f"✅ 连接成功，响应时间: {speed:.2f}秒")
            return True
        else:
            print(f"❌ 连接失败，状态码: {response.status}")
            return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

def install_package(package, mirror_url, upgrade=False):
    """使用指定镜像源安装Python包"""
    try:
        cmd = [sys.executable, "-m", "pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        cmd.extend(["-i", mirror_url])
        cmd.append("--trusted-host")
        # 提取主机名
        from urllib.parse import urlparse
        hostname = urlparse(mirror_url).hostname
        cmd.append(hostname)
        cmd.append(package)
        
        print(f"📦 正在安装 {package}...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 安装失败: {e.stderr}")
        return False

def install_from_requirements(mirror_url):
    """从requirements.txt安装所有依赖"""
    requirements_files = ["requirements.txt", "requirements-core.txt"]
    
    for req_file in requirements_files:
        if os.path.exists(req_file):
            print(f"📋 找到依赖文件: {req_file}")
            try:
                cmd = [
                    sys.executable, "-m", "pip", "install", 
                    "-r", req_file,
                    "-i", mirror_url
                ]
                # 添加信任主机
                from urllib.parse import urlparse
                hostname = urlparse(mirror_url).hostname
                cmd.extend(["--trusted-host", hostname])
                
                print(f"📦 正在从 {req_file} 安装依赖包...")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print("✅ 所有依赖包安装成功")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ 从 {req_file} 安装依赖包失败: {e.stderr}")
                continue
    
    print("❌ 找不到 requirements.txt 或 requirements-core.txt 文件")
    return False

def configure_pip_permanently(mirror_url):
    """永久配置pip使用国内镜像源"""
    try:
        # 获取pip配置目录
        if platform.system() == "Windows":
            pip_dir = os.path.expanduser("~/pip")
            config_file = os.path.join(pip_dir, "pip.ini")
        else:
            pip_dir = os.path.expanduser("~/.pip")
            config_file = os.path.join(pip_dir, "pip.conf")
        
        # 创建配置目录
        os.makedirs(pip_dir, exist_ok=True)
        
        # 获取主机名
        from urllib.parse import urlparse
        hostname = urlparse(mirror_url).hostname
        
        # 配置内容
        config_content = f"""[global]
index-url = {mirror_url}
trusted-host = {hostname}
timeout = 120
"""
        
        # 写入配置文件
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)
        
        print(f"✅ pip配置已保存到: {config_file}")
        print("   以后使用pip安装包时将自动使用该镜像源")
        return True
        
    except Exception as e:
        print(f"❌ 配置pip失败: {e}")
        return False

def setup_chinese_fonts():
    """设置中文字体支持"""
    system = platform.system()
    font_paths = []
    
    if system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc", 
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simkai.ttf"
        ]
    elif system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/Library/Fonts/Songti.ttc"
        ]
    elif system == "Linux":
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
    
    available_fonts = [path for path in font_paths if os.path.exists(path)]
    
    if available_fonts:
        print(f"✅ 找到中文字体: {available_fonts[0]}")
        return available_fonts[0]
    else:
        print("⚠️ 未找到中文字体，词云可能显示异常")
        print("建议安装中文字体包")
        return None

def test_imports():
    """测试关键包的导入"""
    test_packages = [
        ("pandas", "pd"),
        ("numpy", "np"),
        ("matplotlib.pyplot", "plt"),
        ("jieba", None),
        ("snownlp", None),
        ("wordcloud", None),
        ("sklearn", None),
        ("seaborn", "sns")
    ]
    
    print("\n=== 测试包导入 ===")
    failed_imports = []
    
    for package, alias in test_packages:
        try:
            if alias:
                exec(f"import {package} as {alias}")
            else:
                exec(f"import {package}")
            print(f"✅ {package} 导入成功")
        except ImportError as e:
            print(f"❌ {package} 导入失败: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n⚠️ 失败的包: {', '.join(failed_imports)}")
        print("建议重新安装这些包")
    
    return len(failed_imports) == 0

def create_config_file():
    """创建配置文件"""
    config_content = """# 文本分析配置文件
analysis:
  # 评论采样大小（用于性能优化）
  comment_sample_size: 5000
  
  # 关键词提取数量
  top_keywords: 20
  
  # 情感分析阈值
  positive_threshold: 0.6
  negative_threshold: 0.4
  
  # 词云配置
  wordcloud:
    width: 800
    height: 400
    max_words: 100
    background_color: "white"
    colormap: "viridis"

visualization:
  # 图表样式
  figure_size: [15, 12]
  dpi: 100
  
  # 字体设置
  font_family: "SimHei"
  
output:
  # 输出目录
  results_dir: "results"
  
  # 图片格式
  image_format: "png"
  
  # 保存分析结果
  save_results: true
"""
    
    try:
        with open("config.yaml", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ 配置文件 config.yaml 创建成功")
        return True
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False

def main():
    """主安装流程"""
    print("🚀 开始环境配置...")
    print("   使用国内镜像源加速安装")
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 选择镜像源
    mirror_url = select_mirror()
    
    # 测试镜像源连接
    if not test_mirror_speed(mirror_url):
        print("⚠️ 镜像源连接测试失败，但继续尝试安装...")
    
    # 询问是否永久配置
    config_choice = input("\n是否永久配置pip使用该镜像源? (y/N): ").strip().lower()
    if config_choice in ['y', 'yes']:
        configure_pip_permanently(mirror_url)
    
    # 升级pip
    print("\n=== 升级pip ===")
    install_package("pip", mirror_url, upgrade=True)
    
    # 安装依赖包
    print("\n=== 安装依赖包 ===")
    if not install_from_requirements(mirror_url):
        print("尝试逐个安装核心包...")
        core_packages = [
            "pandas", "numpy", "matplotlib", "seaborn", 
            "jieba", "snownlp", "wordcloud", "scikit-learn",
            "tqdm", "jsonlines", "pyyaml" 
        ]
        
        failed_packages = []
        for package in core_packages:
            if not install_package(package, mirror_url):
                failed_packages.append(package)
        
        if failed_packages:
            print(f"\n⚠️ 以下包安装失败: {', '.join(failed_packages)}")
            print("可以稍后手动安装：")
            for pkg in failed_packages:
                print(f"  pip install -i {mirror_url} {pkg}")
    
    # 设置中文字体
    print("\n=== 检查中文字体 ===")
    setup_chinese_fonts()
    
    # 测试导入
    if test_imports():
        print("\n✅ 所有核心包导入正常")
    else:
        print("\n⚠️ 部分包导入失败，请检查安装")
    
    # 创建配置文件
    print("\n=== 创建配置文件 ===")
    create_config_file()
    
    # 创建必要目录
    dirs_to_create = ["results", "data", "logs"]
    for dir_name in dirs_to_create:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ 目录 {dir_name} 创建完成")
    
    print("\n🎉 环境配置完成！")
    print("\n📋 后续步骤：")
    print("1. 运行文本分析: python text_analysis.py")
    print("2. 查看结果目录: results/")
    print("3. 如需重新配置镜像源，重新运行此脚本")
    
    # 显示快速安装命令
    print(f"\n💡 快速安装命令（使用已选择的镜像源）：")
    print(f"   pip install -i {mirror_url} <package_name>")

if __name__ == "__main__":
    main()