# -*- coding: utf-8 -*-

TEXTX_EXTENSION = 'tx'

TEXTX_SYNTAX = \
{
  "comment": [
    "\/\/"
  ],
  "multiline_comment": {
    "open": "/*",
    "close": "*/"
  },
  "extension": [
    "tx"
  ],
  "string": [
    "'",
    "\""
  ],
  "operators": [
    "\|",
    "\*",
    "\+",
    "\?",
    "=",
    "\?=",
    "\+=",
    "\*="
  ],
  "keywords": [
    "import"
  ],
  "definition": [
  ],
  "regex": [
     ["^[a-zA-Z0-9_]*(?=(:))", "properObject", "bold"],
     ["[a-zA-Z0-9_]+[ ]?(?=(\+=|\*=|\?=|=))", "properObject", ],
     ["\/(.*)\/", "extras"]
  ],
  "extras": [
      "ID",
      "INT",
      "BOOL",
      "FLOAT",
      "STRING",
      "BASETYPE",
      "skipws",
      "noskipws",
      "ws",
      "eolterm"
  ]

}

