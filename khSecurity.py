# coding: utf-8
"""
安全验证模块

提供策略代码安全验证、路径规范化和下载文件验证功能。

功能：
1. 策略代码AST白名单验证 - 防止恶意代码执行
2. 安全路径解析 - 防止路径遍历攻击
3. 文件下载验证 - 防止下载恶意文件

@author: OsKhQuant
@version: 1.0
"""

import ast
import re
import os
import hashlib
import requests
from pathlib import Path
from typing import Tuple, List, Dict, Optional, Union
from datetime import datetime

import logging

logger = logging.getLogger('OsKhQuant.security')


class SecurityError(Exception):
    """安全错误异常"""
    def __init__(self, message: str, details: Dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class StrategySecurityValidator:
    """策略代码安全验证器

    使用AST解析和白名单机制验证策略代码的安全性。
    """

    # 允许的节点类型（白名单）
    ALLOWED_NODES = {
        'Module', 'Expr', 'Assign', 'Name', 'Constant', 'Num',
        'BinOp', 'Add', 'Sub', 'Mult', 'Div', 'Mod', 'FloorDiv', 'Pow',
        'Load', 'Call', 'FunctionDef', 'AsyncFunctionDef', 'If', 'For',
        'While', 'Return', 'Continue', 'Break', 'Pass',
        'Compare', 'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot',
        'And', 'Or', 'Not', 'UnaryOp', 'USub', 'UAdd',
        'Subscript', 'Index', 'List', 'Dict', 'Tuple', 'Set',
        'Attribute', 'Slice', 'ExtSlice',
        'arg', 'arguments', 'Return', 'Yield', 'Await',
        'Try', 'ExceptHandler', 'Raise', 'With', 'AsyncWith',
        'BoolOp', 'BinOp',
    }

    # 允许的内置函数
    ALLOWED_BUILTINS = {
        # 基础函数
        'print', 'len', 'range', 'abs', 'max', 'min', 'sum', 'sorted',
        'reversed', 'zip', 'enumerate', 'map', 'filter', 'reduce',
        'isinstance', 'type', 'hasattr', 'getattr', 'setattr', 'delattr',
        'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple',
        'round', 'format', 'hex', 'oct', 'bin', 'ord', 'chr',
        'any', 'all', 'divmod', 'pow', 'hash', 'id', 'memoryview',
        'slice', 'property', 'classmethod', 'staticmethod',
        # 量化专用函数
        'khGet', 'khPrice', 'khHas', 'khHistory', 'khBuy', 'khSell',
        'khHandlebar', 'khPreMarket', 'khPostMarket', 'khMA', 'khEMA',
        # 指标计算函数
        'MA', 'EMA', 'SMA', 'DMA', 'AVEDEV', 'DEVA', 'REF', 'SUM',
        'STD', 'BOLL', 'BBI', 'TR', 'ATR', 'CCI', 'KPN',
        'ROC', 'RSI', 'WR', 'KDJ', 'MACD', 'OBV',
        # numpy
        'numpy', 'np',
    }

    # 禁止的模式（黑名单）
    FORBIDDEN_PATTERNS = [
        (r'import\s+os\b', '禁止导入os模块'),
        (r'import\s+sys\b', '禁止导入sys模块'),
        (r'import\s+subprocess\b', '禁止导入subprocess模块'),
        (r'import\s+threading\b', '禁止导入threading模块'),
        (r'import\s+multiprocessing\b', '禁止导入multiprocessing模块'),
        (r'import\s+requests\b', '禁止导入requests模块'),
        (r'import\s+socket\b', '禁止导入socket模块'),
        (r'import\s+ftplib\b', '禁止导入ftplib模块'),
        (r'import\s+telnetlib\b', '禁止导入telnetlib模块'),
        (r'import\s+smtplib\b', '禁止导入smtplib模块'),
        (r'import\s+ctypes\b', '禁止导入ctypes模块'),
        (r'import\s+shutil\b', '禁止导入shutil模块'),
        (r'__import__\s*\(', '禁止使用__import__'),
        (r'\beval\s*\(', '禁止使用eval'),
        (r'\bexec\s*\(', '禁止使用exec'),
        (r'\bcompile\s*\(', '禁止使用compile'),
        (r'os\.system\s*\(', '禁止执行系统命令'),
        (r'os\.popen\s*\(', '禁止执行系统命令'),
        (r'subprocess\.', '禁止使用subprocess'),
        (r'shutil\.', '禁止使用shutil'),
        (r'socket\.', '禁止使用socket'),
        (r'threading\.', '禁止使用多线程'),
        (r'multiprocessing\.', '禁止使用多进程'),
        (r'ctypes\.', '禁止使用ctypes'),
        (r'open\s*\([^)]*[wa]', '禁止文件写入操作'),
        (r'\bopen\s*\([^)]*,\s*["\']w["\']', '禁止写模式打开文件'),
        (r'\bopen\s*\([^)]*,\s*["\']a["\']', '禁止追加模式打开文件'),
        (r'\bopen\s*\([^)]*,\s*["\']wb["\']', '禁止二进制写模式打开文件'),
        (r'urllib\.request', '禁止使用网络请求'),
        (r'urllib3', '禁止使用urllib3'),
    ]

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """验证策略文件安全性

        Args:
            file_path: 策略文件路径

        Returns:
            Tuple[是否通过, 错误列表]
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.validate_code(code, file_path)
        except UnicodeDecodeError:
            return False, ["文件编码不支持，请使用UTF-8编码"]
        except FileNotFoundError:
            return False, [f"文件不存在: {file_path}"]
        except Exception as e:
            return False, [f"读取文件失败: {str(e)}"]

    def validate_code(self, code: str, source_name: str = "unknown") -> Tuple[bool, List[str]]:
        """验证策略代码安全性

        Args:
            code: 策略代码字符串
            source_name: 源码名称（用于错误提示）

        Returns:
            Tuple[是否通过, 错误/警告列表]
        """
        self.errors = []
        self.warnings = []

        if not code or not code.strip():
            return False, ["策略代码为空"]

        # 1. 检查黑名单模式
        if not self._check_forbidden_patterns(code):
            return False, self.errors

        # 2. AST解析检查
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, [f"语法错误: {str(e)}"]
        except Exception as e:
            return False, [f"AST解析错误: {str(e)}"]

        # 3. 检查AST节点类型
        self._check_ast_nodes(tree)

        # 4. 检查函数调用
        self._check_function_calls(tree)

        # 5. 检查import语句
        self._check_imports(tree)

        # 6. 检查危险操作
        self._check_dangerous_ops(tree)

        # 汇总结果
        all_messages = self.errors + self.warnings
        return len(self.errors) == 0, all_messages

    def _check_forbidden_patterns(self, code: str) -> bool:
        """检查禁止的模式"""
        for pattern, message in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
                self.errors.append(message)
        return len(self.errors) == 0

    def _check_ast_nodes(self, tree: ast.AST):
        """检查AST节点类型"""
        for node in ast.walk(tree):
            node_type = type(node).__name__

            if node_type not in self.ALLOWED_NODES:
                # Import相关节点单独处理
                if 'Import' in node_type:
                    continue
                # 危险节点
                elif node_type in {'Exec', 'Eval', 'Compile'}:
                    self.errors.append(f"包含禁止的节点类型: {node_type}")
                # 其他未知节点给出警告
                else:
                    self.warnings.append(f"未知节点类型: {node_type}")

    def _check_function_calls(self, tree: ast.AST):
        """检查函数调用"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # 检查内置函数调用
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name not in self.ALLOWED_BUILTINS:
                        # 检查是否是用户定义的函数（以小写字母开头）
                        if func_name[0].islower() and not func_name.startswith(('_', '__')):
                            # 允许以kh、my、on_开头的函数
                            if not (func_name.startswith('kh') or
                                    func_name.startswith('my') or
                                    func_name.startswith('on_') or
                                    func_name.startswith('_')):
                                self.warnings.append(f"调用未知函数: {func_name}")

                # 检查属性访问
                elif isinstance(node.func, ast.Attribute):
                    attr_name = node.func.attr
                    if isinstance(node.func.value, ast.Name):
                        base_name = node.func.value.id
                        # 允许numpy的属性
                        if base_name in ('numpy', 'np'):
                            if attr_name not in {'array', 'zeros', 'ones', 'linspace', 'arange'}:
                                self.warnings.append(f"调用未知numpy方法: {attr_name}")

    def _check_imports(self, tree: ast.AST):
        """检查import语句"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name.split('.')[0]  # 只检查顶级模块
                    if name not in self.ALLOWED_BUILTINS:
                        self.errors.append(f"禁止导入模块: {name}")

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                if module:
                    top_module = module.split('.')[0]
                    if top_module not in self.ALLOWED_BUILTINS:
                        self.errors.append(f"禁止从模块导入: {module}")

    def _check_dangerous_ops(self, tree: ast.AST):
        """检查危险操作"""
        for node in ast.walk(tree):
            # 注意：ast.Exec 在 Python 3.13+ 已移除
            # exec语句已在FORBIDDEN_PATTERNS中通过正则检查
            # 这里只保留文件打开检查

            # 检查打开文件操作
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    # 检查文件模式
                    if node.args:
                        mode_arg = node.args[0]
                        if isinstance(mode_arg, (ast.Constant, ast.Str)):
                            mode = str(mode_arg.value if hasattr(mode_arg, 'value') else mode_arg.s)
                            if 'w' in mode or 'a' in mode:
                                self.errors.append("禁止使用写模式打开文件")

    def get_security_report(self) -> Dict:
        """获取安全报告"""
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'is_safe': len(self.errors) == 0,
            'timestamp': datetime.now().isoformat()
        }


class SafePathResolver:
    """安全路径解析器"""

    def __init__(self, base_path: str = None):
        """初始化路径解析器

        Args:
            base_path: 基础路径，默认为当前脚本目录
        """
        self.base_path = Path(base_path or os.path.dirname(os.path.abspath(__file__)))
        self._allowed_paths = [self.base_path]

    def resolve(self, path: Union[str, Path]) -> Path:
        """安全解析路径

        Args:
            path: 输入路径

        Returns:
            Path: 解析后的绝对路径

        Raises:
            SecurityError: 路径不安全时抛出
        """
        input_path = Path(path) if path else Path('.')

        # 转换为绝对路径
        if input_path.is_absolute():
            resolved = input_path.resolve()
        else:
            resolved = (self.base_path / input_path).resolve()

        # 防止路径遍历攻击
        if '..' in str(resolved):
            resolved = resolved.resolve()

        # 确保在允许的目录范围内
        if not self._is_path_allowed(resolved):
            raise SecurityError(
                f"路径不允许访问: {path}",
                {'resolved': str(resolved), 'base': str(self.base_path)}
            )

        return resolved

    def _is_path_allowed(self, path: Path) -> bool:
        """检查路径是否在允许范围内"""
        for base in self._allowed_paths:
            try:
                path.resolve().relative_to(base.resolve())
                return True
            except ValueError:
                continue
        return False

    def add_allowed_path(self, path: str):
        """添加允许访问的路径

        Args:
            path: 路径字符串
        """
        self._allowed_paths.append(Path(path).resolve())

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名

        Args:
            filename: 原始文件名

        Returns:
            str: 清理后的安全文件名
        """
        if not filename:
            return "unnamed"

        # 移除危险字符
        dangerous_chars = ['/', '\\', '..', ':', '*', '?', '"', '<', '>', '|', '\0']
        sanitized = filename
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')

        # 移除首尾空格和点
        sanitized = sanitized.strip().strip('.')

        # 限制长度
        max_length = 255
        if len(sanitized) > max_length:
            name, ext = os.path.splitext(sanitized[:max_length])
            sanitized = name + ext

        # 确保不为空
        if not sanitized or sanitized == '_':
            sanitized = "unnamed"

        return sanitized

    @staticmethod
    def sanitize_dirname(dirname: str) -> str:
        """清理目录名

        Args:
            dirname: 原始目录名

        Returns:
            str: 清理后的安全目录名
        """
        return SafePathResolver.sanitize_filename(dirname)


class SecureFileDownloader:
    """安全文件下载器"""

    # 允许的域名（白名单）
    ALLOWED_DOMAINS = {
        'github.com',
        'api.github.com',
        'raw.githubusercontent.com',
        'pypi.org',
        'files.pythonhosted.org',
    }

    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {'.exe', '.zip', '.whl', '.tar.gz', '.tgz', '.json', '.py'}

    # 最大文件大小（100MB）
    MAX_FILE_SIZE = 100 * 1024 * 1024

    # 默认超时时间（秒）
    DEFAULT_TIMEOUT = 60

    def __init__(self, timeout: int = None):
        """初始化下载器

        Args:
            timeout: 超时时间（秒）
        """
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.session = requests.Session()

    def download(self, url: str, expected_hash: str = None,
                 expected_size: int = None) -> Tuple[bool, str, bytes]:
        """下载并验证文件

        Args:
            url: 下载URL
            expected_hash: 期望的SHA256哈希值
            expected_size: 期望的文件大小

        Returns:
            Tuple[是否成功, 消息, 文件内容]
        """
        try:
            # 验证URL
            if not self._validate_url(url):
                return False, "URL验证失败: 不允许的域名或协议", None

            # 下载文件
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()

            # 检查内容长度
            content_length = int(response.headers.get('content-length', 0))
            if content_length > self.MAX_FILE_SIZE:
                return False, f"文件大小超过限制: {self.MAX_FILE_SIZE / 1024 / 1024:.0f}MB", None

            # 下载内容
            content = response.content

            # 验证大小
            if expected_size and len(content) != expected_size:
                return False, f"文件大小不匹配: 期望{expected_size}, 实际{len(content)}", None

            # 验证哈希
            if expected_hash:
                file_hash = hashlib.sha256(content).hexdigest()
                if file_hash != expected_hash:
                    return False, f"文件哈希验证失败", None

            return True, "下载成功", content

        except requests.exceptions.Timeout:
            return False, "下载超时", None
        except requests.exceptions.RequestException as e:
            return False, f"下载失败: {str(e)}", None
        except Exception as e:
            return False, f"下载异常: {str(e)}", None

    def _validate_url(self, url: str) -> bool:
        """验证URL安全性"""
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)

            # 只允许HTTPS
            if parsed.scheme != 'https':
                return False

            # 检查域名白名单
            if parsed.netloc not in self.ALLOWED_DOMAINS:
                # 允许本地地址
                if parsed.netloc not in ('localhost', '127.0.0.1'):
                    return False

            return True
        except Exception:
            return False

    def verify_python_file(self, content: bytes) -> Tuple[bool, List[str]]:
        """验证Python文件安全性

        Args:
            content: 文件内容

        Returns:
            Tuple[是否安全, 问题列表]
        """
        issues = []
        try:
            code = content.decode('utf-8')
        except UnicodeDecodeError:
            return False, ["文件编码不支持"]

        # 检查危险模式
        danger_patterns = [
            (r'__import__\s*\(', '包含__import__调用'),
            (r'\beval\s*\(', '包含eval调用'),
            (r'\bexec\s*\(', '包含exec调用'),
            (r'os\.system\s*\(', '包含系统命令执行'),
            (r'subprocess\.', '包含subprocess调用'),
            (r'\bopen\s*\([^)]*[wa]', '包含文件写入操作'),
            (r'socket\.', '包含socket操作'),
            (r'threading\.', '包含多线程'),
            (r'multiprocessing\.', '包含多进程'),
        ]

        for pattern, message in danger_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(message)

        return len(issues) == 0, issues


def validate_strategy_file(file_path: str, base_path: str = None) -> Tuple[bool, str]:
    """便捷函数：验证策略文件安全性

    Args:
        file_path: 策略文件路径
        base_path: 基础路径

    Returns:
        Tuple[是否通过, 消息]
    """
    resolver = SafePathResolver(base_path)

    try:
        safe_path = resolver.resolve(file_path)

        # 检查文件扩展名
        if not safe_path.suffix.lower() in ('.py', '.kh'):
            return False, f"不支持的文件类型: {safe_path.suffix}"

        validator = StrategySecurityValidator()
        is_safe, messages = validator.validate_file(str(safe_path))

        if is_safe:
            return True, f"策略验证通过: {safe_path.name}"
        else:
            error_msg = "策略安全验证失败:\n" + "\n".join(f"  - {msg}" for msg in messages)
            return False, error_msg

    except SecurityError as e:
        return False, f"路径安全检查失败: {e.message}"
    except Exception as e:
        return False, f"验证过程出错: {str(e)}"


# 便捷实例
default_validator = StrategySecurityValidator()
default_resolver = SafePathResolver()
default_downloader = SecureFileDownloader()
