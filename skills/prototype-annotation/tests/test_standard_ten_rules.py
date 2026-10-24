import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "check_annotation_assets.py"
SPEC = importlib.util.spec_from_file_location("check_annotation_assets", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

VALID_MD = """### 页面内容
一句概述。

### 交互说明
1) 点击查询。

### 业务规则
1) 规则一。

### 字段说明
本块不涉及字段

### 待确认
暂无
"""


def write_kit(root: Path, annotations: list[dict]) -> None:
    (root / "runtime.js").write_text("window.__vpa = true;", encoding="utf-8")
    (root / "runtime.css").write_text(".vpa{}", encoding="utf-8")
    (root / "annotation.bundle.json").write_text(
        json.dumps({
            "version": 1,
            "annotations": annotations,
            "coverage": {"total": 1, "mapped": 1, "unmapped": 0},
        }),
        encoding="utf-8",
    )


def base_annotation(**overrides):
    item = {
        "id": "1",
        "page": "/records",
        "screenState": "host",
        "target": {"selector": "[data-anno='record-list']"},
        "markdown": VALID_MD,
        "sourceRefs": ["REQ-1"],
    }
    item.update(overrides)
    return item


class TenRulesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.src = self.root / "src"
        self.src.mkdir()
        (self.src / "App.tsx").write_text('<Route path="/records" />', encoding="utf-8")
        (self.src / "page.tsx").write_text("data-anno='record-list'", encoding="utf-8")
        self.config = self.root / "annotation.config.json"
        self.config.write_text(json.dumps({
            "sourceRequirements": [{"id": "REQ-1", "source": "prd.md"}],
            "annotations": [],
        }), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def check_raises(self, annotation, prd_pages=None, **kwargs):
        write_kit(self.root, [annotation])
        with self.assertRaises(ValueError) as ctx:
            MODULE.check_assets(
                self.root,
                src=self.src,
                routes_file=self.src / "App.tsx",
                config_path=self.config,
                prd_pages=prd_pages if prd_pages is not None else ["/records"],
                **kwargs,
            )
        return str(ctx.exception)

    def test_rule1_missing_anchor(self):
        (self.src / "page.tsx").write_text("// no anchor", encoding="utf-8")
        msg = self.check_raises(base_annotation())
        self.assertIn("[判据1]", msg)

    def test_rule2_bad_route(self):
        (self.src / "page.tsx").write_text("data-anno='record-list'", encoding="utf-8")
        msg = self.check_raises(base_annotation(page="/missing"))
        self.assertIn("[判据2]", msg)

    def test_rule3_duplicate_id(self):
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        write_kit(self.root, [base_annotation(), base_annotation()])
        with self.assertRaises(ValueError) as ctx:
            MODULE.check_assets(self.root)
        self.assertIn("[判据3]", str(ctx.exception))

    def _routes_with_catchall(self, extra_routes: str = "") -> None:
        (self.src / "App.tsx").write_text(
            f'<Route path="/records" />\n<Route path="/engage/create" />\n'
            f'<Route path="/engage/edit/:id" />\n{extra_routes}<Route path="*" />',
            encoding="utf-8",
        )

    def test_rule2_catchall_does_not_validate_fake_page(self):
        self._routes_with_catchall()
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        msg = self.check_raises(base_annotation(page="/zzz/nope"))
        self.assertIn("[判据2]", msg)
        self.assertIn("不在真实路由表", msg)

    def test_rule2_bogus_route_matcher(self):
        self._routes_with_catchall()
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        msg = self.check_raises(base_annotation(routeMatcher="does-not-exist"))
        self.assertIn("[判据2]", msg)
        self.assertIn("未命中任何真实路由", msg)

    def test_rule2_narrow_route_matcher(self):
        self._routes_with_catchall()
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        msg = self.check_raises(
            base_annotation(
                page="/engage/edit/1",
                routeMatcher="engage/create",
            )
        )
        self.assertIn("[判据2]", msg)
        self.assertIn("未覆盖本块 page", msg)

    def test_rule8_four_empty_one_substantive(self):
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        shell = """### 页面内容\n暂无\n### 交互说明\n暂无\n### 业务规则\n暂无\n### 字段说明\n本块不涉及字段\n### 待确认\n暂无\n"""
        msg = self.check_raises(base_annotation(markdown=shell))
        self.assertIn("[判据8]", msg)

    def test_rule8_three_empty_two_substantive(self):
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        md = """### 页面内容\n一句概述。\n### 交互说明\n暂无\n### 业务规则\n暂无\n### 字段说明\n本块不涉及字段\n### 待确认\n暂无\n"""
        write_kit(self.root, [base_annotation(markdown=md)])
        MODULE.check_assets(
            self.root,
            src=self.src,
            routes_file=self.src / "App.tsx",
            config_path=self.config,
            prd_pages=["/records"],
        )

    def test_grouped_errors_all_criteria(self):
        self._routes_with_catchall()
        (self.src / "page.tsx").write_text("// no anchor", encoding="utf-8")
        bad = VALID_MD.replace("本块不涉及字段", "见 §3.2 字段清单")
        bad = "> 来源：prd.md\n" + bad
        write_kit(
            self.root,
            [base_annotation(page="/zzz/nope", markdown=bad)],
        )
        with self.assertRaises(ValueError) as ctx:
            MODULE.check_assets(
                self.root,
                src=self.src,
                routes_file=self.src / "App.tsx",
                config_path=self.config,
                prd_pages=["/zzz/nope"],
            )
        msg = str(ctx.exception)
        for rule in ("1", "2", "6", "7"):
            self.assertIn(f"【判据{rule}】", msg)
        self.assertNotIn("【判据10】", msg)

    def test_rule4_non_continuous(self):
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        msg = self.check_raises(base_annotation(id="2"))
        self.assertIn("[判据4]", msg)

    def test_rule5_tab_parse_zero(self):
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        bad = VALID_MD.replace("1) 点击查询。", "点击查询但没有列表符。")
        msg = self.check_raises(base_annotation(markdown=bad))
        self.assertIn("[判据5]", msg)

    def test_rule6_field_pointer(self):
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        bad = VALID_MD.replace("本块不涉及字段", "见 §3.2 字段清单")
        msg = self.check_raises(base_annotation(markdown=bad))
        self.assertIn("[判据6]", msg)

    def test_rule6_empty_field_tab(self):
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        bad = VALID_MD.replace("本块不涉及字段", "暂无")
        msg = self.check_raises(base_annotation(markdown=bad))
        self.assertIn("[判据6]", msg)
        self.assertIn("为空或仅「暂无」", msg)

    def test_rule7_display_source(self):
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        bad = "> 来源：prd.md\n" + VALID_MD
        msg = self.check_raises(base_annotation(markdown=bad))
        self.assertIn("[判据7]", msg)

    def test_rule8_empty_shell(self):
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        shell = """### 页面内容\n暂无\n### 交互说明\n暂无\n### 业务规则\n暂无\n### 字段说明\n暂无\n### 待确认\n暂无\n"""
        msg = self.check_raises(base_annotation(markdown=shell))
        self.assertIn("[判据8]", msg)

    def test_rule9_empty_refs(self):
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        msg = self.check_raises(base_annotation(sourceRefs=[]))
        self.assertIn("[判据9]", msg)

    def test_rule10_foreign_page(self):
        (self.src / "page.tsx").write_text('[data-anno="record-list"]', encoding="utf-8")
        msg = self.check_raises(base_annotation(), prd_pages=["/other"])  # noqa: duplicate kw ok
        self.assertIn("[判据10]", msg)

    def test_rule11_overlay_on_host(self):
        msg = self.check_raises(
            base_annotation(scopeLabel="弹窗：新建行为"),
            prd_pages=["/records"],
        )
        self.assertIn("[判据11]", msg)
        self.assertIn("弹窗：新建行为", msg)
        self.assertIn("modal-", msg)

    def test_rule11_overlay_with_modal_state_passes(self):
        write_kit(
            self.root,
            [base_annotation(scopeLabel="弹窗：新建行为", screenState="modal-xxx")],
        )
        MODULE.check_assets(self.root)


if __name__ == "__main__":
    unittest.main()
