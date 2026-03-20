"""Your rig modules live here. Keep it lean."""
__all__ = []  # 不主動 import 子模組，啟動更乾淨

# 可選：開發期一鍵重載（不想要就刪掉這段）
def refresh():
    import importlib, sys
    prefix = __name__ + "."
    for name, mod in list(sys.modules.items()):
        if name.startswith(prefix):
            try:
                importlib.reload(mod)
            except Exception:
                pass

