# coding: utf-8
"""
Widget辅助工具类

提供PyQt5 Widget测试的辅助方法。
"""

from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QTextEdit, QComboBox, QTableWidget, QListWidget
from PyQt5.QtCore import Qt
from typing import Optional, List, Any


class WidgetHelpers:
    """Widget测试辅助类"""

    @staticmethod
    def find_widget_by_name(parent: QWidget, name: str, widget_type: type = QWidget) -> Optional[QWidget]:
        """
        按对象名称查找widget

        Args:
            parent: 父widget
            name: 对象名称
            widget_type: widget类型

        Returns:
            找到的widget，未找到返回None
        """
        return parent.findChild(widget_type, name)

    @staticmethod
    def find_widgets_by_type(parent: QWidget, widget_type: type) -> List[QWidget]:
        """
        按类型查找所有widget

        Args:
            parent: 父widget
            widget_type: widget类型

        Returns:
            widget列表
        """
        return parent.findChildren(widget_type)

    @staticmethod
    def click_button(qtbot, button: QPushButton):
        """
        点击按钮

        Args:
            qtbot: pytest-qt的qtbot fixture
            button: 要点击的按钮
        """
        qtbot.mouseClick(button, Qt.LeftButton)

    @staticmethod
    def set_line_edit_text(qtbot, line_edit: QLineEdit, text: str):
        """
        设置QLineEdit文本

        Args:
            qtbot: pytest-qt的qtbot fixture
            line_edit: QLineEdit控件
            text: 要设置的文本
        """
        line_edit.setText(text)
        qtbot.wait(100)  # 等待信号处理

    @staticmethod
    def get_line_edit_text(line_edit: QLineEdit) -> str:
        """
        获取QLineEdit文本

        Args:
            line_edit: QLineEdit控件

        Returns:
            文本内容
        """
        return line_edit.text()

    @staticmethod
    def set_combo_box_index(qtbot, combo_box: QComboBox, index: int):
        """
        设置QComboBox选中项

        Args:
            qtbot: pytest-qt的qtbot fixture
            combo_box: QComboBox控件
            index: 选中索引
        """
        combo_box.setCurrentIndex(index)
        qtbot.wait(100)  # 等待信号处理

    @staticmethod
    def get_combo_box_current_text(combo_box: QComboBox) -> str:
        """
        获取QComboBox当前文本

        Args:
            combo_box: QComboBox控件

        Returns:
            当前文本
        """
        return combo_box.currentText()

    @staticmethod
    def get_combo_box_current_data(combo_box: QComboBox) -> Any:
        """
        获取QComboBox当前数据

        Args:
            combo_box: QComboBox控件

        Returns:
            当前数据
        """
        return combo_box.currentData()

    @staticmethod
    def get_table_widget_data(table: QTableWidget, row: int, col: int) -> Any:
        """
        获取QTableWidget单元格数据

        Args:
            table: QTableWidget控件
            row: 行索引
            col: 列索引

        Returns:
            单元格数据
        """
        item = table.item(row, col)
        if item:
            return item.text()
        return None

    @staticmethod
    def get_table_widget_row_count(table: QTableWidget) -> int:
        """
        获取QTableWidget行数

        Args:
            table: QTableWidget控件

        Returns:
            行数
        """
        return table.rowCount()

    @staticmethod
    def get_table_widget_column_count(table: QTableWidget) -> int:
        """
        获取QTableWidget列数

        Args:
            table: QTableWidget控件

        Returns:
            列数
        """
        return table.columnCount()

    @staticmethod
    def get_list_widget_items(list_widget: QListWidget) -> List[str]:
        """
        获取QListWidget所有项

        Args:
            list_widget: QListWidget控件

        Returns:
            项文本列表
        """
        items = []
        for i in range(list_widget.count()):
            items.append(list_widget.item(i).text())
        return items

    @staticmethod
    def get_text_edit_content(text_edit: QTextEdit) -> str:
        """
        获取QTextEdit内容

        Args:
            text_edit: QTextEdit控件

        Returns:
            文本内容
        """
        return text_edit.toPlainText()

    @staticmethod
    def set_text_edit_content(qtbot, text_edit: QTextEdit, text: str):
        """
        设置QTextEdit内容

        Args:
            qtbot: pytest-qt的qtbot fixture
            text_edit: QTextEdit控件
            text: 要设置的文本
        """
        text_edit.setText(text)
        qtbot.wait(100)  # 等待信号处理

    @staticmethod
    def wait_visible(qtbot, widget: QWidget, timeout: int = 1000):
        """
        等待widget可见

        Args:
            qtbot: pytest-qt的qtbot fixture
            widget: 要等待的widget
            timeout: 超时时间（毫秒）
        """
        qtbot.wait_until(lambda: widget.isVisible(), timeout=timeout)

    @staticmethod
    def wait_enabled(qtbot, widget: QWidget, timeout: int = 1000):
        """
        等待widget可用

        Args:
            qtbot: pytest-qt的qtbot fixture
            widget: 要等待的widget
            timeout: 超时时间（毫秒）
        """
        qtbot.wait_until(lambda: widget.isEnabled(), timeout=timeout)

    @staticmethod
    def wait_text_changed(qtbot, widget: QLineEdit, expected_text: str, timeout: int = 1000):
        """
        等待QLineEdit文本变化

        Args:
            qtbot: pytest-qt的qtbot fixture
            widget: QLineEdit控件
            expected_text: 期望的文本
            timeout: 超时时间（毫秒）
        """
        qtbot.wait_until(lambda: widget.text() == expected_text, timeout=timeout)

    @staticmethod
    def assert_widget_visible(widget: QWidget, expected: bool = True):
        """
        断言widget可见性

        Args:
            widget: 要检查的widget
            expected: 是否期望可见
        """
        assert widget.isVisible() == expected, f"Widget可见性断言失败: {widget.isVisible()} != {expected}"

    @staticmethod
    def assert_widget_enabled(widget: QWidget, expected: bool = True):
        """
        断言widget可用性

        Args:
            widget: 要检查的widget
            expected: 是否期望可用
        """
        assert widget.isEnabled() == expected, f"Widget可用性断言失败: {widget.isEnabled()} != {expected}"

    @staticmethod
    def assert_text_equal(widget: QLineEdit, expected: str):
        """
        断言widget文本相等

        Args:
            widget: QLineEdit控件
            expected: 期望的文本
        """
        actual = widget.text()
        assert actual == expected, f"文本断言失败: '{actual}' != '{expected}'"

    @staticmethod
    def assert_combo_box_index(combo_box: QComboBox, expected: int):
        """
        断言QComboBox索引

        Args:
            combo_box: QComboBox控件
            expected: 期望的索引
        """
        actual = combo_box.currentIndex()
        assert actual == expected, f"ComboBox索引断言失败: {actual} != {expected}"

    @staticmethod
    def assert_table_row_count(table: QTableWidget, expected: int):
        """
        断言QTableWidget行数

        Args:
            table: QTableWidget控件
            expected: 期望的行数
        """
        actual = table.rowCount()
        assert actual == expected, f"Table行数断言失败: {actual} != {expected}"

    @staticmethod
    def assert_table_cell_text(table: QTableWidget, row: int, col: int, expected: str):
        """
        断言QTableWidget单元格文本

        Args:
            table: QTableWidget控件
            row: 行索引
            col: 列索引
            expected: 期望的文本
        """
        actual = WidgetHelpers.get_table_widget_data(table, row, col)
        assert actual == expected, f"Table单元格文本断言失败: '{actual}' != '{expected}'"
