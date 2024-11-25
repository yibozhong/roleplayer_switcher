import os
import requests
import zipfile
from pathlib import Path

def download_live2d_model():
    # 创建模型目录
    model_dir = Path('live2d-widget/assets')
    model_dir.mkdir(parents=True, exist_ok=True)

    # 使用替代的模型源
    model_url = "https://github.com/guansss/pixi-live2d-display/archive/refs/heads/master.zip"
    response = requests.get(model_url, stream=True)
    
    if response.status_code == 200:
        # 保存zip文件
        zip_path = model_dir / "live2d_models.zip"
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(model_dir)
        
        # 移动模型文件到正确的位置
        source_dir = model_dir / "pixi-live2d-display-master/examples/models"
        if source_dir.exists():
            for model_folder in source_dir.iterdir():
                if model_folder.is_dir():
                    target_dir = model_dir / model_folder.name
                    if target_dir.exists():
                        import shutil
                        shutil.rmtree(target_dir)
                    shutil.move(str(model_folder), str(target_dir))
        
        # 清理临时文件
        os.remove(zip_path)
        import shutil
        shutil.rmtree(str(model_dir / "pixi-live2d-display-master"))
        
        print("Live2D模型设置完成！")
    else:
        print(f"下载失败，状态码: {response.status_code}")

if __name__ == "__main__":
    download_live2d_model()
