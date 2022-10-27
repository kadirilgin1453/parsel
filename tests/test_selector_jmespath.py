# -*- coding: utf-8 -*-

import unittest

from parsel import Selector


class JMESPathTestCase(unittest.TestCase):
    def test_json_has_html(self):
        """Sometimes the information is returned in a json wrapper"""
        data = """
        {
            "content": [
                {
                    "name": "A",
                    "value": "a"
                },
                {
                    "name": {
                        "age": 18
                    },
                    "value": "b"
                },
                {
                    "name": "C",
                    "value": "c"
                },
                {
                    "name": "<a>D</a>",
                    "value": "<div>d</div>"
                }
            ],
            "html": "<div><a>a<br>b</a>c</div><div><a>d</a>e<b>f</b></div>"
        }
        """
        sel = Selector(text=data)
        self.assertEqual(
            sel.jmespath("html").get(),
            "<div><a>a<br>b</a>c</div><div><a>d</a>e<b>f</b></div>",
        )
        self.assertEqual(
            sel.jmespath("html").xpath("//div/a/text()").getall(),
            ["a", "b", "d"],
        )
        self.assertEqual(
            sel.jmespath("html").css("div > b").getall(), ["<b>f</b>"]
        )
        self.assertEqual(
            sel.jmespath("content").jmespath("name.age").get(), 18
        )

    def test_html_has_json(self):
        html_text = """
        <div>
            <h1>Information</h1>
            <content>
            {
              "user": [
                        {
                                  "name": "A",
                                  "age": 18
                        },
                        {
                                  "name": "B",
                                  "age": 32
                        },
                        {
                                  "name": "C",
                                  "age": 22
                        },
                        {
                                  "name": "D",
                                  "age": 25
                        }
              ],
              "total": 4,
              "status": "ok"
            }
            </content>
        </div>
        """
        sel = Selector(text=html_text)
        self.assertEqual(
            sel.xpath("//div/content/text()")
            .jmespath("user[*].name")
            .getall(),
            ["A", "B", "C", "D"],
        )
        self.assertEqual(
            sel.xpath("//div/content").jmespath("user[*].name").getall(),
            ["A", "B", "C", "D"],
        )
        self.assertEqual(sel.xpath("//div/content").jmespath("total").get(), 4)

    def test_jmestpath_with_re(self):
        html_text = """
            <div>
                <h1>Information</h1>
                <content>
                {
                  "user": [
                            {
                                      "name": "A",
                                      "age": 18
                            },
                            {
                                      "name": "B",
                                      "age": 32
                            },
                            {
                                      "name": "C",
                                      "age": 22
                            },
                            {
                                      "name": "D",
                                      "age": 25
                            }
                  ],
                  "total": 4,
                  "status": "ok"
                }
                </content>
            </div>
            """
        sel = Selector(text=html_text)
        self.assertEqual(
            sel.xpath("//div/content/text()")
            .jmespath("user[*].name")
            .re(r"(\w+)"),
            ["A", "B", "C", "D"],
        )
        self.assertEqual(
            sel.xpath("//div/content").jmespath("user[*].name").re(r"(\w+)"),
            ["A", "B", "C", "D"],
        )

        with self.assertRaises(TypeError):
            sel.xpath("//div/content").jmespath("user[*].age").re(r"(\d+)")

        self.assertEqual(
            sel.xpath("//div/content").jmespath("unavailable").re(r"(\d+)"), []
        )

        self.assertEqual(
            sel.xpath("//div/content")
            .jmespath("unavailable")
            .re_first(r"(\d+)"),
            None,
        )

        self.assertEqual(
            sel.xpath("//div/content")
            .jmespath("user[*].age.to_string(@)")
            .re(r"(\d+)"),
            ["18", "32", "22", "25"],
        )
