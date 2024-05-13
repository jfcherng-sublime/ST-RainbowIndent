# ST-RainbowIndent

[![Required ST Build](https://img.shields.io/badge/ST-4169+-orange.svg?style=flat-square&logo=sublime-text)](https://www.sublimetext.com)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/jfcherng-sublime/ST-RainbowIndent/python.yml?branch=st4&style=flat-square)](https://github.com/jfcherng-sublime/ST-RainbowIndent/actions)
[![Package Control](https://img.shields.io/packagecontrol/dt/RainbowIndent?style=flat-square)](https://packagecontrol.io/packages/RainbowIndent)
[![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/jfcherng-sublime/ST-RainbowIndent?style=flat-square&logo=github)](https://github.com/jfcherng-sublime/ST-RainbowIndent/tags)
[![Project license](https://img.shields.io/github/license/jfcherng-sublime/ST-RainbowIndent?style=flat-square&logo=github)](https://github.com/jfcherng-sublime/ST-RainbowIndent/blob/st4/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/jfcherng-sublime/ST-RainbowIndent?style=flat-square&logo=github)](https://github.com/jfcherng-sublime/ST-RainbowIndent/stargazers)
[![Donate to this project using Paypal](https://img.shields.io/badge/paypal-donate-blue.svg?style=flat-square&logo=paypal)](https://www.paypal.me/jfcherng/5usd)

![screenshot](https://raw.githubusercontent.com/jfcherng-sublime/ST-RainbowIndent/docs/images/screenshot.png)

Makes indentation easier to read.

This is a simple conceptual clone of the [Indent Rainbow][vscode-indent-rainbow] VSCode extension.

## Installation

This package is available on [Package Control][package-control] by the name of [RainbowIndent][st-rainbow-indent].

## Example Color Scheme Rules

You may add following rules into your color scheme.

```js
///////////////////
// RainbowIndent //
///////////////////
{
    // red
    "foreground": "rgba(229, 57, 53, 0.35)",
    "background": "rgba(229, 57, 53, 0.2)",
    "scope": "region.indent.0",
},
{
    // green
    "foreground": "rgba(67, 160, 71, 0.35)",
    "background": "rgba(67, 160, 71, 0.2)",
    "scope": "region.indent.1",
},
{
    // blue
    "foreground": "rgba(30, 136, 229, 0.35)",
    "background": "rgba(30, 136, 229, 0.2)",
    "scope": "region.indent.2",
},
{
    // orange
    "foreground": "rgba(251, 140, 0, 0.35)",
    "background": "rgba(251, 140, 0, 0.2)",
    "scope": "region.indent.3",
},
{
    // purple
    "foreground": "rgba(142, 36, 170, 0.35)",
    "background": "rgba(142, 36, 170, 0.2)",
    "scope": "region.indent.4",
},
{
    // cyan
    "foreground": "rgba(0, 172, 193, 0.35)",
    "background": "rgba(0, 172, 193, 0.2)",
    "scope": "region.indent.5",
},
```

And then use the following plugin setting.

```js
"level_colors": [
    "region.indent.0",
    "region.indent.1",
    "region.indent.2",
    "region.indent.3",
    "region.indent.4",
    "region.indent.5",
],
```

## Known Issues

- There is no way to draw a region, where there is nothing, via ST's plugin APIs.
- Sometimes, ST seems to draw regions wrongly. Not sure how to stably reproduce this.

[package-control]: https://packagecontrol.io
[st-rainbow-indent]: https://packagecontrol.io/packages/RainbowIndent
[vscode-indent-rainbow]: https://marketplace.visualstudio.com/items?itemName=oderwat.indent-rainbow
