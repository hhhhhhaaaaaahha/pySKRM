# pySKRM

**pySKRM** 是一個以 Python 實作的 *Skyrmion Racetrack Memory (SKRM)* 模擬元件套件。  
它提供核心類別 `SKRM` 與多種寫入策略（`naive_write`, `permutation_write`, `pw_plus`），並追蹤操作的 latency/energy 估計計數。

## 安裝

建議使用虛擬環境：

```bash
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -U pip

安裝套件（開發模式 + 開發依賴）：

pip install -e .[dev]


若只需執行（不開發），可使用：

pip install -e .

快速開始
from pyskrm import SKRM

# 建立一個 8-bit word、共 2 個 words 的 SKRM
sk = SKRM(word_size=8, num_words=2, strategy="naive")

# 基本操作
sk.inject(0)           # 在 AP=0 位置注入
bit = sk.detect(0)     # 偵測 AP=0 是否為 1
sk.shift(0, 1)         # 將資料在 AP=0 → AP=1 間位移
sk.remove(1)           # 移除 AP=1 的內容

# 寫入策略
sk.naive_write(3.14, target_word=0)
# 或 sk.permutation_write(2.71, target_word=0)
# 或 sk.pw_plus(1.23, target_word=0)

# 檢視/統計
sk.visualize()
sk.summarize()

測試

專案內建 pytest 測試。啟用虛擬環境後：

pytest -q
# 或加上覆蓋率報告
pytest -q --cov=pyskrm --cov-report=term-missing

專案結構
src/
  pyskrm/
    __init__.py           # 導出 SKRM、版本資訊
    skrm.py               # 主要類別與策略
    ieee754.py            # IEEE-754 轉換工具
    argument_error.py     # 自訂例外
tests/
  conftest.py
  test_skrm.py
  test_skrm_mock.py
pyproject.toml
README.md

相依

bitarray（執行期）

pytest, pytest-cov（僅開發/測試）

版本

目前版本：0.2.0
使用時可透過下列方式取得：

import pyskrm
print(pyskrm.__version__)

授權

MIT（可依需求調整）


---

如果你之後要補 `ieee754.py`、`argument_error.py` 的更完整說明或 API 文件，我可以幫你在 README 裡再加一節 **API 參考**。等你功能補得更完整、想發佈到 PyPI，再一起處理版本規則與發佈流程就好 🙌
